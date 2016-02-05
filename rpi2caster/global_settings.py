# -*- coding: utf-8 -*-
"""Global settings for rpi2caster"""

from rpi2caster import text_ui

# User interface we use (text, web etc.)
USER_INTERFACE = text_ui
# Displays debug info in user interfaces
USER_INTERFACE.DEBUG_MODE = False
# Default caster name
CASTER_NAME = 'Monotype Composition Caster'
# Conffile path
CONFIG_PATH = '/etc/rpi2caster.conf'
# SQLite3 database path
DATABASE_PATH = '/var/local/rpi2caster/rpi2caster.db'
# Comment symbols for parsing
COMMENT_SYMBOLS = ['**', '*', '//', '##', '#']
