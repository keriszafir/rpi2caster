# -*- coding: utf-8 -*-
"""
Monotype:

This module contains low- and mid-level caster control routines for
a physical Monotype composition caster, linked via pneumatic valves
and MCP23017 IC's to the Raspberry Pi.
"""

# Config parser for reading the interface settings
import ConfigParser
# Essential for polling the sensor for state change:
import select
# Built-in time library
import time
# Custom exceptions
import newexceptions
# WiringPi2 Python bindings: essential for controlling the MCP23017!
try:
    import wiringpi2 as wiringpi
except ImportError:
    print 'Missing dependency: wiringPi2 Python bindings: wiringpi2-python'
    print 'Caster control will not work!'
# Set up a default user interface object:
# Instantiate a default text user interface


class Monotype(object):
    """Monotype(job, name, confFilePath):

    A class which stores all hardware-layer methods, related to caster control.
    This class requires a caster name, and a database object.
    """

    def __init__(self, name='Monotype', configPath='/etc/rpi2caster.conf'):
        """Creates a caster object for a given caster name
        """
        self.UI = None
        self.name = name
        self.is_perforator = None
        self.interfaceID = None
        self.unitAdding = None
        self.diecaseSystem = None
        self.emergencyGPIO = None
        self.sensorGPIO = None
        self.mcp0Address = None
        self.mcp1Address = None
        self.pinBase = None
        self.signalsArrangement = None
        self.lock = None
        self.sensorGPIOEdgeFile = None
        self.sensorGPIOValueFile = None
        self.wiringPiPinNumber = None

        # Check if config file is readable first
        try:
            with open(configPath, 'r'):
                self.configPath = configPath
            self.cfg = ConfigParser.SafeConfigParser()
            self.cfg.read(self.configPath)
            self.caster_setup()
        except IOError:
            self.UI.display('Cannot open config file:', configPath)
        # It's not configured yet - we'll do it when needed, and only once:
        self.configured = False

    def __enter__(self):
        """Run the setup when entering the context:
        """
        self.UI.debug_info('Entering caster/interface context...')
        if self.lock:
            self.UI.display('Caster %s is already busy!' % self.name)
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
        # Default caster parameters:
        self.is_perforator = False
        self.interfaceID = 0
        self.unitAdding = False
        self.diecaseSystem = 'norm17'
        # Default interface parameters:
        self.emergencyGPIO = 24
        self.sensorGPIO = 17
        self.mcp0Address = 0x20
        self.mcp1Address = 0x21
        self.pinBase = 65
        self.signalsArrangement = ('1,2,3,4,5,6,7,8,9,10,11,12,13,14,0005,'
                                   '0075,A,B,C,D,E,F,G,H,I,J,K,L,M,N,S,O15')
        # Next, this method reads caster data from database and fetches
        # a list of caster parameters: diecaseFormat, unitAdding, interfaceID.
        # In case there is no data, the function will run on default settings.
        self.get_caster_settings()
        self.get_interface_settings()
        # When debugging, display all caster info:
        output = {'\nCaster parameters:\n' : '',
                  'Using caster name: ' : self.name,
                  'Is a perforator? ' : self.is_perforator,
                  '\nInterface parameters:\n' : '',
                  'Interface ID: ' : self.interfaceID,
                  '1st MCP23017 I2C address: ' : self.mcp0Address,
                  '2nd MCP23017 I2C address: ' : self.mcp1Address,
                  'MCP23017 pin base for GPIO numbering: ' : self.pinBase,
                  'Signals arrangement: ' : self.signalsArrangement,
                  'Emergency button GPIO: ' : self.emergencyGPIO,
                  'Sensor GPIO: ' : self.sensorGPIO}
        for parameter in output:
            self.UI.debug_info(parameter, output[parameter])
        prompt = '[Enter] to continue...'
        self.UI.debug_enter_data(prompt)

        # This is done only for a caster interface:
        if not self.is_perforator:
        # Set up an input for machine cycle sensor:
            gpioSysfsPath = '/sys/class/gpio/gpio%s/' % self.sensorGPIO
            self.sensorGPIOValueFile = gpioSysfsPath + 'value'
            self.sensorGPIOEdgeFile = gpioSysfsPath + 'edge'
        # Check if the sensor GPIO has been configured - file is readable:
            try:
                with open(self.sensorGPIOValueFile, 'r'):
                    pass
            except IOError:
                message = ('%s : file does not exist or cannot be read. '
                           'You must export the GPIO no %s as input first!'
                           % (self.sensorGPIOValueFile, self.sensorGPIO))
                self.UI.display(message)
                self.UI.exit_program()
            # Ensure that the interrupts are generated for sensor GPIO
            # for both rising and falling edge:
            with open(self.sensorGPIOEdgeFile, 'r') as edgeFile:
                if 'both' not in edgeFile.read():
                    message = ('%s: file does not exist, cannot be read, '
                               'or the interrupt on GPIO %i is not set '
                               'to "both". Check the system configuration.'
                               % (self.sensorGPIOEdgeFile, self.sensorGPIO))
                    self.UI.display(message)
                    self.UI.exit_program()
        # Setup the wiringPi MCP23017 chips for valve outputs
        wiringpi.mcp23017Setup(self.pinBase, self.mcp0Address)
        wiringpi.mcp23017Setup(self.pinBase + 16, self.mcp1Address)
        pins = range(self.pinBase, self.pinBase + 32)
        # Set all I/O lines on MCP23017s as outputs - mode=1
        for pin in pins:
            wiringpi.pinMode(pin, 1)
        # Make a nice list out of the signal arrangement string:
        signalsArrangement = self.signalsArrangement.split(',')
        # Assign wiringPi pin numbers on MCP23017s to the Monotype
        # control signals
        self.wiringPiPinNumber = dict(zip(signalsArrangement, pins))
        # Mark the caster as configured
        self.configured = True
        # Wait for user confirmation if in debug mode
        self.UI.debug_enter_data('Caster configured. [Enter] to continue... ')

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
        try:
        # Determine if it's a perforator interface
            self.is_perforator = self.cfg.get(self.name, 'is_perforator')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError,
                ValueError, TypeError):
            self.is_perforator = False
        # We now know if it's a perforator
        try:
            self.interfaceID = self.cfg.get(self.name, 'interface_id')
            if not self.is_perforator:
            # Get caster parameters from conffile
                self.unitAdding = bool(self.cfg.get(self.name, 'unit_adding'))
                self.diecaseSystem = self.cfg.get(self.name, 'diecase_system')
        # Do nothing if config is wrong:
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError,
                ValueError, TypeError):
            self.UI.display('Incorrect caster parameters. '
                            'Using hardcoded defaults.')
            self.UI.exception_handler()
            return None

    def get_interface_settings(self):
        """get_interface_settings():

        Reads a configuration file and gets interface parameters.

        If the config file is correct, it returns a list:
        [emergencyGPIO, sensorGPIO, mcp0Address, mcp1Address, pinBase]

        emergencyGPIO   - BCM number for emergency stop button GPIO
        sensorGPIO      - BCM number for sensor GPIO
        mcp0Address     - I2C address for 1st MCP23017
        mcp1Address     - I2C address for 2nd MCP23017
        pinBase         - pin numbering base for GPIO outputs on MCP23017

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

        interfaceID    mcp0 pin        mcp1 pin        mcp0         mcp1
                       A2,A1,A0        A2,A1,A0        addr         addr
        0              000             001             0x20         0x21
        1              010             011             0x22         0x23
        2              100             101             0x24         0x25
        3              110             111             0x26         0x27

        where 0 means the pin is pulled down, and 1 means pin pulled up.

        As for pinBase parameter, it's the wiringPi's way of identifying GPIOs
        on MCP23017 extenders. WiringPi is an abstraction layer which allows
        you to control (read/write) pins on MCP23017 just like you do it on
        typical Raspberry Pi's GPIO pins. Thus you don't have to send bytes
        to registers.
        The initial 64 GPIO numbers are reserved for Broadcom SoC,
        so the lowest pin base you can use is 65.
        Each interface (2xMCP23017) uses 32 pins.

        If you are using multiple interfaces per Raspberry, you SHOULD
        assign the following pin bases to each interface:

        interfaceID        pinBase
        0                  65
        1                  98                  (pinBase0 + 32)
        2                  131                 (pinBase1 + 32)
        3                  164                 (pinBase2 + 32)
        """
        ifName = 'Interface' + str(self.interfaceID)
        try:
        # Check if the interface is active, else do nothing
            trueAliases = ['true', '1', 'on', 'yes']
            if self.cfg.get(ifName, 'active').lower() in trueAliases:
                if not self.is_perforator:
                # Emergency stop and sensor are valid only for casters,
                # perforators do not have them
                    self.emergencyGPIO = int(self.cfg.get(ifName, 'stop_gpio'))
                    self.sensorGPIO = int(self.cfg.get(ifName, 'sensor_gpio'))
                self.mcp0Address = int(self.cfg.get(ifName, 'mcp0_address'))
                self.mcp1Address = int(self.cfg.get(ifName, 'mcp1_address'))
                self.pinBase = int(self.cfg.get(ifName, 'pin_base'))
            # Check which signals arrangement the interface uses...
                signalsArrangement = self.cfg.get(ifName, 'signals_arr')
            # ...and get the signals order for it:
                self.signalsArrangement = self.cfg.get('SignalsArrangements',
                                                  signalsArrangement)
            else:
            # This happens if the interface is inactive in conffile:
                self.UI.display('Interface %i is marked as inactive!'
                                % self.interfaceID)
        # In case of wrong configuration, do nothing
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError,
                ValueError, TypeError):
            self.UI.display('Incorrect interface parameters. '
                            'Using hardcoded defaults.')
            self.UI.exception_handler()
            return None

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

        def continue_after_machine_not_rotating():
            """continue_after_machine_not_rotating

            Allows user to decide what to do if the machine is not rotating.
            Continue, abort or exit program.
            """
            def continue_casting():
            # Helper function - continue casting.
                return True
            def return_to_menu():
                raise newexceptions.ReturnToMenu
            def exit_program():
                raise newexceptions.ExitProgram
            options = {'C' : continue_casting,
                       'M' : return_to_menu,
                       'E' : exit_program}
            message = ('Machine not running - you need to start it first.\n'
                       '[C]ontinue, return to [M]enu or [E]xit program? ')
            choice = self.UI.simple_menu(message, options).upper()
            return options[choice]()

        # End of subroutine definition
        # Check for sensor signals, keep checking until max time is exceeded
        # or target number of cycles is reached
        with open(self.sensorGPIOValueFile, 'r') as gpiostate:
            while time.time() <= time_start + time_max and cycles <= cycles_max:
                sensorSignals = select.epoll()
                sensorSignals.register(gpiostate, select.POLLPRI)
                events = sensorSignals.poll(0.5)
            # Check if the sensor changes state at all
                if events:
                    gpiostate.seek(0)
                    sensorState = int(gpiostate.read())
                    previousState = 0
                # Increment the number of passed machine cycles
                    if sensorState == 1 and previousState == 0:
                        previousState = 1
                        cycles += 1
                    elif sensorState == 0 and previousState == 1:
                        previousState = 0
            else:
            # Determine if the loop ended due to timeout (machine not running)
            # or exceeded number of cycles (machine running):
                if cycles > cycles_max:
                    self.UI.display('\nOkay, the machine is running...\n')
                    return True
                elif continue_after_machine_not_rotating():
                # Check again recursively:
                    return self.detect_rotation()
                else:
                # This will lead to return to menu
                    return False

    def process_signals(self, signals, machineTimeout=5):
        """process_signals(signals, machineTimeout):

        Checks for the machine's rotation, sends the signals (activates
        solenoid valves) after the caster is in the "air bar down" position.

        If no machine rotation is detected (sensor input doesn't change
        its state) during machineTimeout, calls a function to ask user
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
            with open(self.sensorGPIOValueFile, 'r') as gpiostate:
                po = select.epoll()
                po.register(gpiostate, select.POLLPRI)
                previousState = 0
                while True:
                # Polling the interrupt file
                    events = po.poll(timeout)
                    if events:
                    # Normal control flow when the machine is working
                    # (cycle sensor generates events)
                        gpiostate.seek(0)
                        sensorState = int(gpiostate.read())
                        if sensorState == 1 and previousState == 0:
                        # Now, the air bar on paper tower would go down -
                        # we got signal from sensor to let the air in
                            self.activate_valves(signals)
                            previousState = 1
                        elif sensorState == 0 and previousState == 1:
                        # Air bar on paper tower goes back up -
                        # end of "air in" phase, turn off the valves
                            self.deactivate_valves()
                            previousState = 0
                            # Signals sent to the caster - successful ending
                            return True
                    else:
                    # Timeout with no signals - failed ending
                        return False

        def continue_after_machine_stopped():
            """continue_after_machine_stopped:

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
            choice = self.UI.simple_menu(message, options).upper()
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
            pumpOff = False
            stopSignal = ['N', 'J', '0005']
            self.UI.display('Stopping the pump...')
            while not pumpOff:
            # Try stopping the pump until we succeed!
            # Keep calling process_signals until it returns True
            # (the machine receives and processes the pump stop signal)
                pumpOff = send_signals_to_caster(stopSignal, machineTimeout)
            else:
                self.UI.display('Pump stopped. All valves off...')
                self.deactivate_valves()
                time.sleep(1)
                return True
        # End of subroutine definitions
        while not send_signals_to_caster(signals, 30):
        # Keep trying to cast the combination, or end here
        # (subroutine will throw an exception if operator exits)
            continue_after_machine_stopped()
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
        if signals:
            for monotypeSignal in signals:
                pin = self.wiringPiPinNumber[monotypeSignal]
                wiringpi.digitalWrite(pin, 1)

    def deactivate_valves(self):
        """deactivate_valves():

        Turn all valves off after casting/punching any character.
        Call this function to avoid outputs staying turned on if something
        goes wrong, esp. in case of abnormal program termination.
        """
        for pin in range(self.pinBase, self.pinBase + 32):
            wiringpi.digitalWrite(pin, 0)

    def cleanup(self):
        """cleanup():

        Turn all valves off, then set all lines on MCP23017 as inputs.
        """
        self.UI.debug_info('Cleaning up: turning all pins off...')
        for pin in range(self.pinBase, self.pinBase + 32):
            wiringpi.digitalWrite(pin, 0)
        # Wait for user confirmation in debug mode
        self.UI.debug_enter_data('Press [Enter] to continue... ')

    def __exit__(self, *args):
        """On exit, do the cleanup:
        """
        self.UI.debug_info('Exiting caster/interface context.')
        self.lock = False
        self.cleanup()
