# -*- coding: utf-8 -*-
"""RPi.GPIO input driver for rpi2caster"""

import RPi.GPIO as GPIO
from .global_config import SENSOR_GPIO
from .exceptions import MachineStopped
from .monotype import SensorMixin


class RPiGPIOSensor(SensorMixin):
    """Simple RPi.GPIO input driver for photocell"""
    def __init__(self, gpio=SENSOR_GPIO):
        super().__init__()
        self.name = 'RPi.GPIO input driver'
        self.gpio = gpio
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio, GPIO.IN)

    def __del__(self):
        GPIO.cleanup(self.gpio)

    @property
    def parameters(self):
        """Gets a list of parameters"""
        return [(self.name, 'Sensor driver'),
                (self.gpio, 'GPIO number')]

    def wait_for(self, new_state, timeout=5, *_):
        """Use interrupt handlers in RPi.GPIO for triggering the change"""
        change = GPIO.RISING if new_state else GPIO.FALLING
        channel = GPIO.wait_for_edge(self.gpio, change)
        if channel is None:
            raise MachineStopped
        else:
            return True
