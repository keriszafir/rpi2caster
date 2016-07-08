# -*- coding: utf-8 -*-
"""Caster object for either,  real or virtual Monotype composition caster"""
# Built-in time module
from time import time, sleep
# Custom exceptions module
from . import exceptions as e
# Constants module
from . import constants as c
# Default user interface
from .global_config import UI
from .global_config import SIGNALS_ARRANGEMENT, SENSOR, OUTPUT, BACKEND_SELECT
# Constants for readability
AIR_ON = True
AIR_OFF = False


def adjust_signals(signal_processing_routine):
    """Adjusts the signals received by caster so that:
    1. O15 is stripped unless we are in testing mode (if explicitly stated)
        or in punching mode (always - it helps drive the punches)
    2. row 16 is addressed according to the selected method: HMN, unit-shift
        or is not addressed for plain machines (O15 will be cast instead)
    """
    def wrapper(self, signals, *args, **kw):
        """Changes the signals to match the selected method of addressing
        16th row on the matrix case"""

        def convert_unitshift(signals):
            """Adjust signals for unit-shift:
            replace D column with EF;
            add D for shifting the diecase to row 16.
            Normal wedge stays where it was; only the diecase moves.
            The width of characters in row 16 is the same as for row 15,
            unless 0005 & 0075 wedge corrections are applied.
            """
            if 'D' in signals:
                signals.remove('D')
                signals.extend(['E', 'F'])
            if '16' in signals:
                signals.append('D')

        def convert_hmn(signals):
            """Adjust signals for HMN as commented below.
            The HMN attachment was rare and required special normal wedges
            with additional step for 16th row."""
            if 'H' in signals:
                # H -> HN
                signals.append('N')
            elif 'N' in signals and not ('I' in signals or 'L' in signals):
                # N -> MN
                signals.append('M')
            elif 'N' in signals or 'M' in signals:
                # NI, NL, M -> HNI, HNL, HM
                signals.append('H')
            elif [x for x in 'ABCDEFGIJKL' if x in signals]:
                # A...G, I...L -> HMA...G, HMI...L
                signals.extend(['H', 'M'])
            else:
                # O15 (no other signals) -> HMN
                signals.extend(['H', 'M', 'N'])

        def convert_kmn(signals):
            """Adjust signals for the rare KMN attachment.
            This attachment was made by one of Monotype's customers,
            and HMN was based off it - so it's even less common..."""
            if 'K' in signals:
                # K16: add N
                signals.append('N')
            elif 'M' in signals:
                # M16: add K
                signals.append('K')
            elif 'N' in signals and ('I' in signals or 'L' in signals):
                # NI16, NL16: add K
                signals.append('K')
            elif 'N' in signals:
                # N16: add M
                signals.append('M')
            elif [x for x in 'ABCDEFGHIJL' if x in signals]:
                # All signals apart from above and O16: add KM
                signals.extend(['K', 'M'])
            else:
                # O16: add KMN
                signals.extend(['K', 'M', 'N'])

        # No signals = no casting!
        if not signals:
            return False
        if self.mode.hmn and '16' in signals:
            convert_hmn(signals)
        elif self.mode.kmn and '16' in signals:
            convert_kmn(signals)
        elif self.mode.unitshift:
            # Unit-shift is active for all rows, not just 16
            convert_unitshift(signals)
        # Return a list of "normal" signals i.e. with no signal 16,
        # arranged in Monotype order (NMLK...13, 14, 0005, O15)
        # Scrap O15 signal unless we're in testing mode, where it can
        # be explicitly turned on.
        signals = [sig for sig in c.SIGNALS if sig in signals and
                   (sig is not 'O15' or self.mode.testing)]
        # Always add O15 for punching ribbons
        if self.mode.punching and 'O15' not in signals:
            signals.append('O15')
        # Adjust the signals just before casting; show the new combination
        UI.display('Sending %s' % (' '.join(signals) if signals
                                   else 'no signals'))
        return signal_processing_routine(self, signals, *args, **kw)
    return wrapper


