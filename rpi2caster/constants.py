# -*- coding: utf-8 -*-
"""Constants shared between modules in the rpi2caster package"""
from collections import OrderedDict

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

# Measurement units for line length
UNITS = OrderedDict({'pc': 12.0, 'pt': 1.0,
                     'Pp': 12*0.166/0.1667, 'pp': 0.166/0.1667,
                     'cc': 12*0.1776/0.1667, 'dd': 0.1776/0.1667,
                     'cf': 12*0.1628/0.1667, 'ff': 0.1628/0.1667,
                     'cm': 0.3937*72, 'mm': 0.03937*72, '"': 72.0, 'in': 72.0})
