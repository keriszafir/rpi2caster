# -*- coding: utf-8 -*-
"""Caster object for either,  real or virtual Monotype composition caster"""
# Built-in time module
from time import time, sleep
from contextlib import suppress
# Custom exceptions module
from . import exceptions as e
# Constants module
from . import constants as c
from .ui import UIFactory
from .global_config import Config

UI = UIFactory()
CFG = Config()

# Constants for readability
AIR_ON = True
AIR_OFF = False


class MonotypeCaster(object):
    """Methods common for Caster classes, used for instantiating
    caster driver objects (whether real hardware or mockup for simulation)."""
    lock, pump_working = False, False

    def __init__(self):
        self.mode = CasterMode()

    def __enter__(self):
        """Lock the resource so that only one object can use it
        with context manager"""
        if self.lock:
            UI.display('Caster is already busy!')
        else:
            self.lock = True
            UI.pause('Entering the caster context...', min_verbosity=3)
            sensor, output = self.mode.get_casting_backend()
            self.sensor = sensor()
            self.output = output()
            with self.sensor, self.output:
                return self

    def __exit__(self, *_):
        UI.pause('Caster no longer in use.', min_verbosity=3)
        self.sensor = None
        self.output = None
        self.lock = False

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
        return self.sensor.parameters + self.output.parameters

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
                UI.display('Emergency stop!')
                if not self.mode.punching:
                    self.pump_stop()
                # Exception will be handled in session
                raise e.MachineStopped

    def pump_stop(self):
        """Forces pump stop - won't end until it is turned off"""
        def send_stop_signals():
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
            with suppress(e.MachineStopped, KeyboardInterrupt, EOFError):
                # Run two full sequences to be sure
                send_stop_signals()
                send_stop_signals()
                UI.display('Pump is now off.')
                self.pump_working = False


class SensorBase(object):
    """Mockup for a machine cycle sensor"""
    name = 'generic machine cycle sensor'
    lock, last_state, manual_mode = False, True, True

    def __enter__(self):
        if not self.lock:
            self.lock = True
            UI.pause('Using a %s for machine feedback' % self.name,
                     min_verbosity=2)
            return self

    def __exit__(self, *_):
        UI.pause('The %s is no longer in use' % self.name, min_verbosity=3)
        # Reset manual mode
        self.manual_mode = True
        self.lock = False

    @property
    def parameters(self):
        """Gets a list of parameters"""
        return [(self.name, 'Sensor driver'),
                (self.manual_mode, 'Manual mode')]

    def check_if_machine_is_working(self, exception=e.ReturnToMenu):
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
            except (e.MachineStopped, KeyboardInterrupt, EOFError):
                prompt = 'Machine is not running. Y to try again or N to exit?'
                if not UI.confirm(prompt, default=False):
                    raise exception

    def wait_for(self, new_state, timeout=30, time_on=0.1, time_off=0.1):
        """Waits for a keypress to emulate machine cycle, unless user
        switches to auto mode, where all combinations are processed in batch"""
        status = {True: 'ON', False: 'OFF'}
        UI.display('The sensor is going %s' % status[new_state],
                   min_verbosity=3)
        if self.manual_mode:
            start_time = time()
            # Ask whether to cast or simulate machine stop
            prompt = ('[A] to switch to automatic mode, [S] to stop\n'
                      'or leave blank to continue?')
            answer = UI.enter(prompt, blank_ok=True) or ' '
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


class SimulationSensor(SensorBase):
    """Simulate casting with no actual machine"""
    name = 'simulation - mockup casting interface'

    def check_if_machine_is_working(self, exception=e.ReturnToMenu):
        """Warn that this is just a simulation"""
        UI.display('Simulation mode - no machine is used.\n'
                   'This will emulate the actual casting sequence '
                   'as closely as possible.\n')
        return super().check_if_machine_is_working(exception)


