"""
Monotype:

This module contains low- and mid-level caster control routines for
a physical Monotype composition caster, linked via pneumatic valves
and MCP23017 IC's to the Raspberry Pi.
"""
import io
# Essential for polling the sensor for state change:
import select
# Built-in time library
import time
# Custom exceptions
from rpi2caster import exceptions
# Configuration parser functions
from rpi2caster import cfg_parser
# Default user interface
from rpi2caster import global_settings
UI = global_settings.USER_INTERFACE
# WiringPi2 Python bindings: essential for controlling the MCP23017!
try:
    import wiringpi2 as wiringpi
except ImportError:
    raise exceptions.MissingDependency('You must install wiringpi2!')


class Monotype(object):
    """Monotype(name):

    A class which stores all hardware-layer methods, related to caster control.
    This class requires a caster name, and a database object.
    """

    def __init__(self, name=''):
        """Creates a caster object for a given caster name
        """
        self.name = name or global_settings.CASTER_NAME
        self.is_perforator = None
        self.lock = None
        self.sensor_gpio_edge_file = None
        self.sensor_gpio_value_file = None
        self.emerg_gpio_edge_file = None
        self.emerg_gpio_value_file = None
        # Configure the caster
        self.interface_pin_number = self.caster_setup()

    def __enter__(self):
        """Run the setup when entering the context:
        """
        UI.debug_info('Entering caster/interface context...')
        if self.lock:
            UI.display('Caster %s is already busy!' % self.name)
        else:
            self.lock = True
            return self

    def caster_setup(self):
        """Setup routine:

        Sets up initial default parameters for caster & interface:
        caster - "Monotype" (if no name is given),
        interface ID 0,
        unit-adding disabled,
        diecase format 15x17.
        """
        def configure_sysfs_interface(gpio):
            """configure_sysfs_interface(gpio):

            Sets up the sysfs interface for reading events from GPIO
            (general purpose input/output). Checks if path/file is readable.
            Returns the value and edge filenames for this GPIO.
            """
            # Set up an input polling file for machine cycle sensor:
            gpio_sysfs_path = '/sys/class/gpio/gpio%s/' % gpio
            gpio_value_file = gpio_sysfs_path + 'value'
            gpio_edge_file = gpio_sysfs_path + 'edge'
            # Check if the GPIO has been configured - file is readable:
            try:
                with io.open(gpio_value_file, 'r'):
                    pass
                # Ensure that the interrupts are generated for sensor GPIO
                # for both rising and falling edge:
                with io.open(gpio_edge_file, 'r') as edge_file:
                    if 'both' not in edge_file.read():
                        UI.display('%s: file does not exist, cannot be read, '
                                   'or the interrupt on GPIO %i is not set '
                                   'to "both". Check the system configuration.'
                                   % (gpio_edge_file, gpio))
            except (IOError, FileNotFoundError):
                UI.display('%s : file does not exist or cannot be read. '
                           'You must export the GPIO no %s as input first!'
                           % (gpio_value_file, gpio))
            else:
                return (gpio_value_file, gpio_edge_file)

        # Configure the caster settings
        try:
            caster_settings = cfg_parser.get_caster_settings(self.name)
            (self.is_perforator, interface_id) = caster_settings
        except exceptions.NotConfigured:
            # Cannot read config? Use defaults:
            UI.display('Using hardcoded defaults for caster settings...')
            self.is_perforator = False
            interface_id = 0

        # Now configure interface outputs
        try:
            out_settings = cfg_parser.get_output_settings(interface_id)
            (mcp0_address, mcp1_address,
             pin_base, signals_arrangement) = out_settings
        except exceptions.NotConfigured:
            # Cannot read config? Use defaults:
            UI.display('Using hardcoded defaults for interface outputs...')
            mcp0_address = 0x20
            mcp1_address = 0x21
            pin_base = 65
            signals_arrangement = ('1,2,3,4,5,6,7,8,9,10,11,12,13,14,0005,'
                                   '0075,A,B,C,D,E,F,G,H,I,J,K,L,M,N,S,O15')
        # Setup the wiringPi MCP23017 chips for valve outputs
        wiringpi.mcp23017Setup(pin_base, mcp0_address)
        wiringpi.mcp23017Setup(pin_base + 16, mcp1_address)
        pins = [pin for pin in range(pin_base, pin_base + 32)]
        # Set all I/O lines on MCP23017s as outputs - mode=1
        for pin in pins:
            wiringpi.pinMode(pin, 1)

        # When debugging, display all caster info:
        info = ['Using caster name: ' + self.name,
                'Is a perforator? ' + str(self.is_perforator),
                'Interface ID: ' + str(interface_id),
                '1st MCP23017 I2C address: ' + hex(mcp0_address),
                '2nd MCP23017 I2C address: ' + hex(mcp1_address),
                'MCP23017 pin base for GPIO numbering: ' + str(pin_base),
                'Signals arrangement: ' + signals_arrangement]
        # Configure inputs for casters - perforators don't need them
        if not self.is_perforator:
            try:
                (emergency_stop_gpio,
                 sensor_gpio) = cfg_parser.get_input_settings(interface_id)
            except exceptions.NotConfigured:
                # Cannot read config? Use defaults:
                UI.display('Using hardcoded defaults for interface inputs...')
                emergency_stop_gpio = 24
                sensor_gpio = 17
            # Set up a sysfs interface for machine cycle sensor:
            sensor = configure_sysfs_interface(sensor_gpio)
            (self.sensor_gpio_value_file, self.sensor_gpio_edge_file) = sensor
            # Now the same for the emergency stop button input:
            emerg = configure_sysfs_interface(emergency_stop_gpio)
            (self.emerg_gpio_value_file, self.emerg_gpio_edge_file) = emerg
            # Display this info only for casters and not perforators:
            info.append('Emergency stop GPIO: ' + str(emergency_stop_gpio))
            info.append('Sensor GPIO: ' + str(sensor_gpio))

        # Iterate over the collected data and print the output
        for parameter in info:
            UI.debug_info(parameter)
        # Wait for user confirmation if in debug mode
        UI.debug_enter_data('Caster configured. [Enter] to continue... ')
        # Assign wiringPi pin numbers on MCP23017s to the Monotype
        # control signals. Return the result.
        return dict(zip(signals_arrangement.split(','), pins))

    def process_signals(self, signals, cycle_timeout=5):
        """process_signals(signals, cycle_timeout):

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
                self._send_signals_to_caster(signals, cycle_timeout)
            except exceptions.MachineStopped:
                # Machine stopped during casting - ask what to do
                self._stop_menu()
            else:
                # Successful ending - the combination has been cast
                return True

    def detect_rotation(self):
        """detect_rotation():

        Checks if the machine is running by counting pulses on a sensor
        input. One pass of a while loop is a single cycle. If cycles_max
        value is exceeded in a time <= time_max, the program assumes that
        the caster is rotating and it can start controlling the machine.
        """
        # Let's count up to 3 cycles, max 30s before stop menu is called
        cycles_max = 3
        time_max = 30
        # Reset the cycle counter and input state on each iteration
        cycles = 0
        prev_state = False
        while cycles <= cycles_max:
            # Keep checking until timeout or max cycles reached
            with io.open(self.sensor_gpio_value_file, 'r') as gpiostate:
                sensor_signals = select.epoll()
                sensor_signals.register(gpiostate, select.POLLPRI)
                events = sensor_signals.poll(time_max)
                # Check if the sensor changes state at all
                if events:
                    gpiostate.seek(0)
                    sensor_state = int(gpiostate.read())
                    # Increment the number of passed machine cycles
                    if sensor_state and not prev_state:
                        cycles += 1
                    prev_state = sensor_state
                else:
                    # Timeout with no signals = go to stop menu
                    self._stop_menu(casting=False)
        # Max cycles exceeded = machine is running
        return True

    def _send_signals_to_caster(self, signals, timeout):
        """_send_signals_to_caster:

        Sends a combination of signals passed in function's arguments
        to the caster. This function also checks if the machine cycle
        sensor changes its state, and decides whether it's an "air on"
        phase (turn on the valves) or "air off" phase (turn off the valves,
        end function, return True to signal the success).
        If no signals are detected within a given timeout - returns False
        (to signal the casting failure).
        """
        with io.open(self.sensor_gpio_value_file, 'r') as gpiostate:
            sensor_signals = select.epoll()
            sensor_signals.register(gpiostate, select.POLLPRI)
            prev_state = 0
            while True:
                # Polling the interrupt file
                events = sensor_signals.poll(timeout)
                if events:
                    # Normal control flow when the machine is working
                    # (cycle sensor generates events)
                    gpiostate.seek(0)
                    sensor_state = int(gpiostate.read())
                    if sensor_state == 1 and prev_state == 0:
                        # Now, the air bar on paper tower would go down -
                        # we got signal from sensor to let the air in
                        self.activate_valves(signals)
                        prev_state = 1
                    elif sensor_state == 0 and prev_state == 1:
                        # Air bar on paper tower goes back up -
                        # end of "air in" phase, turn off the valves
                        self.deactivate_valves()
                        prev_state = 0
                        # Signals sent to the caster - successful ending
                        return True
                else:
                    # Timeout with no signals - failed ending
                    raise exceptions.MachineStopped

    def _stop_menu(self, casting=True):
        """_stop_menu:

        This allows us to choose whether we want to continue,
        return to menu or exit if the machine is stopped during casting.
        """
        def continue_casting():
            """Helper function - continue casting."""
            return True

        def with_cleanup_return_to_menu():
            """with_cleanup_return_to_menu

            Aborts casting. Makes sure the pump is turned off.
            Raise an exception to be caught by higher-level functions
            from the Casting class
            """
            self._emergency_cleanup()
            raise exceptions.CastingAborted

        def with_cleanup_exit_program():
            """with_cleanup_exit_program

            Helper function - throws an exception to exit the program.
            Also makes sure the pump is turned off."""
            self._emergency_cleanup()
            raise exceptions.ExitProgram
        # End of subroutine definitions
        # Now, a little menu...
        if casting:
            # This happens when the caster is already casting,
            # and stops running.
            options = {'C': continue_casting,
                       'M': with_cleanup_return_to_menu,
                       'E': with_cleanup_exit_program}
            message = ('Machine has stopped running! Check what happened.\n'
                       '[C]ontinue, return to [M]enu or [E]xit program? ')
        else:
            # This happens if the caster is not yet casting
            # No need to do cleanup; change description a bit
            options = {'C': continue_casting,
                       'M': exceptions.return_to_menu,
                       'E': exceptions.exit_program}
            message = ('Machine not running - you need to start it first.\n'
                       '[C]ontinue, return to [M]enu or [E]xit program? ')
        UI.simple_menu(message, options)()

    def _emergency_cleanup(self):
        """emergency_cleanup:

        If the machine is stopped, we need to turn the pump off and then
        turn all the lines off. Otherwise, the machine will keep pumping
        while it shouldnot (e.g. after a splash).

        The program will hold execution until the operator clears
        the situation, it needs turning the machine at least one
        full revolution. The program MUST turn the pump off to move on.
        """
        pump_off = False
        stop_signal = ('N', 'J', '0005')
        UI.display('Stopping the pump...')
        while not pump_off:
            try:
                # Try stopping the pump until we succeed!
                # Keep calling _send_signals_to_caster until it returns True
                # (the machine receives and processes the pump stop signal)
                pump_off = self._send_signals_to_caster(stop_signal, 60)
            except exceptions.MachineStopped:
                # Loop over
                pass
        UI.display('Pump stopped. All valves off...')
        self.deactivate_valves()
        time.sleep(1)
        return True

    def activate_valves(self, signals):
        """activate_valves(signals):

        Activates the solenoid valves connected with interface's outputs,
        as specified in the "signals" parameter (tuple or list).
        The input array "signals" contains strings, either
        lowercase (a, b, g, s...) or uppercase (A, B, G, S...).
        Do nothing if the function receives an empty sequence, which will
        occur if we cast with the matrix found at position O15.
        """
        pins = [self.interface_pin_number[sig] for sig in signals]
        for pin in pins:
            wiringpi.digitalWrite(pin, 1)

    def deactivate_valves(self):
        """deactivate_valves():

        Turn all valves off after casting/punching any character.
        Call this function to avoid outputs staying turned on if something
        goes wrong, esp. in case of abnormal program termination.
        """
        for pin in self.interface_pin_number.values():
            wiringpi.digitalWrite(pin, 0)

    def __exit__(self, *args):
        """On exit, do the cleanup:
        """
        UI.debug_info('Exiting caster/interface context.')
        self.lock = False
