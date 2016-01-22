# -*- coding: utf-8 -*-
"""Constants shared between modules in the rpi2caster package"""

# Build a sequence of Monotype signals as they appear on the paper tower
SIGNALS = ([x for x in 'NMLKJIHGFSED'] + ['0075'] + [x for x in 'CBA'] +
           [str(x) for x in range(1, 15)] + ['0005', 'O15'])
# Default hardware interface output data
MCP0 = 0x20
MCP1 = 0x21
PIN_BASE = 65
# Signals corresponding to MCP0 A0...A7, B0...B7, MCP1 A0...A7, B0...B7
ALNUM_ARR = ('1,2,3,4,5,6,7,8,9,10,11,12,13,14,0005,'
             '0075,A,B,C,D,E,F,G,H,I,J,K,L,M,N,S,O15')
# Inputs for the casting interface
EMERGENCY_STOP_GPIO = 24
SENSOR_GPIO = 17

# For parsing lines in ribbon files
COMMENT_SYMBOLS = ['**', '*', '//', '##', '#']

# Config file locations
DEFAULT_CONFIG_PATHS = ['/etc/rpi2caster.conf', 'data/rpi2caster.conf']
# Useful for config files
TRUE_ALIASES = ['true', 'on', 'yes']
FALSE_ALIASES = ['false', 'off', 'no']

# Database file locations
DEFAULT_DATABASE_PATHS = ['/var/rpi2caster/monotype.db',
                          '/var/rpi2caster/rpi2caster.db',
                          'data/rpi2caster.db']

# S5 wedge unit arrangement
S5 = ('', 5, 6, 7, 8, 9, 9, 9, 10, 10, 11, 12, 13, 14, 15, 18, 18)

# Column numbers in 15x17 diecase
COLUMNS_15 = [x for x in 'ABCDEFGHIJKLMNO']
COLUMNS_17 = ['NI', 'NL'] + COLUMNS_15
