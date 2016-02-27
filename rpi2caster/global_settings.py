# -*- coding: utf-8 -*-
"""Global settings for rpi2caster"""

from . import text_ui

# User interface we use (text, web etc.)
UI = text_ui
# Conffile path
CONFIG_PATH = '/etc/rpi2caster.conf'
# SQLite3 database path
DATABASE_PATH = '/var/local/rpi2caster/rpi2caster.db'
# Comment symbols for parsing
COMMENT_SYMBOLS = ['**', '*', '//', '##', '#']
# GPIO settings
# Inputs for the casting interface
EMERGENCY_STOP_GPIO = 22
SENSOR_GPIO = 17
# Default hardware interface output data
MCP0 = 0x20
MCP1 = 0x21
PIN_BASE = 65
