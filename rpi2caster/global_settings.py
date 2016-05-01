# -*- coding: utf-8 -*-
"""Global settings for rpi2caster"""
from . import text_ui as UI
from click import get_app_dir

# Conffile path
APPDIR = get_app_dir('rpi2caster', force_posix=True, roaming=True)
CONFIG_PATH = APPDIR + '/rpi2caster.conf'
# SQLite3 database path
DATABASE_PATH = APPDIR + '/rpi2caster.db'
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
