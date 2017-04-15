# -*- coding: utf-8 -*-
"""Caster object for either,  real or virtual Monotype composition caster"""
# Standard library imports
import io
import os
import select
import time
from collections import OrderedDict
from functools import wraps

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
from .config import CFG
from .definitions import OFF, HMN, KMN, UNIT_SHIFT
from .misc import singleton, weakref_singleton
from .ui import UI, option

# Interface config
INTERFACE_CFG = CFG.interface
# Constants for readability
AIR_ON = True
AIR_OFF = False
# Output latch registers for SMBus MCP23017 control
OLATA, OLATB = 0x14, 0x15
# Port direction registers for SMBus MCP23017 control
IODIRA, IODIRB = 0x00, 0x10


class MachineStopped(Exception):
    """Machine stopped exception"""
    pass


class MonotypeCaster(object):
    """Methods common for Caster classes, used for instantiating
    caster driver objects (whether real hardware or mockup for simulation)."""
    pump_working = False
    # caster modes
    testing, simulation, punching, calibration = False, False, False, False
    need_row_16, row_16_mode = False, OFF

    def __enter__(self):
        """Lock the resource so that only one object can use it
        with context manager"""
        UI.pause('Entering the caster context...', min_verbosity=3)
        sensor, output = self.interface_factory()
        self.sensor = sensor()
        self.output = output()
        with self.sensor, self.output:
            return self

    def __exit__(self, *_):
        UI.pause('Caster no longer in use.', min_verbosity=3)
        self.output.valves_off()
        # release resources
        self.sensor = None
        self.output = None

    @property
    def sensor(self):
        """Sensor controls the advance between steps during casting, testing
        or punching the ribbon"""
        return self.__dict__.get('_sensor') or SimulationSensor()

    @sensor.setter
    def sensor(self, sensor):
        """Set a current sensor"""
        self.__dict__['_sensor'] = sensor

    @property
    def output(self):
        """Output is the machine control mechanism, using solenoid valves"""
        return self.__dict__.get('_output') or SimulationOutput()

    @output.setter
    def output(self, output):
        """Set the current output"""
        self.__dict__['_output'] = output

    @property
    def parameters(self):
        """Gets a list of parameters"""
        # Collect data from I/O drivers
        parameters = OrderedDict({'': 'Caster parameters'})
        parameters.update(**self.sensor.parameters)
        parameters.update(**self.output.parameters)
        return parameters

    @property
    def diagnostics(self):
        """Machine diagnostics i.e. testing or calibration"""
        return self.testing or self.calibration

    @diagnostics.setter
    def diagnostics(self, value=False):
        """Turns the testing or calibration mode off"""
        if not value:
            self.testing = False
            self.calibration = False

    @property
    def casting(self):
        """Check if the machine is casting"""
        return not self.punching and not self.testing and not self.calibration

    @property
    def use_row_16(self):
        """Check if row 16 is currently needed."""
        return self.__dict__.get('_use_row_16') or False

    @use_row_16.setter
    def use_row_16(self, value):
        """Choose the diecase row 16 addressing mode, if needed.

        Row 16 is needed and currently off:
        Ask which row 16 addressing system the user's machine has, if any.

        Row 16 is not needed and currently on:
        Tell the user to turn off the attachment.

        Row 16 is not needed and is off, or is needed and is on: do nothing.
        """
        names = {HMN: 'HMN', KMN: 'KMN', UNIT_SHIFT: 'unit-shift'}
        att_name = names.get(self.row_16_mode) or ''

        is_required = bool(value)
        is_active = bool(self.row_16_mode)
        # store the attribute
        self.__dict__['_use_row_16'] = is_required
        # check and notify the user
        if is_required and not is_active:
            self.choose_row16_addressing()
        elif is_active and not is_required:
            UI.pause('\nTurn off the {} attachment.\n'.format(att_name))
            self.row_16_mode = OFF
        elif is_required and is_active:
            UI.display('The {} attachment is turned on - OK.'.format(att_name))

    def choose_row16_addressing(self):
        """Let user decide which way to address row 16"""
        prompt = ('Your ribbon contains codes from the 16th row.\n'
                  'It is supported by special attachments for the machine.\n'
                  'Which mode does your caster use: HMN, KMN, Unit-Shift?\n\n'
                  'If off - characters from row 15 will be cast instead.')
        options = [option(key='h', value=HMN, seq=1, text='HMN'),
                   option(key='k', value=KMN, seq=2, text='KMN'),
                   option(key='u', value=UNIT_SHIFT, seq=3, text='Unit shift'),
                   option(key='o', value=OFF, seq=4,
                          text='Off - cast from row 15 instead')]
        mode = UI.simple_menu(prompt, options,
                              default_key='o', allow_abort=True)
        self.row_16_mode = mode

    def process(self, signals, timeout=None):
        """Control a Monotype composition caster
        for one revolution of its main shaft.

        Wait until the machine is in the position to turn on the valves
        (machine cycle sensor goes ON - air bar lowering on the paper tower).
        Send signals to the control interface.
        After the cycle sensor goes OFF (air bar rising), switch all
        of the valves off and end here, so the caller can continue
        and send next signals.
        """
        # Casting cycle
        # (sensor on - valves on - sensor off - valves off)
        self.output.valves_off()
        self.sensor.wait_for(AIR_ON, timeout=timeout)
        self.output.valves_on(signals)
        self.sensor.wait_for(AIR_OFF, timeout=timeout)
        self.output.valves_off()
        # Successful ending with no exceptions - the combination has been cast

    def interface_factory(self, default_sensor=INTERFACE_CFG.sensor,
                          default_output=INTERFACE_CFG.output):
        """Interface factory combines the sensor and output modules into
        an Interface class. Returns an instance of this class."""
        def test_sensor():
            """Sensor used for testing - manual advance ONLY"""
            self.testing = True
            return TestingSensor()

        def simulation_sensor():
            """Sensor used for simulation - manual or automatic advance,
            can simulate machine stop"""
            self.simulation = True
            return SimulationSensor()

        def punching_sensor():
            """Manual or time-driven advance, no machine stop detection"""
            self.punching = True
            return PunchingSensor()

        def simulation_output():
            """Simulate valves instead of using real hardware"""
            self.simulation = True
            return SimulationOutput()

        def make_interface():
            """Get the sensor and output drivers"""
            sensor_names = {'simulation': simulation_sensor,
                            'sysfs': SysfsSensor,
                            'rpi.gpio': RPiGPIOSensor,
                            'parallel': ParallelInterface,
                            'testing': test_sensor,
                            'punching': punching_sensor}
            output_names = {'simulation': simulation_output,
                            'wiringpi': WiringPiOutput,
                            'smbus': SMBusOutput,
                            'parallel': ParallelInterface}
            # First get the backend from configuration
            backend = [default_sensor, default_output]
            # Use simulation mode if set in configuration
            simulation = True if 'simulation' in backend else self.simulation
            # If we don't know whether simulation is on or off - ask
            if simulation is None and INTERFACE_CFG.choose_backend:
                prompt = 'Use real caster? (no = simulation mode)'
                simulation = not UI.confirm(prompt, default=True)
            # Use parallel interface
            parallel = (True if 'parallel' in backend and not simulation
                        else False)
            punching = True if 'punching' in backend else self.punching
            # Override the backend for parallel and simulation
            # Use parallel sensor above all else
            # Testing and punching sensor overrides simulation sensor
            sensor = ('parallel' if parallel
                      else 'testing' if self.testing
                      else 'punching' if punching
                      else 'simulation' if simulation
                      else default_sensor)
            output = ('parallel' if parallel
                      else 'simulation' if simulation
                      else default_output)
            # Get the function for building the interface based on name
            # These functions will be executed when needed
            sensor_function = sensor_names.get(sensor, SimulationSensor)
            output_function = output_names.get(output, SimulationOutput)
            return sensor_function, output_function

        return make_interface()


