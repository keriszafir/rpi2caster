# -*- coding: utf-8 -*-
"""Drivers for generic Monotype caster """
# Built-in time module
from time import time, sleep
# Custom exceptions module
from . import exceptions
# Default user interface
from .global_settings import USER_INTERFACE as UI
# Alphanumeric arrangement
from .constants import PIN_BASE, ALNUM_ARR


class MonotypeCaster(object):
    """Methods common for Caster classes, used for instantiating
    caster driver objects (whether real hardware or mockup for simulation)."""
    def __init__(self):
        self.name = 'Monotype composition caster (mockup)'
        self.is_perforator = False
        self.simulation_mode = False
        self.sensor = None
        self.output_driver = None
        self.stop = EmergencyStop()
        self.lock = False
        # Attach a pump
        self.pump = Pump()
        # Set default wedge positions
        self.current_0005 = '15'
        self.current_0075 = '15'

    def __enter__(self):
        """Lock the resource so that only one object can use it
        with context manager"""
        if self.lock:
            UI.display('Caster %s is already busy!' % self.name)
        else:
            # Set default wedge positions
            self.current_0005 = '15'
            self.current_0075 = '15'
            self.lock = True
            return self

    def get_parameters(self):
        """Gets a list of parameters"""
        data = [(self.name, 'Caster name'),
                (self.is_perforator, 'Is a perforator?')]
        # Collect data from I/O drivers
        data.append(self.sensor.get_parameters())
        data.append(self.stop.get_parameters())
        data.append(self.output_driver.get_parameters())
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
                self.activate_valves(signals)
                self.sensor.wait_for(new_state=False, timeout=timeout)
                self.deactivate_valves()
                # self._send_signals_to_caster(signals, cycle_timeout)
                # Successful ending - the combination has been cast
                return True
            except (exceptions.MachineStopped, KeyboardInterrupt, EOFError):
                # Machine stopped during casting - clean up and ask what to do
                pump_was_working = self.pump.is_working
                last_0005 = self.current_0005
                last_0075 = self.current_0075
                self.force_pump_stop()
                # Redirect flow by changing exception
                try:
                    stop_menu()
                except exceptions.ReturnToMenu:
                    # Punching: go to menu; casting: abort
                    if self.is_perforator:
                        raise
                    else:
                        raise exceptions.CastingAborted
                # Now we need to re-activate the pump if it was previously on
                # to cast something at all...
                if pump_was_working:
                    UI.display('Resuming pump action...')
                    self.process_signals(['N', 'J', '0005', 'S', last_0005])
                    self.process_signals(['N', 'K', '0075', 'S', last_0075])
                    UI.display('Pump action resumed.')

    def force_pump_stop(self):
        """Forces pump stop - won't end until it is turned off"""
        stop_combination = ['N', 'J', 'S', '0005']
        UI.display('Turning all valves off - just in case...')
        self.deactivate_valves()
        while self.pump.is_working:
            UI.display('The pump is still working - turning it off...')
            try:
                # Run a full machine cycle to turn the pump off
                self.sensor.wait_for(new_state=True, force_cycle=True)
                self.activate_valves(stop_combination)
                self.sensor.wait_for(new_state=False)
                self.deactivate_valves()
                UI.display('Pump is now off.')
                return True
            except (exceptions.MachineStopped, KeyboardInterrupt, EOFError):
                pass

    def activate_valves(self, signals):
        """If there are any signals, print them out"""
        UI.display('Combination: %s' % ' '.join(signals))
        if self.is_perforator and 'O15' not in signals:
            # Always activate O+15 for perforating
            signals.append('O15')
            UI.display('Punching mode - activating additional O15')
        elif not self.is_perforator:
            # Casters update the pump and wedge status and don't use O15
            self.pump.check_working(signals)
            self.get_wedge_positions(signals)
            try:
                signals.remove('O15')
                UI.display('Casting mode, O15 only - no signals sent.')
            except ValueError:
                pass
        # Activate the valves with O15 (punching) or no O15 (casting)
        self.output_driver.valves_on(signals)

    def deactivate_valves(self):
        """No need to do anything"""
        self.output_driver.valves_off()

    def get_wedge_positions(self, signals):
        """Gets current positions of 0005 and 0075 wedges"""
        # Check 0005
        if '0005' in signals or {'N', 'J'}.issubset(signals):
            pos_0005 = [x for x in range(15) if str(x) in signals]
            if pos_0005:
                # One or more signals detected
                self.current_0005 = str(min(pos_0005))
            else:
                # 0005 with no signal = wedge at 15
                self.current_0005 = '15'
        # Check 0075
        if '0075' in signals or {'N', 'K'}.issubset(signals):
            pos_0075 = [x for x in range(15) if str(x) in signals]
            if pos_0075:
                # One or more signals detected
                self.current_0075 = str(min(pos_0075))
            else:
                # 0005 with no signal = wedge at 15
                self.current_0075 = '15'

    def detect_rotation(self, max_cycles=3, max_time=30):
        """Detect machine cycles and alert if it's not working"""
        UI.display('Now checking if the machine is running...')
        while True:
            try:
                cycles = 0
                while cycles <= max_cycles:
                    # Run a new cycle
                    self.sensor.wait_for(new_state=True, timeout=max_time,
                                         force_cycle=True)
                    cycles += 1
                return True
            except (exceptions.MachineStopped,
                    KeyboardInterrupt, EOFError):
                stop_menu()

    def __exit__(self, *args):
        self.deactivate_valves()
        UI.debug_info('Caster no longer in use.')
        self.lock = False


