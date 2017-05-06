# -*- coding: utf-8 -*-
"""Caster object for either real or virtual Monotype composition caster"""
# Standard library imports
import io
import os
import select
import time
from collections import OrderedDict

# Driver library imports
# RPi.GPIO I/O control library (PyPI: RPi.GPIO, Debian: python3-rpi.gpio)
try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    GPIO = None
# Parallel port controller (PyPI: pyparallel, Debian: python3-parallel)
try:
    from parallel import Parallel
except (ImportError, RuntimeError):
    Parallel = None
# SMBus i2c controller (PyPI: smbus-cffi, Debian: python3-smbus)
try:
    from smbus import SMBus
except (ImportError, RuntimeError):
    SMBus = None
# WiringPi i/o controller (PyPI: wiringpi)
try:
    import wiringpi
except (ImportError, RuntimeError):
    wiringpi = None

# Intra-package imports
from .casting_models import Record
from .config import CFG
from .definitions import ROW16_ADDRESSING, SIGNALS
from .matrix_controller import MatrixEngine
from .misc import singleton, weakref_singleton
from .ui import UI, option, Abort

# Interface config
INTERFACE_CFG = CFG.interface
# Constants for readability
AIR_ON = True
AIR_OFF = False
# Output latch registers for SMBus MCP23017 control
OLATA, OLATB = 0x14, 0x15
# Port direction registers for SMBus MCP23017 control
IODIRA, IODIRB = 0x00, 0x10
# Sensor and output drivercollection
SENSORS, OUTPUTS = {}, {}


