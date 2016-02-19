# -*- coding: utf-8 -*-
"""Drivers for generic Monotype caster """
# Built-in time module
from time import time, sleep
# wiringPi2 backend for MCP23017 setup
try:
    import wiringpi2
except ImportError:
    pass
# Custom exceptions module
from . import exceptions as e
# Constants module
from . import constants as c
# Default user interface
from .global_settings import USER_INTERFACE as UI
# Configuration parsing
from . import cfg_parser
try:
    SIGNALS = (str(cfg_parser.get_config('SignalsArrangements',
                                         'signals_arrangement')).upper())
except e.NotConfigured:
    SIGNALS = c.ALNUM_ARR


class MonotypeCaster(object):
    """Methods common for Caster classes, used for instantiating
    caster driver objects (whether real hardware or mockup for simulation)."""
    def __init__(self):
        self.name = 'Monotype composition caster (mockup)'
        self.sensor = Sensor()
        self.output = OutputDriver()
        self.stop = EmergencyStop()
        self.lock = False
        # Attach a pump
        self.pump = Pump(self)

    def __enter__(self):
        """Lock the resource so that only one object can use it
        with context manager"""
        if self.lock:
            UI.display('Caster %s is already busy!' % self.name)
        else:
            # Set default wedge positions
            self.lock = True
            return self

    def get_parameters(self):
        """Gets a list of parameters"""
        data = [(self.name, 'Caster name')]
        # Collect data from I/O drivers
        data.extend(self.sensor.get_parameters())
        data.extend(self.stop.get_parameters())
        data.extend(self.output.get_parameters())
        return data

    def process_signals(self, signals, timeout=5):
        """process_signals(signals, timeout):

        Checks for the machine's rotation, sends the signals (activates
        solenoid valves) after the caster is in the "air bar down" position.

        If no machine rotation is detected (sensor input doesn't change
        its state) during cycle_timeout, calls a function to ask user
        what to do (can be useful for resuming casting after manually
        stopping the machine for a short time - not recommended as the
        mould cools down and type quality can deteriorate).

        If the operator decides to go on with casting, the aborted sequence
        will be re-cast so as to avoid missing characters in the composition.

        Safety measure: this function will call "emergency_cleanup" routine
        whenever the operator decides to go back to menu or exit program
        after the machine stops rotating during casting. This is to ensure
        that the pump will not stay on afterwards, leading to lead squirts
        or any other unwanted effects.

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
        while True:
            # Escape this only by returning True on success,
            # or raising exceptions.CastingAborted, exceptions.ExitProgram
            # (which will be handled by the methods of the Casting class)
            try:
                # Casting cycle
                # (sensor on - valves on - sensor off - valves off)
                self.sensor.wait_for(new_state=True, timeout=timeout)
                self.output.valves_on(signals)
                self.sensor.wait_for(new_state=False, timeout=timeout)
                self.output.valves_off()
                # self._send_signals_to_caster(signals, cycle_timeout)
                # Successful ending - the combination has been cast
                return True
            except (e.MachineStopped, KeyboardInterrupt, EOFError):
                # Machine stopped during casting - clean up and ask what to do
                self.pump.stop()
                stop_menu()
                # If user continues, pump will be restarted if it was working
                self.pump.start()

    def __exit__(self, *_):
        UI.debug_info('Caster no longer in use.')
        self.lock = False


class Pump(object):
    """Pump class for storing the pump working/non-working status."""
    def __init__(self, caster):
        self.caster = caster
        self.is_working = self.was_working = False
        # Remember wedge positions on resume
        self.current_0005 = self.last_0005 = '15'
        self.current_0075 = self.last_0075 = '15'

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def stop(self):
        """Forces pump stop - won't end until it is turned off"""
        UI.display('Turning all valves off - just in case...')
        self.caster.output.valves_off()
        self.last_0075, self.last_0005 = self.current_0075, self.current_0005
        self.was_working = self.is_working
        while self.is_working:
            UI.display('The pump is still working - turning it off...')
            try:
                # Run a full machine cycle to turn the pump off
                self.caster.sensor.wait_for(new_state=True, force_cycle=True)
                self.caster.output.valves_on(c.PUMP_STOP)
                self.caster.sensor.wait_for(new_state=False)
                self.caster.output.valves_off()
                UI.display('Pump is now off.')
                return True
            except (e.MachineStopped, KeyboardInterrupt, EOFError):
                pass

    def start(self):
        """Starts the pump with given wedge positions"""
        if self.was_working:
            UI.display('Resuming pump action...')
            # Set the wedge positions from before stop
            self.caster.process_signals(c.PUMP_STOP + [self.last_0005])
            self.caster.process_signals(c.PUMP_START + [self.last_0075])
            UI.display('Pump action resumed.')


