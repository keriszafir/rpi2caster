# -*- coding: utf-8 -*-
"""Constants shared between modules in the rpi2caster package"""

# Build a sequence of Monotype signals as they appear on the paper tower
SIGNALS = ([x for x in 'NMLKJIHGFSED'] + ['0075'] + [x for x in 'CBA'] +
           [str(x) for x in range(1, 15)] + ['0005', 'O15'])

# Column numbers in 15x17 diecase
COLUMNS_15 = [x for x in 'ABCDEFGHIJKLMNO']
COLUMNS_17 = ['NI', 'NL'] + COLUMNS_15

# For parsing lines in ribbon files
COMMENT_SYMBOLS = ['**', '*', '//', '##', '#']
ASSIGNMENT_SYMBOLS = ['=', ':', ' ']

# Useful for config files (all aliases must be lowercase)
TRUE_ALIASES = ['true', 'on', 'yes', '1']
FALSE_ALIASES = ['false', 'off', 'no', '0']