class MonotypeCaster(object):
    """Methods common for Caster classes, used for instantiating
    caster driver objects (whether real hardware or mockup for simulation)."""
    pump_working, simulation, punching = False, False, False
    sensor, output = None, None
    # caster modes
    row_16_mode = ROW16_ADDRESSING.off

    def __init__(self, simulation=False, punching=False,
                 hw_sensor=INTERFACE_CFG.sensor,
                 hw_output=INTERFACE_CFG.output):
        """Lock the resource so that only one object can use it
        with context manager"""
        def choose_driver():
            """Get drivers for sensor and output"""
            if self.simulation:
                return SimulationSensor, SimulationOutput
            sensor, output = SENSORS.get(hw_sensor), OUTPUTS.get(hw_output)
            if 'paralell' in (sensor, output):
                # special case; parallel sensor/output must work together
                return ParallelSensor, ParallelOutput
            if not sensor or not output:
                # ask once again if it's not simulation mode
                UI.confirm(sim2, abort=False)
                self.simulation = True
                return SimulationSensor, SimulationOutput
            return sensor, output

        self.simulation, self.punching = simulation, punching
        UI.pause('Initializing caster...', min_verbosity=3, allow_abort=True)
        sim = 'Simulate casting instead of real casting?'
        sim2 = 'Cannot initialize a hardware interface. Simulate instead?'
        self.simulation = (self.simulation or INTERFACE_CFG.simulation or
                           INTERFACE_CFG.choose_backend and UI.confirm(sim))
        sensor, output = choose_driver()
        self.sensor, self.output = sensor(), output()

    def __enter__(self):
        self.sensor.__enter__()
        self.output.__enter__()
        return self

    def __exit__(self, *_):
        self.output.__exit__()
        self.sensor.__exit__()

    @property
    def parameters(self):
        """Gets a list of parameters"""
        # Collect data from I/O drivers
        parameters = OrderedDict({'': 'Caster parameters'})
        parameters.update(**self.sensor.parameters)
        parameters.update(**self.output.parameters)
        return parameters

    def check_row_16(self, is_required=False):
        """Choose the diecase row 16 addressing mode, if needed.

        Row 16 is needed and currently off:
        Ask which row 16 addressing system the user's machine has, if any.

        Row 16 is not needed and currently on:
        Tell the user to turn off the attachment.

        Row 16 is not needed and is off, or is needed and is on: do nothing.
        """
        is_active = self.row_16_mode is not ROW16_ADDRESSING.off

        # check and notify the user
        if is_required and not is_active:
            self.choose_row16_addressing()
        elif is_active and not is_required:
            UI.pause('\n\nTurn off the {} attachment.\n\n'
                     .format(self.row_16_mode))
            self.row_16_mode = ROW16_ADDRESSING.off
        elif is_required and is_active:
            UI.display('The {} attachment is turned on - OK.'
                       .format(self.row_16_mode))

    def choose_row16_addressing(self):
        """Let user decide which way to address row 16"""
        prompt = ('Your ribbon contains codes from the 16th row.\n'
                  'It is supported by special attachments for the machine.\n'
                  'Which mode does your caster use: HMN, KMN, Unit-Shift?\n\n'
                  'If off - characters from row 15 will be cast instead.')
        options = [option(key='h', value=ROW16_ADDRESSING.hmn,
                          seq=1, text=ROW16_ADDRESSING.hmn),
                   option(key='k', value=ROW16_ADDRESSING.kmn,
                          seq=2, text=ROW16_ADDRESSING.kmn),
                   option(key='u', value=ROW16_ADDRESSING.unitshift,
                          seq=3, text=ROW16_ADDRESSING.unitshift),
                   option(key='o', value=ROW16_ADDRESSING.off, seq=4,
                          text='Off - cast from row 15 instead')]
        mode = UI.simple_menu(prompt, options,
                              default_key='o', allow_abort=True)
        self.row_16_mode = mode

    def update_pump_state(self, record):
        """Read the record data and check if the pump is working"""
        state = (False if record.code.is_pump_stop
                 else self.pump_working or record.code.is_pump_start)
        self.pump_working = state

    def pump_off(self):
        """Ensure that the pump is turned off"""
        UI.display('EMERGENCY STOP: Cleaning up and switching the pump off...')
        UI.display('If the machine is stopped, turn it by hand once or twice.')
        record = Record('NJS0005')
        while self.pump_working:
            self.cast_one(record, timeout=60)
            self.cast_one(record, timeout=60)
            self.pump_working = False

    def cast_one(self, record, timeout=None):
        """Casting sequence: sensor on - valves on - sensor off - valves off"""
        try:
            self.update_pump_state(record)
            self.output.valves_off()
            self.sensor.wait_for(AIR_ON, timeout=timeout)
            self.output.valves_on(record.adjusted_signals)
            self.sensor.wait_for(AIR_OFF, timeout=timeout)
            self.output.valves_off()
        except (KeyboardInterrupt, EOFError, MachineStopped):
            self.pump_off()
            raise MachineStopped

    def cast_many(self, sequence, ask=True, repetitions=1):
        """Cast a series of multiple records."""
        stop_prompt = 'Machine stopped: continue casting?'
        # do we need to cast from row 16 and choose an attachment?
        needed = any((record.code.uses_row_16 for record in sequence))
        self.check_row_16(needed)
        # use caster context to check machine rotation and ensure
        # that no valves stay open after we're done
        with self:
            # cast as many as initially ordered and ask to continue
            while repetitions > 0:
                try:
                    for record in sequence:
                        self.cast_one(record)
                    # ensure that the pump is not working
                    self.pump_off()
                    # repetition successful
                    repetitions -= 1
                except MachineStopped:
                    # repetition failed
                    UI.confirm(stop_prompt, abort_answer=False)
                if ask and not repetitions and UI.confirm('Repeat?'):
                    repetitions += 1

    def punch(self, signals_sequence):
        """Punching sequence: valves on - wait - valves off- wait"""
        def manual(signals):
            """Advance between combinations is controlled by keypress"""
            self.output.valves_off()
            self.output.valves_on(signals)
            UI.pause('Next combination?', allow_abort=True)

        def by_timer(signals):
            """Advance is dictated by timer"""
            self.output.valves_off()
            self.output.valves_on(signals)
            time.sleep(0.25)
            self.output.valves_off()
            time.sleep(0.4)

        info = '{r.adjusted_signals_string:<20}{r.comment}'
        punch_one = manual if UI.confirm('Manual advance?') else by_timer
        # we only need output for this action
        with self.output:
            for item in signals_sequence:
                record = Record(item, signal_o15=True, default_o15=True)
                UI.display(info.format(r=record))
                punch_one(record.adjusted_signals)

    def test(self, signals_sequence, duration=None):
        """Testing: advance manually"""
        # we only need output for this action
        with self.output:
            while True:
                for item in signals_sequence:
                    record = Record(item, signal_o15=True)
                    UI.display(record.signals_string)
                    self.output.valves_off()
                    self.output.valves_on(record.signals)
                    if duration:
                        time.sleep(duration)
                    else:
                        UI.pause('Next?', allow_abort=True)
                UI.confirm('Repeat?', abort_answer=False)

    def diagnostics(self):
        """Settings and alignment menu for servicing the caster"""
        def test_front_pinblock(*_):
            """Sends signals 1...14, one by one"""
            info = 'Testing the front pinblock - signals 1...14.'
            UI.pause(info, allow_abort=True)
            self.test([str(n) for n in range(1, 15)])

        def test_rear_pinblock(*_):
            """Sends NI, NL, A...N"""
            info = 'This will test the rear pinblock - NI, NL, A...N. '
            UI.pause(info, allow_abort=True)
            self.test(['NI', 'NL', *'ABCDEFGHIJKLMN'])

        def test_all(*_):
            """Tests all valves and composition caster's inputs in original
            Monotype order:
            NMLKJIHGFSED 0075 CBA 123456789 10 11 12 13 14 0005.
            """
            info = ('This will test all the air lines in the same order '
                    'as the holes on the paper tower: \n{}\n'
                    'MAKE SURE THE PUMP IS DISENGAGED.')
            UI.pause(info.format(' '.join(SIGNALS)), allow_abort=True)
            self.test(SIGNALS)

        def test_justification(*_):
            """Tests the 0075-S-0005"""
            info = 'This will test the justification pinblock: 0075, S, 0005.'
            UI.pause(info, allow_abort=True)
            self.test(['0075', 'S', '0005'])

        def test_any_code(*_):
            """Tests a user-specified combination of signals"""
            with self.output:
                while True:
                    UI.display('Enter the signals to send to the caster, '
                               'or leave empty to return to menu: ')
                    string = UI.enter('Signals?', default=Abort)
                    record = Record(string, signal_o15=True)
                    self.output.valves_off()
                    UI.display('Sending {}'.format(record.signals_string))
                    self.output.valves_on(record.signals)

        def blow_all(*_):
            """Blow all signals for a short time; add NI, NL also"""
            info = 'Blowing air through all air pins on both pinblocks...'
            UI.pause(info, allow_abort=True)
            queue = ['NI', 'NL', 'A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7',
                     'H8', 'I9', 'J10', 'K11', 'L12', 'M13', 'N14',
                     '0075 S', '0005 O15']
            self.test(queue, duration=0.3)

        def calibrate_draw_rods(*_):
            """Keeps the diecase at G8 so that the operator can adjust
            the diecase draw rods until the diecase stops moving sideways
            when the centering pin is descending."""
            UI.display('Draw rods calibration:\n'
                       'The diecase will be moved to the central position '
                       '(G8).\n Turn on the machine and adjust the diecase '
                       'draw rods until the diecase stops wobbling.\n')
            if not UI.confirm('Proceed?', default=True, abort_answer=False):
                return
            with self.output:
                self.output.valves_on(['G', '8'])
                UI.pause('Sending G8, waiting for you to stop...')
                self.output.valves_off()

        def calibrate_wedges(*_):
            """Allows to calibrate the justification wedges so that when you're
            casting a 9-unit character with the S-needle at 0075:3 and 0005:8
            (neutral position), the    width is the same.

            It works like this:
            1. 0075 - turn the pump on,
            2. cast 7 spaces from the specified matrix (default: G5),
            3. put the line to the galley & set 0005 to 8, 0075 to 3, pump on,
            4. cast 7 spaces with the S-needle from the same matrix,
            5. put the line to the galley, then 0005 to turn the pump off.
            """
            UI.display('Transfer wedge calibration:\n\n'
                       'This function will cast two lines of 5 spaces: '
                       'first: G5, second: GS5 with wedges at 3/8. \n'
                       'Adjust the 52D space transfer wedge '
                       'until the lengths are the same.\n')
            UI.confirm('Proceed?', default=True, abort_answer=False)
            # prepare casting sequence
            record, justified_record = Record('G7'), Record('GS7')
            pump_start, pump_stop = Record('NKS 0075 3'), Record('NJS 0005 8')
            line_out = Record('NKJS 0005 0075 8')
            # start - 7 x G5 - line out - start - 7 x GS5 - line out - stop
            sequence = [pump_start, *[record] * 7, line_out, pump_start,
                        *[justified_record] * 7, line_out, pump_stop]
            self.cast_many(sequence)

        def calibrate_mould_and_diecase(*_):
            """Casts the "en dash" characters for calibrating the character X-Y
            relative to type body."""
            def get_codes(mat):
                """Gets two mats for a given char and adjusts its parameters"""
                positions = mat_engine.get_wedge_positions(mat)
                pos_0075, pos_0005 = positions.pos_0075, positions.pos_0005
                # use single justification to adjust character width
                use_s_needle = (pos_0075, pos_0005) != (3, 8)
                ribbon_record = mat.get_ribbon_record(s_needle=use_s_needle)
                char_record = Record(ribbon_record)
                return [Record('NJS 0005 {}'.format(pos_0005)),
                        Record('NKS 0075 {}'.format(pos_0075)),
                        char_record, char_record]

            UI.display('Mould blade opening and X-Y character calibration:\n'
                       'Cast G5, adjust the sort width to the value shown.\n'
                       '\nThen cast some lowercase "n" letters and n-dashes,\n'
                       'check the position of the character relative to the\n'
                       'type body and adjust the bridge X-Y.\n'
                       'Repeat if needed.\n')
            UI.confirm('Proceed?', default=True, abort_answer=False)

            # this method needs to know the diecase and wedge
            mat_engine = MatrixEngine()
            wedge = mat_engine.choose_wedge()
            # use half-quad, quad, "n" and en-dash
            mats = [mat_engine.find_space(units=9),
                    mat_engine.find_space(units=18),
                    mat_engine.find_matrix(char='n'),
                    mat_engine.find_matrix(char='--')]
            # operator needs to know how wide (in inches) the sorts should be
            template = '{u} units (1{n}) is {i}" wide'
            quad_width = self.wedge.set_width / 12 * wedge.pica
            UI.display(template.format(u=9, n='en', i=0.5 * quad_width))
            UI.display(template.format(u=18, n='em', i=quad_width))
            # build a casting queue and cast it repeatedly
            line_out, pump_stop = Record('NKJS 0005 0075'), Record('NJS 0005')
            codes = (get_codes(mat) for mat in mats)
            sequence = [*codes, line_out, pump_stop]
            self.cast_many(sequence)

        def test_row_16(*_):
            """Tests the row 16 addressing attachment (HMN, KMN, unit-shift).
            Casts from all matrices in 16th row.
            """
            UI.display('This will test the 16th row addressing.\n'
                       'If your caster has HMN, KMN or unit-shift attachment, '
                       'turn it on.\n')
            # build casting queue
            pump_start, pump_stop = Record('NKS 0075'), Record('NJS 0005')
            line_out = Record('NKJS 0005 0075')
            row = [Record('{}16'.format(col))
                   for col in ('NI', 'NL', *'ABCDEFGHIJKLMNO')]
            # test with actual casting or not?
            if UI.confirm('Use the pump? Y = cast the row, N = test codes.'):
                sequence = [pump_start, *row, line_out, pump_stop]
                self.cast_many(sequence)
            else:
                self.test(row)

        options = [option(key='a', value=test_all, seq=1,
                          text='Test outputs',
                          desc='Test all the air outputs N...O15, one by one'),
                   option(key='f', value=test_front_pinblock, seq=2,
                          cond=not self.punching,
                          text='Test the front pin block',
                          desc='Test the pins 1...14'),
                   option(key='r', value=test_rear_pinblock, seq=2,
                          cond=not self.punching,
                          text='Test the rear pin block',
                          desc='Test the pins NI, NL, A...N, one by one'),
                   option(key='b', value=blow_all, seq=2,
                          text='Blow all air pins',
                          desc='Blow air into every pin for a short time'),
                   option(key='j', value=test_justification, seq=2,
                          cond=not self.punching,
                          text='Test the justification block',
                          desc='Test the pins for 0075, S and 0005'),
                   option(key='c', value=test_any_code, seq=1,
                          text='Send specified signal combination',
                          desc='Send the specified signals to the machine'),
                   option(key='w', value=calibrate_wedges, seq=4,
                          cond=not self.punching,
                          text='Calibrate the 52D wedge',
                          desc=('Calibrate the space transfer wedge '
                                'for correct width')),
                   option(key='d', value=calibrate_mould_and_diecase, seq=4,
                          cond=not self.punching,
                          text='Calibrate mould blade and diecase',
                          desc=('Set the type body width and '
                                'character-to-body position')),
                   option(key='m', value=calibrate_draw_rods, seq=3,
                          cond=not self.punching,
                          text='Calibrate matrix case draw rods',
                          desc=('Keep the matrix case at G8 '
                                'and adjust the draw rods')),
                   option(key='l', value=test_row_16, seq=5,
                          cond=not self.punching,
                          text='Test large 16x17 diecase attachment',
                          desc=('Cast type from row 16 '
                                'with HMN, KMN or unit-shift'))]

        header = 'Diagnostics and machine calibration menu:'
        catch_exceptions = (Abort, KeyboardInterrupt, EOFError, MachineStopped)
        # Keep displaying the menu and go back here after any method ends
        UI.dynamic_menu(options=options, header=header, func_args=(self,),
                        catch_exceptions=catch_exceptions)


