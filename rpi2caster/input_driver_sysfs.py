# -*- coding: utf-8 -*-
"""
Kernel SysFS-based input drivers for photocell and machine cycle sensor.
"""
import io
# Essential for polling the sensor for state change:
import select
# Debounce timers need this
from time import time
# Constants shared between modules
from .global_config import UI, SENSOR_GPIO
# Custom exceptions
from .exceptions import MachineStopped
# Caster prototype
from .monotype import SimulationSensor


class SysfsSensor(SimulationSensor):
    """Optical cycle sensor using kernel sysfs interface"""
    def __init__(self, gpio=SENSOR_GPIO):
        super().__init__()
        self.gpio = gpio
        self.signals = None
        self.last_state = False
        self.value_file_obj = None
        self.name = 'Kernel SysFS interface for photocell sensor GPIO'
        try:
            self.value_file = configure_sysfs_interface(gpio)
        except TypeError:
            self.value_file = '/dev/null'
            self.edge_file = '/dev/null'

    @property
    def parameters(self):
        """Gets a list of parameters"""
        return [(self.name, 'Sensor driver'),
                (self.gpio, 'GPIO number'),
                (self.value_file, 'Value file path'),
                (self.edge_file, 'Edge file path')]

    def wait_for(self, new_state, timeout=5, *_):
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

        # Set debounce time to now
        debounce = time()
        # Prevent sudden exit in the midst of machine cycle
        with io.open(self.value_file, 'r') as gpiostate:
            if get_state() == new_state:
                self.last_state = not new_state
        with io.open(self.value_file, 'r') as gpiostate:
            signals = select.epoll()
            signals.register(gpiostate, select.POLLPRI)
            while self.last_state != new_state:
                if signals.poll(timeout):
                    state = get_state()
                    if time() - debounce > 0.005:
                        self.last_state = state
                    debounce = time()
                else:
                    raise MachineStopped


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
        return gpio_value_file