class Sensor(object):
    """Mockup for a machine cycle sensor"""
    def __init__(self):
        self.lock = False
        self.manual_mode = True
        self.last_state = False
        self.name = 'Mockup machine cycle sensor'

    def __enter__(self):
        if not self.lock:
            self.lock = True
            return self

    def __exit__(self, *_):
        self.lock = False

    def get_parameters(self):
        """Gets a list of parameters"""
        data = [(self.name, 'Sensor driver'),
                (self.manual_mode, 'Manual mode')]
        return data

    def detect_rotation(self):
        """Detect machine cycles and alert if it's not working"""
        UI.display('Now checking if the machine is running...')
        cycles = 3
        while True:
            try:
                while cycles:
                    # Run a new cycle
                    UI.display(cycles)
                    self.wait_for(new_state=True, timeout=30, force_cycle=True)
                    cycles -= 1
                return True
            except (e.MachineStopped,
                    KeyboardInterrupt, EOFError):
                stop_menu()

    def wait_for(self, new_state, timeout=5, force_cycle=False):
        """Waits for a keypress to emulate machine cycle, unless user
        switches to auto mode, where all combinations are processed in batch"""
        status = {True: 'ON', False: 'OFF'}
        UI.display('The sensor is going %s' % status[new_state])
        if self.manual_mode:
            start_time = time()
            # Ask whether to cast or simulate machine stop
            prompt = ('[Enter] to continue, [S] to stop '
                      'or [A] to switch to automatic mode? ')
            answer = UI.enter_data_or_blank(prompt) or ' '
            if answer in 'aA':
                self.manual_mode = False
            elif answer in 'sS':
                raise e.MachineStopped
            elif time() - start_time > timeout:
                UI.display('Timeout - you answered after %ds' % timeout)
                raise e.MachineStopped
        else:
            sleep(0.1)


class PunchingSensor(Sensor):
    """A special sensor class for perforators"""
    def __init__(self):
        super().__init__()
        self.name = 'Timer-driven or manual advance for perforator'

    def detect_rotation(self):
        """Ask for user confirmation before punching"""
        UI.confirm('\nRibbon punching: \n'
                   'Put the ribbon on the perforator and turn on the air.')

    def wait_for(self, new_state, timeout=30, force_cycle=False):
        """Waits for user keypress before toggling the output state.
        After switching to auto mode on/off timings are fixed and the process
        continues without user intervention."""
        status = {True: 'UP', False: 'DOWN'}
        UI.display('Punches going %s' % status[new_state])
        if self.manual_mode or force_cycle:
            start_time = time()
            # Ask whether to cast or simulate machine stop
            prompt = ('[Enter] to continue, [S] to stop '
                      'or [A] to switch to automatic mode? ')
            answer = UI.enter_data_or_blank(prompt) or ' '
            if answer in 'aA':
                self.manual_mode = False
            elif answer in 'sS':
                raise e.MachineStopped
            elif time() - start_time > timeout:
                UI.display('Timeout - you answered after %ds' % timeout)
                raise e.MachineStopped
        elif new_state:
            # Time needed for all punches to go down
            sleep(0.4)
        else:
            # Time needed for all punches to go up
            sleep(0.25)


class TestSensor(Sensor):
    """A keyboard-operated "sensor" for testing inputs.
    No automatic mode is supported."""
    def __init__(self):
        super().__init__()
        self.name = 'Timer-driven or manual advance for perforator'

    def detect_rotation(self):
        """Don't hold the process"""
        pass

    def wait_for(self, new_state, *_, **__):
        """Waits for keypress before turning the line off"""
        if not new_state:
            UI.confirm('Next combination?')


class EmergencyStop(object):
    """Mockup for an emergency stop button"""
    def __init__(self, gpio=None):
        self.gpio = gpio
        self.name = 'Mockup emergency stop button'
        self.signals, self.value_file, self.edge_file = None, None, None

    def get_parameters(self):
        """Gets a list of parameters"""
        return [(self.name, 'Emergency stop button driver')]