class MonotypeCaster(object):
    """Methods common for Caster classes, used for instantiating
    caster driver objects (whether real hardware or mockup for simulation)."""
    def __init__(self):
        self.mode = CasterMode()
        self.sensor = SimulationSensor()
        self.output = SimulationOutput()
        self.lock = False
        self.pump_working = False

    def __enter__(self):
        """Lock the resource so that only one object can use it
        with context manager"""
        if self.lock:
            UI.display('Caster is already busy!')
        else:
            self.lock = True
            UI.debug_pause('Entering the caster context...')
            return self

    def __exit__(self, *_):
        UI.debug_pause('Caster no longer in use.')
        self.lock = False

    @property
    def parameters(self):
        """Gets a list of parameters"""
        # Collect data from I/O drivers
        return self.sensor.parameters + self.output.parameters

    @adjust_signals
    def process(self, signals):
        """process(signals):

        Checks for the machine's rotation, sends the signals (activates
        solenoid valves) after the caster is in the "air bar down" position.

        If no machine rotation is detected (sensor input doesn't change
        its state) during cycle_timeout, calls a function to ask user
        what to do (can be useful for resuming casting after manually
        stopping the machine for a short time - not recommended as the
        mould cools down and type quality can deteriorate).

        If the pump was working, the program will store 0075/0005 wedge
        positions, send 0005 to stop the pump and display the menu.
        If the operator decides to go on with casting, the aborted sequence
        will be re-cast so as to avoid missing characters in the composition.
        If the pump was working before, its operation will be resumed
        and the wedges will be reset to previous positions.

        When casting, the pace is dictated by the caster and its RPM. Thus,
        we can't arbitrarily set the intervals between valve ON and OFF
        signals. We need to get feedback from the machine, and we can use
        contact switch (unreliable in the long run), magnet & reed switch
        (not precise enough) or a photocell sensor + LED (very precise).
        We can use a paper tower's operating lever for obscuring the sensor
        (like John Cornelisse did), or we can use a partially obscured disc
        attached to the caster's shaft (like Bill Welliver did).
        Both ways are comparable; the former can be integrated with the
        valve block assembly, and the latter allows for very precise tweaking
        of duty cycle (bright/dark area ratio) and phase shift (disc's position
        relative to 0 degrees caster position).
        """
        busy = True
        while busy:
            # Escape this only by returning True on success, or raising
            # exceptions handled by the methods of the Casting class
            try:
                # Casting cycle
                # (sensor on - valves on - sensor off - valves off)
                self.sensor.wait_for(AIR_ON)
                self.output.valves_on(signals)
                self.sensor.wait_for(AIR_OFF)
                self.output.valves_off()
                busy = False
                # Successful ending - the combination has been cast
            except (e.MachineStopped, KeyboardInterrupt, EOFError):
                # Machine stopped during casting - clean up
                # Punching doesn't need this at all
                if not self.mode.punching:
                    self.pump_stop()
                # Exception will be handled in session
                raise

    def pump_stop(self):
        """Forces pump stop - won't end until it is turned off"""
        def send_signals():
            """Send a combination - full cycle"""
            self.output.valves_off()
            self.sensor.wait_for(AIR_ON, 30)
            self.output.valves_on(['N', 'J', 'S', '0005'])
            self.sensor.wait_for(AIR_OFF, 30)
            self.output.valves_off()

        UI.display('Turning all valves off - just in case...')
        self.output.valves_off()
        while self.pump_working:
            UI.display('The pump is still working - turning it off...')
            try:
                # Run two full sequences to be sure
                send_signals()
                send_signals()
                UI.display('Pump is now off.')
                return True
            except (e.MachineStopped, KeyboardInterrupt, EOFError):
                pass


class SensorMixin(object):
    """Mockup for a machine cycle sensor"""
    def __init__(self):
        self.lock = False
        self.manual_mode = True
        self.last_state = False
        self.name = 'generic machine cycle sensor'

    def __enter__(self):
        if not self.lock:
            self.lock = True
            UI.debug_pause('Using a %s for machine feedback' % self.name)
            return self

    def __exit__(self, *_):
        UI.debug_pause('The %s is no longer in use' % self.name)
        # Reset manual mode
        self.manual_mode = True
        self.lock = False

    @property
    def parameters(self):
        """Gets a list of parameters"""
        return [(self.name, 'Sensor driver'),
                (self.manual_mode, 'Manual mode')]

    def check_if_machine_is_working(self):
        """Detect machine cycles and alert if it's not working"""
        UI.display('Turn on the air, motor, pump (if put out) and machine.')
        UI.display('Checking if the machine is running...')
        cycles = 3
        while True:
            try:
                while cycles:
                    # Run a new cycle
                    UI.display(cycles)
                    self.wait_for(new_state=True, timeout=30)
                    cycles -= 1
                return True
            except (e.MachineStopped, KeyboardInterrupt, EOFError):
                if UI.confirm('Machine stopped - continue? ', default=False):
                    # Continue checking
                    pass
                else:
                    return False

    def wait_for(self, new_state, timeout=30, time_on=0.1, time_off=0.1):
        """Waits for a keypress to emulate machine cycle, unless user
        switches to auto mode, where all combinations are processed in batch"""
        status = {True: 'ON', False: 'OFF'}
        UI.debug_info('The sensor is going %s' % status[new_state])
        if self.manual_mode:
            start_time = time()
            # Ask whether to cast or simulate machine stop
            prompt = ('[A] to switch to automatic mode, [S] to stop\n'
                      'or leave blank to continue?')
            answer = UI.enter_data_or_blank(prompt) or ' '
            if answer in 'aA':
                self.manual_mode = False
            elif answer in 'sS':
                raise e.MachineStopped
            elif time() - start_time > timeout:
                UI.display('Timeout - you answered after %ds' % timeout)
                raise e.MachineStopped
        elif new_state:
            sleep(time_off)
        else:
            sleep(time_on)


