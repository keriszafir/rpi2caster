# -*- coding: utf-8 -*-
"""Static data for rpi2caster: unit arrangements, wedge definitions,
letter frequencies for different languages etc."""
from json import loads
from pkg_resources import resource_string as rs

SOURCE = 'rpi2caster.data'


def get_data(name):
    """Get the resource from a JSON-encoded file"""
    return loads(rs(SOURCE, '{}.json'.format(name)).decode())

# Unit arrangement dictionary: {UA_ID: {style1: {char1: unit_value1...}...}...}
UNIT_ARRANGEMENTS = get_data('unit_arrangements')
# Letter frequencies dictionary: {LANG: {char1: freq1...}...}
LETTER_FREQUENCIES = get_data('char_freqs')
# Wedge definitions: {WEDGE_SERIES: [row1_units, row2_units...]...}
WEDGE_DEFINITIONS = get_data('wedge_units')
WEDGE_ALIASES = ('10E: UK S527', '10L: UK S536', '11Q: UK S574',
                 '14E: UK S1406', '1A: UK S207', '1B: UK S209',
                 '1C: UK S210', '1O: UK S221', '1R: UK S223',
                 '1Q: UK S224', '2A: UK S233', '2Z: UK S261',
                 '3O: UK S275', '3Q: UK S277', '3Y: UK S286',
                 '4A: UK S295', '4G: UK S300', '5P: UK S327',
                 '5V: UK S371', '7J: UK S422', '7Z: UK S449',
                 '8A: UK S450', '8U: UK S409', 'TW: S535 typewriter',
                 'AK: EU S5', 'BO: EU S221', 'CZ: EU S336',
                 'A: UK S5', 'D: UK S46', 'E: UK S92',
                 'F: UK S94', 'G: UK S93', 'J: UK S101',
                 'K: UK S87', 'L: UK S96', 'M: UK S45',
                 'N: UK S88', 'O: UK S111', 'Q: UK S50',
                 'S: UK S197', 'V: UK S202', 'W: UK S205', 'X: UK S47')

# Typefaces by series - their names, styles
TYPEFACES = get_data('typefaces')
# Help and documentation
HELP = get_data('help')
# Easter egg
EASTER_EGG = """
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                   _                              _    ║
    ║    /\___/\       __   __     __   |    __  _ __       __   __    |    ║
    ║   |       |     /  \ /  \   /  \ -+-  |  \ |/  \     /  \ /  \  -+-   ║
    ║  _  *   *  _   |      __ |  \__   |   +--/ |        |      __ |  |    ║
    ║  -   /_\   -   |     /  \|     \  |   |    |        |     /  \|  |    ║
    ║      ---        \__/_\__/\__\__/___\_/ \__/|_        \__/_\__/\___\_  ║
    ║                                                                       ║
    ║ Hello Kitty!              gives your MONOTYPE nine lives              ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """
