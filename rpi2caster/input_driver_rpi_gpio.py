# -*- coding: utf-8 -*-
"""RPi.GPIO input driver for rpi2caster"""

import RPi.GPIO as GPIO
from .rpi2caster import CFG
from .exceptions import MachineStopped
from .monotype import SensorBase
from .misc import singleton
SENSOR_GPIO = CFG.get_option('sensor_gpio')
BOUNCE_TIME = CFG.get_option('input_bounce_time')


@singleton
class RPiGPIOSensor(SensorBase):
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
        done = False
        while not done:
            try:
                channel = GPIO.wait_for_edge(self.gpio, change,
                                             timeout=timeout*1000,
                                             bouncetime=BOUNCE_TIME)
                if channel is None:
                    raise MachineStopped
                else:
                    done = True
            except RuntimeError:
                # In case RuntimeError: Error waiting for edge is raised...
                pass
            except (KeyboardInterrupt, EOFError):
                # Emergency stop by keyboard
                raise MachineStopped