class PunchingSensor(SensorBase):
    """A special sensor class for perforators"""
    name = 'timer-driven or manual advance for perforator'

    def check_if_machine_is_working(self, exception=e.ReturnToMenu):
        """Ask for user confirmation before punching"""
        try:
            UI.pause('\nRibbon punching: \n'
                     'Put the ribbon on the perforator and turn on the air.')
        except KeyboardInterrupt:
            raise exception

    def wait_for(self, new_state, timeout=30, time_on=0.25, time_off=0.4):
        """Calls simulation sensor's function, but with different timings"""
        if new_state:
            super().wait_for(new_state, timeout, time_on, time_off)
        else:
            sleep(time_off)


class TestSensor(SensorBase):
    """A keyboard-operated "sensor" for testing inputs.
    No automatic mode is supported."""
    name = 'manual advance for testing'

    def wait_for(self, new_state, *_):
        """Waits for keypress before turning the line off"""
        if not new_state:
            UI.pause('Next combination?')

    def check_if_machine_is_working(self, exception=e.ReturnToMenu):
        """Do nothing here"""
        try:
            return True
        except KeyboardInterrupt:
            raise exception


class OutputBase(object):
    """Mockup for a driver for 32 pneumatic outputs"""
    name = 'generic output driver'
    lock = False

    def __init__(self,
                 signals_arrangement=CFG.get_option('signals_arrangement')):
        self.signals_arrangement = signals_arrangement

    def __del__(self):
        UI.pause('Deleting the %s' % self.name, min_verbosity=3)

    def __enter__(self):
        if not self.lock:
            self.lock = True
            UI.pause('Using the %s for sending signals...' % self.name,
                     min_verbosity=2)
            return self

    def __exit__(self, *_):
        self.valves_off()
        UI.pause('Driver for %s no longer in use.' % self.name,
                 min_verbosity=3)
        self.lock = False

    @property
    def parameters(self):
        """Gets a list of parameters"""
        return [(self.name, 'Output driver'),
                (' '.join(self.signals_arrangement), 'Signals arrangement')]

    @staticmethod
    def one_on(sig):
        """Looks a signal up in arrangement and turns it on"""
        try:
            UI.display(sig + ' on', min_verbosity=2)
        except KeyError:
            raise e.WrongConfiguration('Signal %s not defined!' % sig)

    @staticmethod
    def one_off(sig):
        """Looks a signal up in arrangement and turns it on"""
        try:
            UI.display(sig + ' off', min_verbosity=2)
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


class SimulationOutput(OutputBase):
    """Simulation output driver - don't control any hardware"""
    name = 'simulation - mockup casting interface'


class CasterMode(object):
    """Session mode: casting / simulation / perforation"""
    row_16_addressing = None

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
        return self.__dict__.get('_calibration', False)

    @calibration.setter
    def calibration(self, value):
        """Set the machine calibration mode"""
        self.__dict__['_calibration'] = value

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
        return self.__dict__.get('_punching', False)

    @punching.setter
    def punching(self, value):
        """Set the punching mode"""
        self.__dict__['_punching'] = value

    @property
    def testing(self):
        """Testing mode"""
        return self.__dict__.get('_testing', False)

    @testing.setter
    def testing(self, value):
        """Set the testing mode"""
        self.__dict__['_testing'] = value

    @property
    def casting(self):
        """Check if the machine is casting"""
        return not self.punching and not self.testing and not self.calibration

    @property
    def needs_row_16(self):
        """Check if row 16 is currently needed."""
        return self.__dict__.get('_needs_row_16') or False

    @needs_row_16.setter
    def needs_row_16(self, value):
        """Choose the diecase row 16 addressing mode, if needed.

        Row 16 is needed and currently off:
        Ask which row 16 addressing system the user's machine has, if any.

        Row 16 is not needed and currently on:
        Tell the user to turn off the attachment.

        Row 16 is not needed and is off, or is needed and is on: do nothing.
        """
        def choose_row16_addressing():
            """Let user decide which way to address row 16"""
            prm = ('Your ribbon contains codes from the 16th row.\n'
                   'It is supported by special attachments for the machine.\n'
                   'Which mode does your caster use: HMN, KMN, Unit-Shift?\n\n'
                   'If off - characters from row 15 will be cast instead.\n\n'
                   'Your choice: [U]nit-Shift, [H]MN, [K]MN, blank = off?: ')
            options = {'U': c.UNIT_SHIFT, 'H': c.HMN, 'K': c.KMN, '': c.OFF}
            self.row_16_addressing = UI.simple_menu(prm, options)

        names = {c.HMN: 'HMN', c.KMN: 'KMN', c.UNIT_SHIFT: 'unit-shift'}
        attachment_name = names.get(self.row_16_addressing) or ''

        is_required = bool(value)
        is_active = bool(self.row_16_addressing)
        self.__dict__['_needs_row_16'] = is_required
        if is_required and not is_active:
            choose_row16_addressing()
        elif is_active and not is_required:
            UI.pause('\nTurn off the %s attachment.\n' % attachment_name)
            self.row_16_addressing = c.OFF
        elif is_required and is_active:
            UI.display('The %s attachment is turned on - OK...'
                       % attachment_name)

    def get_casting_backend(self):
        """Use the interface factory method to determine sensor and output"""
        return interface_factory(self)