class SensorBase(object):
    """Mockup for a machine cycle sensor"""
    name = 'generic machine cycle sensor'
    gpio = INTERFACE_CFG.sensor_gpio
    last_state, manual_mode, signals = True, True, None
    timeout, time_on, time_off = 30, 0.1, 0.1

    def __enter__(self):
        UI.pause('Using a {} for machine feedback'.format(self.name),
                 min_verbosity=3)
        self.check_if_machine_is_working()
        return self

    def __exit__(self, *_):
        UI.pause('The {} is no longer in use'.format(self.name),
                 min_verbosity=3)
        self.manual_mode = True

    @property
    def parameters(self):
        """Gets a list of parameters"""
        parameters = OrderedDict()
        parameters['Sensor driver'] = self.name
        parameters['Manual mode'] = self.manual_mode
        return parameters

    def check_if_machine_is_working(self):
        """Detect machine cycles and alert if it's not working"""
        UI.display('Turn on the air, motor, pump (if put out) and machine.')
        UI.display('Checking if the machine is running...')
        cycles = 3
        while True:
            try:
                self.wait_for(AIR_ON, timeout=30)
                while cycles:
                    # Run a new cycle
                    UI.display(cycles)
                    self.wait_for(AIR_ON, timeout=30)
                    cycles -= 1
                return

            except (MachineStopped, KeyboardInterrupt, EOFError):
                prompt = 'Machine is not running. Y to try again or N to exit?'
                UI.confirm(prompt, default=True, abort_answer=False)

    def wait_for(self, new_state, timeout=None):
        """Waits for a keypress to emulate machine cycle, unless user
        switches to auto mode, where all combinations are processed in batch"""
        def switch_to_auto():
            """Switch to automatic mode"""
            self.manual_mode = False

        # do nothing
        timeout = timeout
        prompt = 'The sensor is going {}'
        UI.display(prompt.format('ON' if new_state else 'OFF'),
                   min_verbosity=3)

        if new_state and self.manual_mode:
            # Ask whether to cast or simulate machine stop
            options = [option(key='a', text='Switch to automatic mode',
                              value=switch_to_auto, seq=1),
                       option(key='s', text='Stop',
                              value=MachineStopped, seq=2),
                       option(key='enter', text='Continue',
                              value=lambda: 0, seq=3)]

            UI.simple_menu('Simulation mode: decide what to do.',
                           options, default_key='enter')()
        elif new_state:
            time.sleep(self.time_off)
        else:
            time.sleep(self.time_on)


