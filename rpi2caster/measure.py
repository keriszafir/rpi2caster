# -*- coding: utf-8 -*-
"""Line length and character width module"""
from .rpi2caster import UI, CFG


class Measure(object):
    """Chooses and represents a line length"""
    default_unit = CFG.get_option('default_unit')
    default_value = CFG.get_option('default_measure')
    symbols = ['pc', 'pt', 'Pp', 'pp', 'cc', 'dd', 'cf', 'ff',
               'cm', 'mm', 'in', '"']
    units = {'pc': 12.0, 'pt': 1.0,
             'Pp': 12*0.166/0.1667, 'pp': 0.166/0.1667,
             'cc': 12*0.1776/0.1667, 'dd': 0.1776/0.1667,
             'cf': 12*0.1628/0.1667, 'ff': 0.1628/0.1667,
             'cm': 0.3937*72, 'mm': 0.03937*72, '"': 72.0, 'in': 72.0}

    def __init__(self, context, value='', unit='',
                 what='galley width', manual_choice=False):
        self.context = context
        value = value or Measure.default_value
        unit = unit or Measure.default_unit
        try:
            if manual_choice or value is None:
                raise ValueError
            string = '%s%s' % (value, unit)
            self.points = parse_value(string)
        except (TypeError, ValueError, AttributeError):
            self.points = enter(value, unit, what)

    def __str__(self):
        return '%s%s' % (self.default_unit_width, Measure.default_unit)

    @property
    def default_unit_width(self):
        """Get a value in default units specified in configuration"""
        # Get the coefficient for calculation
        factor = 1 / Measure.units.get(Measure.default_unit, 1)
        return round(self.points * factor, 2)

    @property
    def ems(self):
        """Gets the number of ems of specified set width"""
        return round(self.points / self.context.wedge.set_width, 2)

    @property
    def wedge_set_units(self):
        """Calculates the line length in wedge's units"""
        return round(self.points / self.context.wedge.unit_point_width, 2)


def enter(value=0, unit=Measure.default_unit, what='galley width'):
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
    value = value or Measure.default_value
    default_value = '%s%s' % (value, unit)
    while True:
        # If 0, use default
        raw_string = UI.enter_data_or_default(prompt, default_value)
        if '?' in raw_string:
            # Display help message and start again
            unit_help()
            continue
        try:
            return parse_value(raw_string)
        except (TypeError, ValueError):
            UI.display('Incorrect value - enter again...')


def parse_value(raw_string):
    """Parse the entered value with units"""
    factor = 1
    string = raw_string.strip()
    for symbol in Measure.symbols:
        # End after first match
        if string.endswith(symbol):
            string = string.replace(symbol, '')
            # Default unit - 1pt
            factor = Measure.units.get(symbol, 1)
            break
    else:
        factor = Measure.units.get(Measure.default_unit, 1)
    # Filter the string
    string.replace(',', '.')
    num_string = ''.join(x for x in string if x.isdigit() or x is '.')
    # Convert the value with known unit to DTP points
    points = float(num_string) * factor
    return round(points, 2)
