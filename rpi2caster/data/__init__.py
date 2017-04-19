# -*- coding: utf-8 -*-
"""Static data for rpi2caster: unit arrangements, wedge definitions,
letter frequencies for different languages etc."""
from json import loads
from pkg_resources import resource_string as rs

SOURCE = 'rpi2caster.data'

# Unit arrangement dictionary: {UA_ID: {style1: {char1: unit_value1...}...}...}
UNIT_ARRANGEMENTS = loads(rs(SOURCE, 'unit_arrangements.json').decode())
# Letter frequencies dictionary: {LANG: {char1: freq1...}...}
LETTER_FREQUENCIES = loads(rs(SOURCE, 'char_freqs.json').decode())
# Wedge definitions: {WEDGE_SERIES: [row1_units, row2_units...]...}
WEDGE_DEFINITIONS = loads(rs(SOURCE, 'wedge_units.json').decode())
# Help and documentation
HELP = loads(rs(SOURCE, 'help.json').decode())