class SimulationSensor(SensorBase):
    """Simulate casting with no actual machine"""
    name = 'simulation - mockup casting interface'

    def check_if_machine_is_working(self):
        """Warn that this is just a simulation"""
        UI.display('Simulation mode - no machine is used.\n'
                   'This will emulate the actual casting sequence '
                   'as closely as possible.\n')
        return super().check_if_machine_is_working()


class OutputBase(object):
    """Mockup for a driver for 32 pneumatic outputs"""
    signals_arrangement = INTERFACE_CFG.signals_arrangement
    mcp0_address = INTERFACE_CFG.mcp0
    mcp1_address = INTERFACE_CFG.mcp1
    i2c_bus_number = INTERFACE_CFG.i2c_bus
    signal_numbers = [*range(1, 33)]
    working, port, _mapping = False, None, None
    name = 'generic output driver'

    def __enter__(self):
        UI.pause('Using the {} for sending signals...'.format(self.name),
                 min_verbosity=2)
        return self

    def __exit__(self, *_):
        self.valves_off()

    @property
    def mapping(self):
        """Signal-to-number mapping (memoize for multiple use)"""
        assoc = self._mapping
        if not assoc:
            assoc = dict(zip(INTERFACE_CFG.signals_arrangement,
                             self.signal_numbers))
            self._mapping = assoc
        return assoc

    @property
    def parameters(self):
        """Gets a list of parameters"""
        parameters = OrderedDict()
        parameters['Output driver'] = self.name
        parameters['Signals arrangement'] = ' '.join(self.signals_arrangement)
        return parameters

    @staticmethod
    def valves_on(signals):
        """Turns on multiple valves"""
        for sig in signals:
            UI.display(sig + ' on', min_verbosity=2)

    @staticmethod
    def valves_off():
        """Turns off all the valves"""
        UI.display('All valves off', min_verbosity=2)