def interface_factory(mode,
                      default_sensor=CFG.get_option('sensor'),
                      default_output=CFG.get_option('output')):
    """Interface factory combines the sensor and output modules into
    an Interface class. Returns an instance of this class."""
    def sysfs_sensor():
        """Gets hardware sensor - prevents import loop"""
        from .input_driver_sysfs import SysfsSensor
        return SysfsSensor()

    def rpigpio_sensor():
        """Gets hardware sensor with RPi.GPIO backend"""
        from .input_driver_rpi_gpio import RPiGPIOSensor
        return RPiGPIOSensor()

    def parallel_sensor():
        """A parallel port valve control for John Cornelisse's
        old interface built by Symbiosys"""
        from .io_driver_parallel import ParallelInterface
        try:
            return ParallelInterface()
        except (FileNotFoundError, IOError, OSError):
            UI.pause('ERROR: Cannot access the parallel port!\n'
                     'Check your hardware and OS configuration...\n'
                     'Using simulation interface instead.')
            return (punching_sensor() if mode.punching
                    else test_sensor() if mode.testing
                    else simulation_sensor())

    def parallel_output():
        """A parallel port valve control for John Cornelisse's
        old interface built by Symbiosys"""
        from .io_driver_parallel import ParallelInterface
        try:
            return ParallelInterface()
        except (FileNotFoundError, IOError, OSError):
            return simulation_output()

    def test_sensor():
        """Sensor used for testing - manual advance ONLY"""
        mode.testing = True
        return TestSensor()

    def simulation_sensor():
        """Sensor used for simulation - manual or automatic advance,
        can simulate machine stop"""
        mode.simulation = True
        return SimulationSensor()

    def punching_sensor():
        """Manual or time-driven advance, no machine stop detection"""
        mode.punching = True
        return PunchingSensor()

    def wiringpi_output():
        """Gets hardware output - prevents import loop"""
        from .output_driver_wiringpi import WiringPiOutputDriver
        return WiringPiOutputDriver()

    def simulation_output():
        """Simulate valves instead of using real hardware"""
        mode.simulation = True
        return SimulationOutput()

    def get_classes():
        """Get the sensor and output drivers"""
        sensor_names = {'simulation': simulation_sensor,
                        'sysfs': sysfs_sensor,
                        'rpi.gpio': rpigpio_sensor,
                        'parallel': parallel_sensor,
                        'testing': test_sensor,
                        'punching': punching_sensor}
        output_names = {'simulation': simulation_output,
                        'wiringpi': wiringpi_output,
                        'parallel': parallel_output}
        # First get the backend from configuration
        backend = [default_sensor, default_output]
        # Use simulation mode if set in configuration
        simulation = True if 'simulation' in backend else mode.simulation
        # If we don't know whether simulation is on or off - ask
        if simulation is None and CFG.get_option('choose_backend'):
            prompt = 'Use real caster? (no = simulation mode)'
            simulation = not UI.confirm(prompt, True)
        # Use parallel interface
        parallel = True if 'parallel' in backend and not simulation else False
        punching = True if 'punching' in backend else mode.punching
        # Override the backend for parallel and simulation
        # Use parallel sensor above all else
        # Testing and punching sensor overrides simulation sensor
        sensor = ('parallel' if parallel
                  else 'testing' if mode.testing
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

    return get_classes()