class OutputDriver(object):
    """Mockup for a driver for 32 pneumatic outputs"""
    def __init__(self, pin_base=c.PIN_BASE, sig_arr=SIGNALS):
        pins = [pin for pin in range(pin_base, pin_base + 32)]
        self.lock = False
        self.name = 'Mockup output driver for simulation'
        self.signals_arrangement = [str(x).upper() for x in sig_arr.split(',')]
        self.pin_numbers = dict(zip(self.signals_arrangement, pins))

    def __enter__(self):
        if not self.lock:
            self.lock = True
            return self

    def __exit__(self, *_):
        self.valves_off()
        self.lock = False

    def get_parameters(self):
        """Gets a list of parameters"""
        data = [(self.name, 'Output driver'),
                (' '.join(self.signals_arrangement), 'Signals arrangement')]
        return data

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


class WiringPi2OutputDriver(OutputDriver):
    """A 32-channel control interface based on two MCP23017 chips,
    using wiringPi2 library"""
    def __init__(self, mcp0_address=c.MCP0, mcp1_address=c.MCP1,
                 pin_base=c.PIN_BASE, sig_arr=SIGNALS):
        super().__init__(pin_base=pin_base, sig_arr=sig_arr)
        self.name = 'MCP23017 driver using wiringPi2-Python library'
        UI.debug_info('Creating a hardware sensor')
        # Set up an output interface on two MCP23017 chips
        wiringpi2.mcp23017Setup(pin_base, mcp0_address)
        wiringpi2.mcp23017Setup(pin_base + 16, mcp1_address)
        # Set all I/O lines on MCP23017s as outputs - mode=1
        for pin in self.pin_numbers.values():
            wiringpi2.pinMode(pin, 1)
        UI.debug_info('Successfully created a hardware sensor')

    def __del__(self):
        UI.debug_confirm('Deleting the hardware sensor')

    def one_on(self, sig):
        """Looks a signal up in arrangement and turns it on"""
        try:
            wiringpi2.digitalWrite(self.pin_numbers[sig], 1)
        except KeyError:
            raise e.WrongConfiguration('Signal %s not defined!' % sig)

    def one_off(self, sig):
        """Looks a signal up in arrangement and turns it off"""
        try:
            wiringpi2.digitalWrite(self.pin_numbers[sig], 0)
        except KeyError:
            msg = ('Signal %s not defined! Signals arrangement: %s\n'
                   % (sig, self.signals_arrangement))
            raise e.WrongConfiguration(msg)


def stop_menu():
    """This allows us to choose whether we want to continue,
    return to menu or exit if the machine is stopped during casting.
    """
    def continue_casting():
        """Helper function - continue casting."""
        return True
    options = {'C': continue_casting,
               'A': e.abort_casting,
               'E': e.exit_program}
    message = ('Machine is not running!\n'
               '[C]ontinue, [A]bort or [E]xit program? ')
    UI.simple_menu(message, options)()


class Mode(object):
    """Session mode: casting / simulation / perforation"""
    def __init__(self):
        self.simulation = False
        self.punching = False
        self.testing = False

    @property
    def simulation(self):
        """Simulation mode"""
        return self.__dict__['simulation'] and True or False

    @simulation.setter
    def simulation(self, value):
        """Set the simulation mode"""
        self.__dict__['simulation'] = value

    @property
    def punching(self):
        """Punching mode"""
        return self.__dict__['punching'] and True or False

    @punching.setter
    def punching(self, value):
        """Set the punching mode"""
        self.__dict__['punching'] = value

    @property
    def testing(self):
        """Testing mode"""
        return self.__dict__['testing'] and True or False

    @testing.setter
    def testing(self, value):
        """Set the testing mode"""
        self.__dict__['testing'] = value

    @property
    def casting(self):
        """Check if the machine is casting"""
        return not self.punching and not self.testing

    @property
    def sensor(self):
        """Chooses a proper sensor"""
        sensor = (self.testing and TestSensor or
                  self.punching and PunchingSensor or
                  self.simulation and SimulationSensor or
                  HardwareSensor)
        return sensor

    @property
    def output(self):
        """Chooses a simulation or hardware output driver"""
        output = (self.simulation and SimulationOutput or
                  HardwareOutput)
        return output


# Hardware control modules
def sysfs_sensor():
    """Loads and instantiates the SysFS sensor"""
    from . import input_driver_sysfs
    return input_driver_sysfs.SysfsSensor


SimulationSensor = Sensor
SimulationOutput = OutputDriver
HardwareOutput = WiringPi2OutputDriver
HardwareSensor = sysfs_sensor()