class SensorBase(object):
    """Mockup for a machine cycle sensor"""
    name = 'generic machine cycle sensor'
    gpio = INTERFACE_CFG.sensor_gpio
    last_state, manual_mode, signals = True, True, None
    timeout, time_on, time_off = 30, 0.1, 0.1

    def __enter__(self):
        UI.pause('Using a {} for machine feedback'.format(self.name),
                 min_verbosity=2)
        return self

    def __exit__(self, *_):
        UI.pause('The {} is no longer in use'.format(self.name),
                 min_verbosity=3)
        # Reset manual mode
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
                self.wait_for(new_state=True, timeout=30)
                while cycles:
                    # Run a new cycle
                    UI.display(cycles)
                    self.wait_for(new_state=True, timeout=30)
                    cycles -= 1
                return

            except (MachineStopped, KeyboardInterrupt, EOFError):
                prompt = 'Machine is not running. Y to try again or N to exit?'
                UI.confirm(prompt, default=True, abort_answer=False)

    def wait_for(self, new_state, **_):
        """Waits for a keypress to emulate machine cycle, unless user
        switches to auto mode, where all combinations are processed in batch"""
        def switch_to_auto():
            """Switch to automatic mode"""
            self.manual_mode = False

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


class PunchingSensor(SensorBase):
    """A special sensor class for perforators"""
    name = 'timer-driven or manual advance for perforator'
    time_on, time_off = 0.25, 0.4

    @staticmethod
    def check_if_machine_is_working():
        """Ask for user confirmation before punching"""
        UI.confirm('\nRibbon punching: \n'
                   'Put the ribbon on the perforator and turn on the air.',
                   abort_answer=False, default=True, force_answer=True)


