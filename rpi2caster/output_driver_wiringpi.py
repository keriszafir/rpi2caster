# -*- coding: utf-8 -*-
"""
output_driver_wiringpi - wiringPi2-based output driver for MCP23017
"""

# WiringPi2 Python bindings: essential for controlling the MCP23017!
try:
    import wiringpi2 as wiringpi
except ImportError:
    print('You must install wiringpi2!')
# Import mockup output driver from monotype
from .monotype import OutputDriver
from .exceptions import WrongConfiguration, NotConfigured
from .constants import ALNUM_ARR, MCP0, MCP1, PIN_BASE
from . import cfg_parser


# Read configuration
try:
    SIGS = cfg_parser.get_config('SignalsArrangements',
                                 'signals_arrangement').upper()
except NotConfigured:
    SIGS = ALNUM_ARR


class MCP23017Interface(OutputDriver):
    """A 32-channel control interface based on two MCP23017 chips"""
    def __init__(self, mcp0_address=MCP0, mcp1_address=MCP1,
                 pin_base=PIN_BASE, sig_arr=SIGS):
        super().__init__(pin_base=pin_base, sig_arr=sig_arr)
        self.name = 'MCP23017 driver using wiringPi2-Python library'
        # Set up an output interface on two MCP23017 chips
        wiringpi.mcp23017Setup(pin_base, mcp0_address)
        wiringpi.mcp23017Setup(pin_base + 16, mcp1_address)
        # Set all I/O lines on MCP23017s as outputs - mode=1
        for pin in self.pin_numbers.values():
            wiringpi.pinMode(pin, 1)

    def one_on(self, sig):
        """Looks a signal up in arrangement and turns it on"""
        try:
            wiringpi.digitalWrite(self.pin_numbers[sig], 1)
        except KeyError:
            raise WrongConfiguration('Signal %s not defined!' % sig)

    def one_off(self, sig):
        """Looks a signal up in arrangement and turns it off"""
        try:
            wiringpi.digitalWrite(self.pin_numbers[sig], 0)
        except KeyError:
            raise WrongConfiguration('Signal %s not defined!' % sig)