class SimulationOutput(OutputBase):
    """Simulation output driver - don't control any hardware"""
    name = 'simulation - mockup casting interface'


# HARDWARE DRIVERS
class SysfsSensor(SensorBase):
    """Optical cycle sensor using kernel sysfs interface"""
    name = 'Kernel SysFS interface for photocell sensor GPIO'
    bounce_time = INTERFACE_CFG.bounce_time * 0.001
    timeout = 5

    def __init__(self, gpio=None):
        self.value_file = self._configure_sysfs_interface(gpio)

    @property
    def parameters(self):
        """Gets a list of parameters"""
        parameters = OrderedDict()
        parameters['Sensor driver'] = self.name
        parameters['GPIO number'] = self.gpio
        parameters['Value file path'] = self.value_file
        return parameters

    def wait_for(self, new_state, timeout=None):
        """
        Waits until the sensor is in the desired state.
        new_state = True or False.
        timeout means that if no signals in given time, raise MachineStopped.
        force_cycle means that if last_state == new_state, a full cycle must
        pass before exit.
        Uses software debouncing set at 5ms
        """
        def get_state():
            """Reads current input state"""
            gpiostate.seek(0)
            # File can contain "1\n" or "0\n"; convert it to boolean
            return bool(int(gpiostate.read().strip()))

        _timeout = timeout or self.timeout
        # Set debounce time to now
        debounce = time.time()
        # Prevent sudden exit if the current state is the desired state
        with io.open(self.value_file, 'r') as gpiostate:
            if get_state() == new_state:
                self.last_state = not new_state
        with io.open(self.value_file, 'r') as gpiostate:
            while True:
                try:
                    signals = select.epoll()
                    signals.register(gpiostate, select.POLLPRI)
                    while self.last_state != new_state:
                        # Keep polling or raise MachineStopped on timeout
                        if signals.poll(_timeout):
                            state = get_state()
                            # Input bounce time is given in milliseconds
                            if time.time() - debounce > self.bounce_time:
                                self.last_state = state
                            debounce = time.time()
                        else:
                            raise MachineStopped

                    # state changed
                    return

                except RuntimeError:
                    continue
                except (KeyboardInterrupt, EOFError):
                    raise MachineStopped

    @staticmethod
    def _configure_sysfs_interface(gpio):
        """configure_sysfs_interface(gpio):

        Sets up the sysfs interface for reading events from GPIO
        (general purpose input/output). Checks if path/file is readable.
        Returns the value and edge filenames for this GPIO.
        """
        # Set up an input polling file for machine cycle sensor:
        gpio_sysfs_path = '/sys/class/gpio/gpio{}/'.format(gpio)
        gpio_value_file = gpio_sysfs_path + 'value'
        gpio_edge_file = gpio_sysfs_path + 'edge'

        # Run the gauntlet to make sure GPIO is configured properly
        if not os.access(gpio_value_file, os.R_OK):
            message = ('GPIO value file does not exist or cannot be read. '
                       'You must export the GPIO no {} as input first!')
            raise OSError(13, message.format(gpio), gpio_value_file)

        if not os.access(gpio_edge_file, os.R_OK):
            message = ('GPIO edge file does not exist or cannot be read. '
                       'You must export the GPIO no {} as input first!')
            raise OSError(13, message.format(gpio), gpio_edge_file)

        with io.open(gpio_edge_file, 'r') as edge_file:
            message = ('GPIO {} must be set to generate interrupts '
                       'on both rising AND falling edge!')
            if 'both' not in edge_file.read():
                raise OSError(19, message.format(gpio), gpio_edge_file)

        return gpio_value_file


@singleton
class RPiGPIOSensor(SensorBase):
    """Simple RPi.GPIO input driver for photocell"""
    name = 'RPi.GPIO input driver'
    timeout = 5
    gpio = INTERFACE_CFG.sensor_gpio
    bounce_time = INTERFACE_CFG.bounce_time

    def __enter__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio, GPIO.IN)
        return self

    def __exit__(self, *_):
        GPIO.cleanup(self.gpio)
        return True

    @property
    def parameters(self):
        """Gets a list of parameters"""
        parameters = OrderedDict()
        parameters['Sensor driver'] = self.name
        parameters['GPIO number'] = self.gpio
        return parameters

    def wait_for(self, new_state, timeout=None):
        """Use interrupt handlers in RPi.GPIO for triggering the change"""
        _timeout = timeout or self.timeout

        change = GPIO.RISING if new_state else GPIO.FALLING
        while True:
            try:
                channel = GPIO.wait_for_edge(self.gpio, change,
                                             timeout=_timeout*1000,
                                             bouncetime=self.bounce_time)
                if channel is None:
                    raise MachineStopped
                else:
                    return
            except RuntimeError:
                # In case RuntimeError: Error waiting for edge is raised...
                continue
            except (KeyboardInterrupt, EOFError):
                # Emergency stop by keyboard
                raise MachineStopped