class TestingSensor(SensorBase):
    """A keyboard-operated "sensor" for testing inputs.
    No automatic mode is supported."""
    name = 'manual advance for testing'

    def wait_for(self, new_state, **_):
        """Waits for keypress before turning the line off"""
        if not new_state:
            UI.pause('Next combination?')

    @staticmethod
    def check_if_machine_is_working():
        """Do nothing here"""
        pass


class OutputBase(object):
    """Mockup for a driver for 32 pneumatic outputs"""
    signals_arrangement = INTERFACE_CFG.signals_arrangement
    mcp0_address = INTERFACE_CFG.mcp0
    mcp1_address = INTERFACE_CFG.mcp1
    i2c_bus_number = INTERFACE_CFG.i2c_bus
    signal_numbers = [*range(1, 33)]
    working, port = False, None
    name = 'generic output driver'

    def __enter__(self):
        UI.pause('Using the {} for sending signals...'.format(self.name),
                 min_verbosity=2)
        return self

    def __exit__(self, *_):
        self.valves_off()
        UI.pause('Driver for {} is no longer in use.'.format(self.name),
                 min_verbosity=3)

    @property
    def mapping(self):
        """Signal-to-number mapping (memoize for multiple use)"""
        assoc = self.__dict__.get('_mapping')
        if not assoc:
            assoc = dict(zip(INTERFACE_CFG.signals_arrangement,
                             self.signal_numbers))
            self.__dict__['_mapping'] = assoc
        return assoc

    @property
    def parameters(self):
        """Gets a list of parameters"""
        parameters = OrderedDict()
        parameters['Output driver'] = self.name
        parameters['Signals arrangement'] = ' '.join(self.signals_arrangement)
        return parameters

    @staticmethod
    def valves_on(signals_list):
        """Turns on multiple valves"""
        for sig in signals_list:
            UI.display(sig + ' on', min_verbosity=2)

    def valves_off(self):
        """Turns off all the valves"""
        for sig in self.signals_arrangement:
            UI.display(sig + ' off', min_verbosity=2)


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

    def wait_for(self, new_state, timeout=None, **_):
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

    @property
    def parameters(self):
        """Gets a list of parameters"""
        parameters = OrderedDict()
        parameters['Sensor driver'] = self.name
        parameters['GPIO number'] = self.gpio
        return parameters

    def wait_for(self, new_state, timeout=None, **_):
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

    def valves_on(self, signals=()):
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


@weakref_singleton
class ParallelInterface(SensorBase, SMBusOutput):
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

    def _send(self, *data):
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

        for byte in data:
            send_byte(byte)

    def _wait_until_not_busy(self):
        """Wait until busy goes OFF"""
        while not self.port.getInBusy():
            time.sleep(0.01)

    def check_if_machine_is_working(self):
        """Reset the interface if needed and go on"""
        UI.confirm('Turn on the machine...', default=True, abort_answer=False)

    def valves_off(self):
        """Deactivate the valves - actually, do nothing"""
        pass

    def wait_for(self, *args, **kw):
        """Do nothing"""
        pass


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

    def valves_on(self, signals=()):
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


def caster_context(casting_routine):
    """Decorator for casting routines.
    Checks current modes (simulation, perforation, testing)"""
    @wraps(casting_routine)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        what = ('cast composition' if self.caster.casting
                else 'test the outputs' if self.caster.testing
                else 'calibrate the machine' if self.caster.calibration
                else 'punch the ribbon' if self.caster.punching
                else 'blow')
        UI.pause('About to {}...'.format(what), min_verbosity=3)
        with self.caster:
            return casting_routine(self, *args, **kwargs)

    return wrapper


def calibration_mode(routine):
    """Use a calibration mode for the routine.
    This will affect casting statistics and some prompts."""
    @wraps(routine)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        # Turn on the calibration mode
        try:
            self.caster.calibration = True
            return routine(self, *args, **kwargs)
        finally:
            self.caster.calibration = False
    return wrapper


def testing_mode(routine):
    """Output testing mode - skip some steps in casting"""
    @wraps(routine)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        # Turn on the testing mode
        try:
            self.caster.testing = True
            return routine(self, *args, **kwargs)
        finally:
            self.caster.testing = False
    return wrapper