class SimulationSensor(SensorMixin):
    """Simulate casting with no actual machine"""
    def __init__(self):
        super().__init__()
        self.name = 'simulation - mockup casting interface'

    def check_if_machine_is_working(self):
        """Warn that this is just a simulation"""
        UI.display('Simulation mode - no machine is used.\n'
                   'This will emulate the actual casting sequence '
                   'as closely as possible.\n')
        return super().check_if_machine_is_working()


class PunchingSensor(SensorMixin):
    """A special sensor class for perforators"""
    def __init__(self):
        super().__init__()
        self.name = 'timer-driven or manual advance for perforator'

    def check_if_machine_is_working(self):
        """Ask for user confirmation before punching"""
        UI.pause('\nRibbon punching: \n'
                 'Put the ribbon on the perforator and turn on the air.')
        return True

    def wait_for(self, new_state, timeout=30, time_on=0.25, time_off=0.4):
        """Calls simulation sensor's function, but with different timings"""
        super().wait_for(new_state, timeout, time_on, time_off)


class TestSensor(SensorMixin):
    """A keyboard-operated "sensor" for testing inputs.
    No automatic mode is supported."""
    def __init__(self):
        super().__init__()
        self.name = 'manual advance for testing'

    def wait_for(self, new_state, *_):
        """Waits for keypress before turning the line off"""
        if not new_state:
            UI.pause('Next combination?')

    def check_if_machine_is_working(self):
        """Do nothing here"""
        return True


class OutputMixin(object):
    """Mockup for a driver for 32 pneumatic outputs"""
    def __init__(self, signals_arrangement=SIGNALS_ARRANGEMENT):
        self.lock = False
        self.name = 'generic output driver'
        self.signals_arrangement = signals_arrangement
        self.working = True

    def __del__(self):
        UI.debug_pause('Deleting the %s' % self.name)

    def __enter__(self):
        if not self.lock:
            self.lock = True
            UI.debug_pause('Using the %s for sending signals...' % self.name)
            return self

    def __exit__(self, *_):
        self.valves_off()
        UI.debug_pause('Driver for %s no longer in use.' % self.name)
        self.lock = False

    @property
    def parameters(self):
        """Gets a list of parameters"""
        return [(self.name, 'Output driver'),
                (' '.join(self.signals_arrangement), 'Signals arrangement')]

    def one_on(self, sig):
        """Looks a signal up in arrangement and turns it on"""
        try:
            UI.debug_info(sig + ' on')
        except KeyError:
            raise e.WrongConfiguration('Signal %s not defined!' % sig)

    def one_off(self, sig):
        """Looks a signal up in arrangement and turns it on"""
        try:
            UI.debug_info(sig + ' off')
        except KeyError:
            raise e.WrongConfiguration('Signal %s not defined!' % sig)

    def valves_on(self, signals_list):
        """Turns on multiple valves"""
        for sig in signals_list:
            self.one_on(sig)

    def valves_off(self):
        """Turns off all the valves"""
        for sig in self.signals_arrangement:
            self.one_off(sig)


class SimulationOutput(OutputMixin):
    """Simulation output driver - don't control any hardware"""
    def __init__(self):
        super().__init__()
        self.name = 'simulation - mockup casting interface'


class CasterMode(object):
    """Session mode: casting / simulation / perforation"""
    def __init__(self):
        self.punching = False
        self.testing = False
        self.calibration = False

    @property
    def simulation(self):
        """Simulation mode"""
        return self.__dict__.get('simulation')

    @simulation.setter
    def simulation(self, value):
        """Set the simulation mode"""
        self.__dict__['simulation'] = value

    @property
    def calibration(self):
        """Machine calibration mode"""
        return self.__dict__.get('calibration', False)

    @calibration.setter
    def calibration(self, value):
        """Set the machine calibration mode"""
        self.__dict__['calibration'] = value

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
    def punching(self):
        """Punching mode"""
        return self.__dict__.get('punching', False)

    @punching.setter
    def punching(self, value):
        """Set the punching mode"""
        self.__dict__['punching'] = value

    @property
    def testing(self):
        """Testing mode"""
        return self.__dict__.get('testing', False)

    @testing.setter
    def testing(self, value):
        """Set the testing mode"""
        self.__dict__['testing'] = value

    @property
    def casting(self):
        """Check if the machine is casting"""
        return not self.punching and not self.testing and not self.calibration

    @property
    def hmn(self):
        """Check if HMN mode is currently on"""
        return self.__dict__.get('_hmn', False)

    @hmn.setter
    def hmn(self, value):
        """Set the HMN mode"""
        value = value and True or False
        self.__dict__['_hmn'] = value

    @property
    def kmn(self):
        """Check if KMN mode is currently on"""
        return self.__dict__.get('_kmn', False)

    @kmn.setter
    def kmn(self, value):
        """Set the KMN mode"""
        self.__dict__['_kmn'] = value

    @property
    def unitshift(self):
        """Check if the unit shift mode is currently on"""
        return self.__dict__.get('_unit-shift', False)

    @unitshift.setter
    def unitshift(self, value):
        """Set the unit-shift mode"""
        self.__dict__['_unit-shift'] = value

    @property
    def casting_backend(self):
        """Chooses the sensor and output for controlling the machine
        or simulating machine control"""
        # First set the simulation backend
        backend = [SENSOR, OUTPUT]
        # Set simulation mode if specified in config
        if 'simulation' in backend:
            self.simulation = True
        if self.simulation is None and BACKEND_SELECT:
            # Select the casting or simulation mode
            prompt = 'Use caster? (no = simulation mode)'
            self.simulation = not UI.confirm(prompt, True)
        if self.simulation:
            # Simulation sensor and output driver must work together
            # (unless for punching or testing)
            backend = ['simulation', 'simulation']
        # Override depending on mode
        backend[0] = (self.testing and 'testing' or
                      self.punching and 'punching' or backend[0])
        if 'parallel' in backend:
            # Parallel sensor and output driver must work together
            # even for punching or testing
            backend = ['parallel', 'parallel']
        sensor, output = backend
        return (SENSORS.get(sensor, SimulationSensor),
                OUTPUTS.get(output, SimulationOutput))

    def choose_row16_addressing(self):
        """Let user decide which way to address row 16"""
        def hmn_on():
            """Turn on the HMN 16x17 attachment"""
            UI.display('Turn the HMN attachment ON')
            self.hmn = True

        def kmn_on():
            """Turn on the rare KMN 16x17 attachment"""
            UI.display('Turn the KMN attachment ON')
            self.kmn = True

        def unitshift_on():
            """Turn on the unit-shift attachment (introduced in 1960s)"""
            UI.display('Turn the attachment ON - switch under the paper tower')
            self.unitshift = True

        def do_nothing():
            """User can choose not to use any attachment"""
            return None

        prompt = ('Your ribbon contains codes from the 16th row.\n'
                  'It is supported by special attachments for the machine.\n'
                  'Which mode does your caster use: HMN, KMN, Unit-Shift?\n\n'
                  'If none - characters from row 15 will be cast instead.\n\n'
                  'Your choice: [U]nit-Shift, [H]MN, [K]MN '
                  '(leave blank for none)?: ')
        options = {'U': unitshift_on,
                   'H': hmn_on,
                   'K': kmn_on,
                   '': do_nothing}
        UI.simple_menu(prompt, options)()


def sysfs_sensor():
    """Gets hardware sensor - prevents import loop"""
    from .input_driver_sysfs import SysfsSensor
    return SysfsSensor()


def wiringpi_output():
    """Gets hardware output - prevents import loop"""
    from .output_driver_wiringpi import WiringPiOutputDriver
    return WiringPiOutputDriver()


def parallel_sensor():
    """A parallel port sensor for John Cornelisse's old interface"""
    from .driver_parallel import ParallelSensor
    return ParallelSensor()


def parallel_output():
    """A parallel port valve control for John Cornelisse's old interface"""
    from .driver_parallel import ParallelOutputDriver
    return ParallelOutputDriver()


SENSORS = {'simulation': SimulationSensor, 'sysfs': sysfs_sensor,
           'parallel': parallel_sensor, 'testing': TestSensor,
           'punching': PunchingSensor}
OUTPUTS = {'simulation': SimulationOutput, 'wiringpi': wiringpi_output,
           'parallel': parallel_output}