@singleton
class WiringPiOutput(OutputBase):
    """A 32-channel control interface based on two MCP23017 chips"""
    name = 'MCP23017 driver using wiringPi2-Python library'
    pin_base = INTERFACE_CFG.pin_base
    signal_numbers = [*range(pin_base, pin_base+32)]

    def __init__(self):
        # Set up an output interface on two MCP23017 chips
        wiringpi.mcp23017Setup(self.pin_base, self.mcp0_address)
        wiringpi.mcp23017Setup(self.pin_base + 16, self.mcp1_address)
        # Set all I/O lines on MCP23017s as outputs - mode=1
        for pin in self.mapping.values():
            wiringpi.pinMode(pin, 1)

    def valves_on(self, signals):
        """Looks a signal up in arrangement and turns it on"""
        for sig in signals:
            pin_number = self.mapping.get(sig)
            if not pin_number:
                continue
            wiringpi.digitalWrite(pin_number, 1)

    def valves_off(self):
        """Looks a signal up in arrangement and turns it off"""
        for pin in self.mapping.values():
            wiringpi.digitalWrite(pin, 0)


class SMBusOutput(OutputBase):
    """Python SMBus-based output controller for rpi2caster."""
    name = 'SMBus output driver'
    # define a signal-to-bit mapping
    # NOTE: reverse the range if signals are backwards
    signal_numbers = [2 ** x for x in range(31, -1, -1)]

    def _send(self, byte0, byte1, byte2, byte3):
        """Write 4 bytes of data to all ports (A, B) on all devices (0, 1)"""
        self.port.write_byte_data(self.mcp0_address, OLATA, byte0)
        self.port.write_byte_data(self.mcp0_address, OLATB, byte1)
        self.port.write_byte_data(self.mcp1_address, OLATA, byte2)
        self.port.write_byte_data(self.mcp1_address, OLATB, byte3)

    def valves_on(self, signals):
        """Get the signals, transform them to numeric value and send
        the bytes to i2c devices"""
        if signals:
            number = sum(self.mapping.get(signal, 0) for signal in signals)
            # Split it to four bytes sent in sequence
            byte0 = (number >> 24) & 0xff
            byte1 = (number >> 16) & 0xff
            byte2 = (number >> 8) & 0xff
            byte3 = number & 0xff
        else:
            byte0 = byte1 = byte2 = byte3 = 0x00

        UI.display('{:08b} {:08b} {:08b} {:08b}'
                   .format(byte0, byte1, byte2, byte3), min_verbosity=3)
        self._send(byte0, byte1, byte2, byte3)

    def valves_off(self):
        """Turn off all the valves"""
        self._send(0x00, 0x00, 0x00, 0x00)

    def __enter__(self):
        self.port = SMBus(self.i2c_bus_number)
        for address in self.mcp0_address, self.mcp1_address:
            for register in IODIRA, IODIRB, OLATA, OLATB:
                self.port.write_byte_data(address, register, 0x00)
        return self

    def __exit__(self, *_):
        self.valves_off()
        self.port = None
        return True


