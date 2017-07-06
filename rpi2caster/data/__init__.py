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
