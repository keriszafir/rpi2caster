# -*- coding: utf-8 -*-
"""
Monotype:

This module contains low- and mid-level caster control routines for
a physical Monotype composition caster, linked via pneumatic valves
and MCP23017 IC's to the Raspberry Pi.

The Caster
"""
import io
# Essential for polling the sensor for state change:
import select
# Constants shared between modules
from rpi2caster import constants
# Custom exceptions
from rpi2caster import exceptions
# Configuration parser functions
from rpi2caster import cfg_parser
# Default user interface
from rpi2caster.global_settings import USER_INTERFACE as UI
# Caster prototype
from rpi2caster import common_caster
# WiringPi2 Python bindings: essential for controlling the MCP23017!
try:
    import wiringpi2 as wiringpi
except ImportError:
    raise exceptions.MissingDependency('You must install wiringpi2!')


class Caster(common_caster.Caster):
    """Caster(name):

    A class which stores all hardware-layer methods, related to caster control.
    This class requires a caster name, and a database object.
    """

    def __init__(self):
        """Creates a caster object for a given caster name
        """
        self.name = 'Monotype'
        self.is_perforator = None
        self.lock = None
        self.sensor_gpio_edge_file = None
        self.sensor_gpio_value_file = None
        self.emerg_gpio_edge_file = None
        self.emerg_gpio_value_file = None
        # Configure the caster
        self.interface_pin_number = self.caster_setup()
        # Add a pump
        self.pump = common_caster.Pump()
        # Set default wedge positions
        self.current_0005 = '15'
        self.current_0075 = '15'

    def caster_setup(self):
        """Sets up initial default parameters for caster & interface."""
        # Inputs are represented as files in kernel's sysfs interface
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
            UI.debug_info('Using hardcoded defaults for caster settings...')
            self.is_perforator = False
            interface_id = 0

        # Now configure interface outputs
        try:
            out_settings = cfg_parser.get_output_settings(interface_id)
            (mcp0_address, mcp1_address,
             pin_base, signals_arrangement) = out_settings
        except exceptions.NotConfigured:
            # Cannot read config? Use defaults:
            UI.debug_info('Using hardcoded defaults for interface outputs...')
            mcp0_address = constants.MCP0
            mcp1_address = constants.MCP1
            pin_base = constants.PIN_BASE
            signals_arrangement = constants.ALNUM_ARR
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
                emergency_stop_gpio = constants.EMERGENCY_STOP_GPIO
                sensor_gpio = constants.SENSOR_GPIO
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
        UI.debug_confirm('Caster configured.')
        # Assign wiringPi pin numbers on MCP23017s to the Monotype
        # control signals. Return the result.
        return dict(zip(signals_arrangement.split(','), pins))

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
                # Check if the sensor changes state at all
                if sensor_signals.poll(time_max):
                    gpiostate.seek(0)
                    sensor_state = int(gpiostate.read())
                    # Increment the number of passed machine cycles
                    if sensor_state and not prev_state:
                        cycles += 1
                    prev_state = sensor_state
                else:
                    # Timeout with no signals = go to stop menu
                    self._stop_menu(casting=False)
                    # Start counting cycles all over again
                    cycles = 0
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
        try:
            with io.open(self.sensor_gpio_value_file, 'r') as gpiostate:
                sensor_signals = select.epoll()
                sensor_signals.register(gpiostate, select.POLLPRI)
                prev_state = 0
                while True:
                    # Polling the interrupt file
                    if sensor_signals.poll(timeout):
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
        except (KeyboardInterrupt, EOFError):
            # Let user decide if they want to continue / go to menu / exit
            self._stop_menu()

    def activate_valves(self, signals):
        """activate_valves(signals):

        Activates the solenoid valves connected with interface's outputs,
        as specified in the "signals" parameter (tuple or list).
        The input array "signals" contains strings, either
        lowercase (a, b, g, s...) or uppercase (A, B, G, S...).
        Do nothing if the function receives an empty sequence, which will
        occur if we cast with the matrix found at position O15.
        """
        self.pump.check_working(signals)
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
