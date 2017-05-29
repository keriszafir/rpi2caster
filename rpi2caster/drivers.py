# -*- coding: utf-8 -*-
"""hardware drivers for rpi2caster"""

from collections import OrderedDict
from functools import reduce
import time
from .rpi2caster import UI, CFG, option
from .misc import singleton, weakref_singleton
from .monotype import AIR_ON, MachineStopped
from .definitions import HardwareBackend

# Output latch registers for SMBus MCP23017 control
OLATA, OLATB = 0x14, 0x15
# Port direction registers for SMBus MCP23017 control
IODIRA, IODIRB = 0x00, 0x10
# Sensor and output drivercollection
SENSORS, OUTPUTS = {}, {}


class SensorBase(object):
    """Mockup for a machine cycle sensor"""
    name = 'generic machine cycle sensor'
    gpio = CFG.interface.sensor_gpio
    last_state, manual_mode, signals = True, True, None
    timeout, time_on, time_off = 30, 0.1, 0.1

    def __enter__(self):
        UI.pause('Using a {} for machine feedback'.format(self.name),
                 min_verbosity=3)
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


class OutputBase(object):
    """Mockup for a driver for 32 pneumatic outputs"""
    signals_arrangement = CFG.interface.signals_arrangement
    mcp0_address = CFG.interface.mcp0
    mcp1_address = CFG.interface.mcp1
    i2c_bus_number = CFG.interface.i2c_bus
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
            assoc = dict(zip(CFG.interface.signals_arrangement,
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


def make_simulation_interface():
    """Simulation interface - no hardware control;
    used for testing the casting/punching routines."""

    class SimulationSensor(SensorBase):
        """Simulate casting with no actual machine"""
        name = 'simulation - mockup casting interface'

        def check_if_machine_is_working(self):
            """Warn that this is just a simulation"""
            UI.display('Simulation mode - no machine is used.\n'
                       'This will emulate the actual casting sequence '
                       'as closely as possible.\n')
            return super().check_if_machine_is_working()

    class SimulationOutput(OutputBase):
        """Simulation output driver - don't control any hardware"""
        name = 'simulation - mockup casting interface'

    return HardwareBackend(SimulationSensor, SimulationOutput)


# HARDWARE DRIVERS
# Some interfaces have a sensor and output that must work together.
# e.g. parallel interface
# Other sensors and outputs are modular and can work together
# in different combinations (e.g. SysFS/RPi.GPIO + WiringPi/SMBus).

def make_parallel_interface():
    """"Parallel port controller
    (PyPI: pyparallel, Debian: python3-parallel)"""
    from parallel import Parallel

    @weakref_singleton
    class ParallelOutput(OutputBase):
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

        def __exit__(self, *_):
            super().__exit__()
            self.port = None

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

        def valves_on(self, signals):
            """Get the signals, transform them to numeric value and send
            the bytes to i2c devices"""
            if signals:
                assignment = (self.mapping.get(sig, 0) for sig in signals)
                number = reduce(lambda x, y: x | y, assignment)
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
            """Deactivate the valves - actually, do nothing"""
            pass

    class ParallelSensor(SensorBase):
        """Parallel sensor does nothing, as everything is controlled by
        the micro-controller in the interface."""
        name = 'Symbiosys parallel port interface'

        def check_if_machine_is_working(self):
            """Reset the interface if needed and go on"""
            UI.confirm('Turn on the machine...',
                       default=True, abort_answer=False)

        def wait_for(self, new_state, timeout=None):
            """Do nothing"""
            new_state, timeout = new_state, timeout

    return HardwareBackend(ParallelSensor, ParallelOutput)


def make_sysfs_sensor():
    """SysFS kernel interface sensor. Must be pre-configured."""
    import io
    import os
    import select

    class SysfsSensor(SensorBase):
        """Optical cycle sensor using kernel sysfs interface"""
        name = 'Kernel SysFS interface for photocell sensor GPIO'
        bounce_time = CFG.interface.bounce_time * 0.001
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
            timeout means that if no signals in given time,
            raise MachineStopped.
            force_cycle means that if last_state == new_state,
            a full cycle must pass before exit.
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

    return SysfsSensor


def make_gpio_sensor():
    """RPi.GPIO I/O control library
    (PyPI: RPi.GPIO, Debian: python3-rpi.gpio)"""
    import RPi.GPIO as GPIO

    @singleton
    class RPiGPIOSensor(SensorBase):
        """Simple RPi.GPIO input driver for photocell"""
        name = 'RPi.GPIO input driver'
        timeout = 5
        gpio = CFG.interface.sensor_gpio
        bounce_time = CFG.interface.bounce_time

        def __enter__(self):
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.gpio, GPIO.IN)
            super().__enter__()
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

    return RPiGPIOSensor


def make_wiringpi_output():
    """WiringPi i/o controller (PyPI: wiringpi)"""
    import wiringpi

    @singleton
    class WiringPiOutput(OutputBase):
        """A 32-channel control interface based on two MCP23017 chips"""
        name = 'MCP23017 driver using wiringPi2-Python library'
        pin_base = CFG.interface.pin_base
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

    return WiringPiOutput


def make_smbus_output():
    """SMBus i2c controller (PyPI: smbus-cffi, Debian: python3-smbus)"""
    from smbus import SMBus

    class SMBusOutput(OutputBase):
        """Python SMBus-based output controller for rpi2caster."""
        name = 'SMBus output driver'
        # define a signal-to-bit mapping
        signal_numbers = [2 ** x for x in range(32)]

        def _send(self, byte0, byte1, byte2, byte3):
            """Write 4 bytes of data to all ports (A, B)
            on all devices (0, 1)"""
            self.port.write_byte_data(self.mcp0_address, OLATA, byte3)
            self.port.write_byte_data(self.mcp0_address, OLATB, byte2)
            self.port.write_byte_data(self.mcp1_address, OLATA, byte1)
            self.port.write_byte_data(self.mcp1_address, OLATB, byte0)

        def valves_on(self, signals):
            """Get the signals, transform them to numeric value and send
            the bytes to i2c devices"""
            if signals:
                assignment = (self.mapping.get(sig, 0) for sig in signals)
                number = reduce(lambda x, y: x | y, assignment)
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
            super().__enter__()
            return self

        def __exit__(self, *_):
            super().__exit__()
            self.port = None

    return SMBusOutput


def make_interface(sensor_name, output_name):
    """Return a HardwareBackend namedtuple with sensor and driver"""
    sensors = {'sysfs': make_sysfs_sensor,
               'gpio': make_gpio_sensor,
               'rpi_gpio': make_gpio_sensor}
    outputs = {'smbus': make_smbus_output,
               'wiringpi': make_wiringpi_output}
    try:
        sensor_factory = sensors[str(sensor_name).lower()]
        output_factory = outputs[str(output_name).lower()]
        sensor, output = sensor_factory(), output_factory()
        return HardwareBackend(sensor, output)
    except KeyError as exc:
        raise NameError('{}: not defined'.format(str(exc)))