@weakref_singleton
class ParallelOutput(SMBusOutput):
    """Output driver for parallel port. Sends four bytes in sequence:
    byte0: O N M L K J I H
    byte1: G F S E D 0075 C B
    byte2: A 1 2 3 4 5 6 7
    byte3: 8 9 10 11 12 13 14 0005
    Uses pyparallel package (or python3-parallel from debian repo)
    """
    signal_numbers = [2 ** x for x in range(31, -1, -1)]
    name = 'Symbiosys parallel port interface'

    def __enter__(self):
        self.port = self.port or Parallel()
        if self.port and not self.working:
            # Check for working to avoid re-initialization
            # toggle the init on and off for a moment
            self.port.setInitOut(False)
            # 5us sleep
            time.sleep(0.000005)
            self.port.setInitOut(True)
            # interface is initialized and waiting until button press
            UI.display_header('Press the button on the interface...')
            self._wait_until_not_busy()
            self.working = True
        return self

    def _send(self, byte0, byte1, byte2, byte3):
        """Send the codes through the data port"""
        def send_byte(single_byte):
            """Send a single byte of data"""
            # nothing to do if port is not there...
            if not self.port:
                return
            # wait until we can send the codes
            self._wait_until_not_busy()
            # set the byte on port lines
            self.port.setData(single_byte)
            # strobe on (negative logic)
            # signal that we finished and wait until interface acknowledges
            self.port.setDataStrobe(False)
            # 5us sleep
            time.sleep(0.000005)
            # wait until interface signals BUSY
            while self.port.getInBusy():
                pass
            # strobe off (again, negative logic)
            self.port.setDataStrobe(True)
            self._wait_until_not_busy()

        for byte in (byte0, byte1, byte2, byte3):
            send_byte(byte)

    def _wait_until_not_busy(self):
        """Wait until busy goes OFF"""
        while not self.port.getInBusy():
            time.sleep(0.01)

    def valves_off(self):
        """Deactivate the valves - actually, do nothing"""
        pass


class ParallelSensor(SensorBase):
    """Parallel sensor does nothing, as everything is controlled by
    the micro-controller in the interface."""
    name = 'Symbiosys parallel port interface'

    def check_if_machine_is_working(self):
        """Reset the interface if needed and go on"""
        UI.confirm('Turn on the machine...', default=True, abort_answer=False)

    def wait_for(self, new_state, timeout=None):
        """Do nothing"""
        new_state, timeout = new_state, timeout


class MachineStopped(Exception):
    """Machine stopped exception"""
    def __str__(self):
        return ''


SENSORS.update(sysfs=SysfsSensor,
               rpi_gpio=RPiGPIOSensor if GPIO else None,
               parallel=ParallelSensor if Parallel else None,
               simulation=SimulationSensor)
OUTPUTS.update(wiringpi=WiringPiOutput if wiringpi else None,
               smbus=SMBusOutput if SMBus else None,
               parallel=ParallelOutput if Parallel else None,
               simulation=SimulationOutput)
