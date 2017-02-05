# -*- coding: utf-8 -*-
"""Line length and character width module"""
from .rpi2caster import UI, CFG
from .constants import UNITS

DEFAULT_UNIT = CFG.get_option('measurement_unit')
DEFAULT_MEASURE = CFG.get_option('default_measure')


def parse_measure(raw_string=''):
    """Parse the entered value with units; return the value and unit"""
    # Safeguard against giving a 0, '', None - use default value instead
    if not raw_string:
        raw_string = DEFAULT_MEASURE
    # Sanitize the input value
    string = ''.join(x for x in str(raw_string) if x.isalnum() or x in ',.')
    # Determine and strip the unit
    for symbol in UNITS:
        # End after first match
        if string.endswith(symbol):
            string = string.replace(symbol, '')
            unit = symbol
            break
    else:
        unit = DEFAULT_UNIT
    # Filter the string to remove all letters, round the value to 2
    num_string = ''.join(x for x in string if x.isdigit() or x in '.,')
    value = round(float(num_string), 2)
    return (value, unit)


def enter(input_value='', what='galley width'):
    """Enter the line length, choose measurement units
    (for e.g. British or European measurement system).
    Return length in DTP points."""
    def unit_help():
        """Display a help text about available units"""
        text = ('\n\nAvailable units:\n'
                '    dd - European Didot point,\n'
                '    cc - cicero (=12dd, .1776"),\n'
                '    ff - Fournier point,\n'
                '    cf - Fournier cicero (=12ff, .1628"),\n'
                '    pp - TeX / US printer\'s pica point,\n'
                '    Pp - TeX / US printer\'s pica (=12pp, .1660"),\n'
                '    pt - DTP / PostScript point = 1/72",\n'
                '    pc - DTP / PostScript pica (=12pt, .1667"),\n'
                '    ", in - inch;   '
                'mm - millimeter;   cm - centimeter\n\n')
        UI.display(text)

    prompt = 'Enter the %s value and unit (or "?" for help)' % what
    value, unit = parse_measure(input_value)
    default_value = '%s%s' % (value, unit)
    while True:
        # If 0, use default
        raw_string = UI.enter_data_or_default(prompt, default_value)
        if '?' in raw_string:
            # Display help message and start again
            unit_help()
            continue
        try:
            return parse_measure(raw_string)
        except (TypeError, ValueError):
            UI.display('Incorrect value - enter again...')


class Measure(object):
    """Chooses and represents a line length"""
    default_value, default_unit = parse_measure()

    def __init__(self, context, value='', what='galley width',
                 manual_choice=False):
        self.context = context
        # Enter the value manually if needed
        if manual_choice:
            value, unit = enter(value, what)
        else:
            value, unit = parse_measure(value)
        # Convert the parsed value to DTP points
        self.points = value * UNITS.get(unit)

    def __str__(self):
        return '%s%s' % (self.default_unit_width, DEFAULT_UNIT)

    @property
    def default_unit_width(self):
        """Get a value in default units specified in configuration"""
        # Get the coefficient for calculation
        factor = 1 / UNITS.get(DEFAULT_UNIT, 1)
        return round(self.points * factor, 2)

    @property
    def ems(self):
        """Gets the number of ems of specified set width"""
        return round(self.points / self.context.wedge.set_width, 2)

    @property
    def wedge_set_units(self):
        """Calculates the line length in wedge's units"""
        return round(self.points / self.context.wedge.unit_point_width, 2)