class Pump(object):
    """Pump class for storing the pump working/non-working status."""
    def __init__(self):
        self.last_state = False
        self.is_working = False

    def check_working(self, signals):
        """Checks if pump is working based on signals in sequence"""
        # 0075 / NK is satisfactory to turn the pump on...
        if '0075' in signals or set(['N', 'K']).issubset(signals):
            self.is_working = False
            self.last_state = True
        # No 0075 / NK; then 0005 / NJ turns the pump off
        elif '0005' in signals or set(['N', 'J']).issubset(signals):
            self.is_working = False
            self.last_state = False
        else:
            self.is_working = self.last_state

    def status(self):
        """Displays info whether pump is working or not"""
        if self.is_working:
            return 'Pump is ON'
        else:
            return 'Pump is OFF'


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

    def wait_for(self, new_state, timeout=5, force_cycle=False):
        """Waits for a keypress to emulate machine cycle, unless user
        switches to auto mode, where all combinations are processed in batch"""
        status = {True: 'ON', False: 'OFF'}
        UI.display('The sensor is going %s' % status[new_state])
        if self.manual_mode or force_cycle:
            start_time = time()
            # Ask whether to cast or simulate machine stop
            prompt = ('[Enter] to continue, [S] to stop '
                      'or [A] to switch to automatic mode? ')
            answer = UI.enter_data_or_blank(prompt) or ' '
            if answer in 'aA':
                self.manual_mode = False
            elif answer in 'sS':
                raise exceptions.MachineStopped
            elif time() - start_time > timeout:
                UI.display('Timeout - you answered after %ds' % timeout)
                raise exceptions.MachineStopped
        else:
            sleep(0.1)


class PerforatorSensor(Sensor):
    """A special sensor class for perforators"""
    def __init__(self):
        Sensor.__init__(self)
        self.name = 'Timer-driven or manual advance for perforator'

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
                raise exceptions.MachineStopped
            elif time() - start_time > timeout:
                UI.display('Timeout - you answered after %ds' % timeout)
                raise exceptions.MachineStopped
        elif new_state:
            # Time needed for all punches to go down
            sleep(0.4)
        else:
            # Time needed for all punches to go up
            sleep(0.25)


class InputTestSensor(Sensor):
    """A keyboard-operated "sensor" for testing inputs.
    No automatic mode is supported."""
    def __init__(self):
        Sensor.__init__(self)
        self.name = 'Timer-driven or manual advance for perforator'

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
        data = [(self.name, 'Emergency stop button driver')]
        return data


class OutputDriver(object):
    """Mockup for a driver for 32 pneumatic outputs"""
    def __init__(self, pin_base=PIN_BASE, sig_arr=ALNUM_ARR):
        pins = [pin for pin in range(pin_base, pin_base + 32)]
        self.lock = False
        self.name = 'Mockup output driver for simulation'
        self.signals_arrangement = sig_arr.split(',')
        self.pin_numbers = dict(zip(self.signals_arrangement, pins))

    def __enter__(self):
        if not self.lock:
            self.lock = True
            return self

    def __exit__(self, *_, **__):
        self.lock = False

    def get_parameters(self):
        """Gets a list of parameters"""
        data = [(self.name, 'Output driver'),
                (self.signals_arrangement, 'Signals arrangement')]
        return data

    def one_on(self, sig):
        """Looks a signal up in arrangement and turns it on"""
        try:
            UI.debug_info(sig + ' on')
        except KeyError:
            raise exceptions.WrongConfiguration('Signal %s not defined!' % sig)

    def one_off(self, sig):
        """Looks a signal up in arrangement and turns it on"""
        try:
            UI.debug_info(sig + ' off')
        except KeyError:
            raise exceptions.WrongConfiguration('Signal %s not defined!' % sig)

    def valves_on(self, signals_list):
        """Turns on multiple valves"""
        for sig in signals_list:
            self.one_on(sig)

    def valves_off(self):
        """Turns off all the valves"""
        for sig in self.signals_arrangement:
            self.one_off(sig)


def stop_menu():
    """This allows us to choose whether we want to continue,
    return to menu or exit if the machine is stopped during casting.
    """
    def continue_casting():
        """Helper function - continue casting."""
        return True
    options = {'C': continue_casting,
               'M': exceptions.return_to_menu,
               'E': exceptions.exit_program}
    message = ('Machine is not running!\n'
               '[C]ontinue, return to [M]enu or [E]xit program? ')
    UI.simple_menu(message, options)()


# Hardware control modules
def sysfs_sensor():
    """Loads and instantiates the SysFS sensor"""
    from . import input_driver_sysfs
    return input_driver_sysfs.SysfsSensor()


def wiringpi_output_driver():
    """Loads and instantiates the wiringPi2 driver for MCP23017"""
    from . import output_driver_wiringpi
    return output_driver_wiringpi.MCP23017Interface()
