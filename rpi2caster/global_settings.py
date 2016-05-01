# -*- coding: utf-8 -*-
"""Global settings for rpi2caster"""
from click import get_app_dir
from . import text_ui as UI

# Conffile path
APPDIR = get_app_dir('rpi2caster', force_posix=True, roaming=True)
CONFIG_PATH = APPDIR + '/rpi2caster.conf'
# SQLite3 database path
DATABASE_PATH = APPDIR + '/rpi2caster.db'
# Display debug data
UI.debug_info('Application data directory: %s' % APPDIR)
UI.debug_info('User config file: %s' % CONFIG_PATH)
UI.debug_info('User database file: %s' % DATABASE_PATH)
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
