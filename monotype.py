# -*- coding: utf-8 -*-
"""
Monotype:

This module contains low- and mid-level caster control routines for
a physical Monotype composition caster, linked via pneumatic valves
and MCP23017 IC's to the Raspberry Pi.
"""
# Essential for polling the sensor for state change:
import select
# Built-in time library
import time
# Custom exceptions
import newexceptions
# User interface
import text_ui as ui
# Configuration parser functions
import cfg_parser
# WiringPi2 Python bindings: essential for controlling the MCP23017!
try:
    import wiringpi2 as wiringpi
except ImportError:
    print 'Missing dependency: wiringPi2 Python bindings: wiringpi2-python'
    print 'Caster control will not work!'
# Set up a default user interface object:
# Instantiate a default text user interface


class Monotype(object):
    """Monotype(name):

    A class which stores all hardware-layer methods, related to caster control.
    This class requires a caster name, and a database object.
    """

    def __init__(self, name='Monotype'):
        """Creates a caster object for a given caster name
        """
        self.name = name
        self.is_perforator = None
        self.interface_id = None
        self.unit_adding = None
        self.diecase_system = None
        self.emergency_gpio = None
        self.sensor_gpio = None
        self.mcp0_address = None
        self.mcp1_address = None
        self.pin_base = None
        self.signals_arrangement = None
        self.lock = None
        self.sensor_gpio_edge_file = None
        self.sensor_gpio_value_file = None
        self.interface_pin_number = None

        # Configure the caster now
        self.configured = False
        self.caster_setup()

    def __enter__(self):
        """Run the setup when entering the context:
        """
        ui.debug_info('Entering caster/interface context...')
        if self.lock:
            ui.display('Caster %s is already busy!' % self.name)
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
        # Next, this method reads caster data from conffile and sets up
        # instance attributes for the caster.
        # In case there is no data, the function will run on default settings.
        self.get_caster_settings()
        # The same for the interface settings:
        self.get_interface_settings()
        # When debugging, display all caster info:
        output = {'Using caster name: ' : self.name,
                  'Is a perforator? ' : self.is_perforator,
                  'Interface ID: ' : self.interface_id,
                  '1st MCP23017 I2C address: ' : self.mcp0_address,
                  '2nd MCP23017 I2C address: ' : self.mcp1_address,
                  'MCP23017 pin base for GPIO numbering: ' : self.pin_base,
                  'Signals arrangement: ' : self.signals_arrangement}
        # Display this info only for casters and not perforators:
        if not self.is_perforator:
            output['Emergency button GPIO: '] = self.emergency_gpio
            output['Sensor GPIO: '] = self.sensor_gpio
            output['Diecase system: '] = self.diecase_system
            output['Unit adding: '] = self.unit_adding
        # Iterate over the dict and print the output
        for parameter in output:
            ui.debug_info(parameter, output[parameter])
        # Info displayed. Wait for user to read it and continue...
        prompt = '[Enter] to continue...'
        ui.debug_enter_data(prompt)
        # Input configuration for sensor and emergency stop button
        # This is done only for a caster interface:
        if not self.is_perforator:
        # Set up an input for machine cycle sensor:
            gpio_sysfs_path = '/sys/class/gpio/gpio%s/' % self.sensor_gpio
            self.sensor_gpio_value_file = gpio_sysfs_path + 'value'
            self.sensor_gpio_edge_file = gpio_sysfs_path + 'edge'
        # Check if the sensor GPIO has been configured - file is readable:
            try:
                with open(self.sensor_gpio_value_file, 'r'):
                    pass
            except IOError:
                message = ('%s : file does not exist or cannot be read. '
                           'You must export the GPIO no %s as input first!'
                           % (self.sensor_gpio_value_file, self.sensor_gpio))
                ui.display(message)
                ui.exit_program()
            # Ensure that the interrupts are generated for sensor GPIO
            # for both rising and falling edge:
            with open(self.sensor_gpio_edge_file, 'r') as edge_file:
                if 'both' not in edge_file.read():
                    message = ('%s: file does not exist, cannot be read, '
                               'or the interrupt on GPIO %i is not set '
                               'to "both". Check the system configuration.'
                               % (self.sensor_gpio_edge_file, self.sensor_gpio))
                    ui.display(message)
                    ui.exit_program()
        # Setup the wiringPi MCP23017 chips for valve outputs
        wiringpi.mcp23017Setup(self.pin_base, self.mcp0_address)
        wiringpi.mcp23017Setup(self.pin_base + 16, self.mcp1_address)
        pins = range(self.pin_base, self.pin_base + 32)
        # Set all I/O lines on MCP23017s as outputs - mode=1
        for pin in pins:
            wiringpi.pinMode(pin, 1)
        # Make a nice list out of the signal arrangement string:
        signals_arrangement = self.signals_arrangement.split(',')
        # Assign wiringPi pin numbers on MCP23017s to the Monotype
        # control signals
        self.interface_pin_number = dict(zip(signals_arrangement, pins))
        # Mark the caster as configured
        self.configured = True
        # Wait for user confirmation if in debug mode
        ui.debug_enter_data('Caster configured. [Enter] to continue... ')

    def get_caster_settings(self):
        """get_caster_settings():

        Reads the settings for a caster with self.name
        from the config file (where it is represented by a section, whose
        name is the same as the caster's).

        The parameters returned are:
        [diecase_system, unit_adding, interface_id]

        where:
        diecase_system - caster's diecase layout and a method of
        accessing 16th row, if applicable:
             norm15     - old 15x15,
             norm17     - 15x17 NI, NL,
             hmn        - 16x17 HMN (rare),
             kmn        - 16x17 KMN (rare),
             shift      - 16x17 unit-shift (most modern).
        unit_adding [0,1] - whether the machine has a unit-adding attachment,
        interface_id [0,1,2,3] - ID of the interface connected to the caster.
        """
        if cfg_parser.section_not_found(self.name):
            # Default caster parameters:
            self.is_perforator = False
            self.interface_id = 0
            self.unit_adding = False
            self.diecase_system = 'norm17'
            self.unit_adding = False
            self.diecase_system = 'norm17'
            # End here if caster not found in config
            return False
        self.is_perforator = cfg_parser.get_config(self.name, 'is_perforator')
        self.interface_id = cfg_parser.get_config(self.name, 'interface_id')
        if not self.is_perforator:
        # Get caster parameters from conffile
            self.unit_adding = cfg_parser.get_config(self.name, 'unit_adding')
            self.diecase_system = cfg_parser.get_config(self.name,
                                                        'diecase_system')
        # Caster correctly configured
        return True

    def get_interface_settings(self):
        """get_interface_settings():

        Reads a configuration file and gets interface parameters.

        If the config file is correct, it returns a list:
        [emergency_gpio, sensor_gpio, mcp0_address, mcp1_address, pin_base]

        emergency_gpio    - BCM number for emergency stop button GPIO
        sensor_gpio       - BCM number for sensor GPIO
        mcp0_address     - I2C address for 1st MCP23017
        mcp1_address     - I2C address for 2nd MCP23017
        pin_base         - pin numbering base for GPIO outputs on MCP23017

        Multiple interfaces attached to a single Raspberry Pi:

        It's possible to use up to four interfaces (i.e. 2xMCP23017, 4xULN2803)
        for a single Raspberry. It can be used for operating multiple casters,
        or a caster and a keyboard's paper tower, simultaneously (without
        detaching a valve block from the paper tower and moving it elsewhere).

        These interfaces should be identified by numbers: 0, 1, 2, 3.

        Each of the MCP23017 chips has to have unique I2C addresses. They are
        set by pulling the A0, A1, A2 pins up (to 3.3V) or down (to GND).
        There are 2^3 = 8 possible addresses, and an interface uses two chips,
        so you can use up to four interfaces.

        It's best to order the MCP23017 chips' addresses ascending, i.e.

        interface_id   mcp0 pin        mcp1 pin        mcp0         mcp1
                       A2,A1,A0        A2,A1,A0        address      address
        0              000             001             0x20         0x21
        1              010             011             0x22         0x23
        2              100             101             0x24         0x25
        3              110             111             0x26         0x27

        where 0 means the pin is pulled down, and 1 means pin pulled up.

        As for pin_base parameter, it's the wiringPi's way of identifying GPIOs
        on MCP23017 extenders. WiringPi is an abstraction layer which allows
        you to control (read/write) pins on MCP23017 just like you do it on
        typical Raspberry Pi's GPIO pins. Thus you don't have to send bytes
        to registers.
        The initial 64 GPIO numbers are reserved for Broadcom SoC,
        so the lowest pin base you can use is 65.
        Each interface (2xMCP23017) uses 32 pins.

        If you are using multiple interfaces per Raspberry, you SHOULD
        assign the following pin bases to each interface:

        interface_id       pin_base
        0                  65
        1                  98                  (pin_base0 + 32)
        2                  131                 (pin_base1 + 32)
        3                  164                 (pin_base2 + 32)
        """
        iface_name = 'Interface' + str(self.interface_id)
        if cfg_parser.section_not_found(iface_name):
            # Set default parameters if interface not found in config:
            self.emergency_gpio = 24
            self.sensor_gpio = 17
            self.mcp0_address = 0x20
            self.mcp1_address = 0x21
            self.pin_base = 65
            self.signals_arrangement = ('1,2,3,4,5,6,7,8,9,10,11,12,13,14,'
                                        '0005,0075,'
                                        'A,B,C,D,E,F,G,H,I,J,K,L,M,N,S,O15')
            # Signal that we're on fallback
            return False
        if not self.is_perforator:
            # Emergency stop and sensor are valid only for casters,
            # perforators do not have them
            self.emergency_gpio = cfg_parser.get_config(iface_name, 'stop_gpio')
            self.sensor_gpio = cfg_parser.get_config(iface_name, 'sensor_gpio')
        # Set up MCP23017 interface parameters
        self.mcp0_address = cfg_parser.get_config(iface_name, 'mcp0_address')
        self.mcp1_address = cfg_parser.get_config(iface_name, 'mcp1_address')
        self.pin_base = cfg_parser.get_config(iface_name, 'pin_base')
        # Check which signals arrangement the interface uses...
        signals_arr = cfg_parser.get_config(iface_name, 'signals_arrangement')
        # ...and get the signals order for it:
        self.signals_arrangement = cfg_parser.get_config('SignalsArrangements',
                                                         signals_arr)
        # Interface configured successfully - return True
        return True

    def detect_rotation(self):
        """detect_rotation():

        Checks if the machine is running by counting pulses on a sensor
        input. One pass of a while loop is a single cycle. If cycles_max
        value is exceeded in a time <= time_max, the program assumes that
        the caster is rotating and it can start controlling the machine.
        """
        cycles = 0
        cycles_max = 3
        # Let's give it 30 seconds timeout
        time_start = time.time()
        time_max = 30
        # Subroutine definition

        def start_the_machine():
            """start_the_machine

            Allows user to decide what to do if the machine is not rotating.
            Continue, abort or exit program.
            """
            def continue_casting():
                """Helper function - continue casting."""
                return True
            def return_to_menu():
                """Raise an exception to return to main menu"""
                raise newexceptions.ReturnToMenu
            def exit_program():
                """Raise an exception to exit program"""
                raise newexceptions.ExitProgram
            options = {'C' : continue_casting,
                       'M' : return_to_menu,
                       'E' : exit_program}
            message = ('Machine not running - you need to start it first.\n'
                       '[C]ontinue, return to [M]enu or [E]xit program? ')
            choice = ui.simple_menu(message, options).upper()
            return options[choice]()

        # End of subroutine definition
        # Check for sensor signals, keep checking until max time is exceeded
        # or target number of cycles is reached
        with open(self.sensor_gpio_value_file, 'r') as gpiostate:
            while time.time() <= time_start + time_max and cycles <= cycles_max:
                sensor_signals = select.epoll()
                sensor_signals.register(gpiostate, select.POLLPRI)
                events = sensor_signals.poll(0.5)
            # Check if the sensor changes state at all
                if events:
                    gpiostate.seek(0)
                    sensor_state = int(gpiostate.read())
                    prev_state = 0
                # Increment the number of passed machine cycles
                    if sensor_state == 1 and prev_state == 0:
                        prev_state = 1
                        cycles += 1
                    elif sensor_state == 0 and prev_state == 1:
                        prev_state = 0
            else:
            # Determine if the loop ended due to timeout (machine not running)
            # or exceeded number of cycles (machine running):
                if cycles > cycles_max:
                    ui.display('\nOkay, the machine is running...\n')
                    return True
                elif start_the_machine():
                # Check again recursively:
                    return self.detect_rotation()
                else:
                # This will lead to return to menu
                    return False

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
        # Subroutine definitions
        def send_signals_to_caster(signals, timeout):
            """send_signals_to_caster:

            Sends a combination of signals passed in function's arguments
            to the caster. This function also checks if the machine cycle
            sensor changes its state, and decides whether it's an "air on"
            phase (turn on the valves) or "air off" phase (turn off the valves,
            end function, return True to signal the success).
            If no signals are detected within a given timeout - returns False
            (to signal the casting failure).
            """
            with open(self.sensor_gpio_value_file, 'r') as gpiostate:
                polling = select.epoll()
                polling.register(gpiostate, select.POLLPRI)
                prev_state = 0
                while True:
                # Polling the interrupt file
                    events = polling.poll(timeout)
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
                        return False

        def stop_menu():
            """stop_menu:

            This allows us to choose whether we want to continue,
            return to menu or exit if the machine is stopped during casting.
            """
            def continue_casting():
                """Helper function - continue casting."""
                return True

            def return_to_menu():
                """return_to_menu

                Aborts casting. Makes sure the pump is turned off.
                Raise an exception to be caught by higher-level functions
                from the Casting class
                """
                emergency_cleanup()
                raise newexceptions.CastingAborted

            def exit_program():
                """exit_program

                Helper function - throws an exception to exit the program.
                Also makes sure the pump is turned off."""
                emergency_cleanup()
                raise newexceptions.ExitProgram
            # End of subroutine definitions
            # Now, a little menu...
            options = {'C' : continue_casting,
                       'M' : return_to_menu,
                       'E' : exit_program}
            message = ('Machine has stopped running! Check what happened.\n'
                       '[C]ontinue, return to [M]enu or [E]xit program? ')
            choice = ui.simple_menu(message, options).upper()
            return options[choice]()

        def emergency_cleanup():
            """emergency_cleanup:

            If the machine is stopped, we need to turn the pump off and then
            turn all the lines off. Otherwise, the machine will keep pumping
            while it shouldnot (e.g. after a splash).

            The program will hold execution until the operator clears
            the situation, it needs turning the machine at least one
            full revolution. The program MUST turn the pump off to move on.
            """
            pump_off = False
            stop_signals = ['N', 'J', '0005']
            ui.display('Stopping the pump...')
            while not pump_off:
            # Try stopping the pump until we succeed!
            # Keep calling process_signals until it returns True
            # (the machine receives and processes the pump stop signal)
                pump_off = send_signals_to_caster(stop_signals, cycle_timeout)
            else:
                ui.display('Pump stopped. All valves off...')
                self.deactivate_valves()
                time.sleep(1)
                return True
        # End of subroutine definitions
        while not send_signals_to_caster(signals, 30):
        # Keep trying to cast the combination, or end here
        # (subroutine will throw an exception if operator exits)
            stop_menu()
        else:
        # Successful ending - the combination has been cast
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
        for pin in range(self.pin_base, self.pin_base + 32):
            wiringpi.digitalWrite(pin, 0)

    def cleanup(self):
        """cleanup():

        Turn all valves off, then set all lines on MCP23017 as inputs.
        """
        ui.debug_info('Cleaning up: turning all pins off...')
        for pin in range(self.pin_base, self.pin_base + 32):
            wiringpi.digitalWrite(pin, 0)
        # Wait for user confirmation in debug mode
        ui.debug_enter_data('Press [Enter] to continue... ')

    def __exit__(self, *args):
        """On exit, do the cleanup:
        """
        ui.debug_info('Exiting caster/interface context.')
        self.lock = False
        self.cleanup()
