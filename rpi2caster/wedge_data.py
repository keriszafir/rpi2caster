# -*- coding: utf-8 -*-
"""Wedge data model for rpi2caster"""
from itertools import zip_longest
# Default user interface
from .global_settings import UI
# Constants for known normal wedge unit values
from . import wedge_unit_values as wu


class Wedge(object):
    """Default S5-12E wedge"""
    def __init__(self, wedge_name='', manual_choice=False):
        if wedge_name or manual_choice:
            self.name = wedge_name
        else:
            # Default S5-12E
            self.series = '5'
            self.set_width = 12
            self.is_brit_pica = True
            self.units = wu.S5

    def __repr__(self):
        return self.name

    def __getitem__(self, row):
        return self.units[row]

    def __bool__(self):
        return True

    @property
    def pica(self):
        """Get the pica value for the wedge. Can be .1667" (old British)
        or .166" (new British; American). The .1667" was commonly used with
        wedges made for European markets (wedge designation series-setE).
        Curiously, the old British pica is the same as modern DTP pica."""
        return self.is_brit_pica and 0.1667 or 0.166

    @property
    def em_width(self):
        """Get the wedge em width (i.e. 18 units of wedge's set) in inches"""
        return self.pica * self.set_width / 12

    @property
    def name(self):
        """Gets a wedge name - for example S5-12.25E.
        S (for stopbar) is prepended by convention.
        E is appended whenever the wedge is based on pica = .1667".
        """
        # Avoid displaying ".0" in non-fractional set widths
        if self.set_width % 1 == 0:
            set_width = int(self.set_width)
        else:
            set_width = self.set_width
        name = 'S%s-%s%s' % (self.series, set_width, self.is_brit_pica * 'E')
        return name

    @name.setter
    def name(self, wedge_name=None):
        """Defines a wedge based on designation.
        Recognizes many new-style (numeric) names, like S5-12 or 5-12,
        and some old-style (alphabetic) names, like AK, BO etc.
        For unknown wedges, the user has to enter the values manually."""
        # Ask for wedge name and set width as it is written on the wedge
        al_it = iter(wu.ALIASES)
        # Group by three
        grouper = zip_longest(al_it, al_it, al_it, fillvalue='')
        old_wedges = '\n'.join('\t'.join(z) for z in grouper)
        prompt = ('\nSome old-style wedge designations:\n\n%s'
                  '\n\nIf you have one of those, enter number (like S5-xx.yE).'
                  '\n\nWedge designation?' % old_wedges)
        wedge_name = wedge_name or UI.enter_data_or_default(prompt, 'S5-12')
        # For countries that use comma as decimal delimiter, convert to point:
        wedge_name = wedge_name.replace(',', '.').upper().strip()
        # Check if this is an European wedge
        # (these were based on pica = .1667" )
        is_brit_pica = wedge_name.endswith('E')
        # Away with the initial S, final E and any spaces before and after
        # Make it work with space or dash as delimiter
        wedge = wedge_name.strip('SE ').replace('-', ' ').split(' ')
        try:
            (series, set_width) = wedge
        except ValueError:
            series = wedge[0]
            set_width = None
        # Now get the set width - ensure that it is float divisible by 0.25
        # no smaller than 5 (narrowest type), no wider than 20 (large comp)
        while True:
            try:
                set_width = float(set_width)
                if not set_width % 0.25 and 5 <= set_width <= 20:
                    break
                else:
                    raise ValueError
            except (TypeError, ValueError):
                prompt = ('Enter the set width as a decimal fraction '
                          'divisible by 0.25 - e.g. 12.25: ')
                set_width = UI.enter_data(prompt, float)
        # We have the wedge name, so we can look the wedge up in known wedges
        # (no need to enter the unit values manually)
        units = wu.UNITS.get(series, None)
        while not units:
            # Enter manually if not found:
            prompt = ('Enter the wedge unit values for rows 1...15 '
                      'or 1...16, separated by commas.\n')
            # Now we need to be sure that all whitespace is stripped,
            # and the value written to database is a list of integers
            try:
                units = [int(i.strip())
                         for i in UI.enter_data(prompt).split(',')]
                # Display warning if the number of steps is not
                # 15 or 16 (15 is most common, 16 was used for HMN and KMN).
                if not 15 <= len(units) <= 16:
                    UI.display('Wedge must have 15 or 16 steps - enter again.')
                    units = None
            except ValueError:
                UI.display('Incorrect value - enter the values again.')
                units = None
        # Finally set the collected data
        self.series = series
        self.set_width = set_width
        self.is_brit_pica = is_brit_pica
        self.units = units

    @property
    def parameters(self):
        """Gets a list of parameters"""
        return [(self, 'Wedge designation'),
                ('%.4f"' % self.pica, 'Pica base is'),
                (' '.join([str(x) for x in self.units if x]),
                 'Row unit values for this wedge')]

    @property
    def units(self):
        """Gets the unit values for the wedge's rows"""
        units = self.__dict__.get('_units', None) or wu.S5
        # Add 0 at the beginning so that the list can be indexed with
        # row numbers - i.e. units[1] for row 1
        if units[0] is not 0:
            units = [0] + units
        # Ensure that wedge has 0 + 16 steps - i.e. length is 17
        # Keep adding the last value until we have enough
        while len(units) < 17:
            units.append(units[-1])
        return units

    @units.setter
    def units(self, units):
        """Sets the wedge unit values"""
        self.__dict__['_units'] = units

    @property
    def points(self):
        """Gets the point values for the wedge's rows"""
        return [round(self.units_to_points_factor * units, 2)
                for units in self.units]

    @property
    def units_to_points_factor(self):
        """Gets the factor for converting points to units and vice versa"""
        return self.set_width * self.pica / 18 / 0.1667
