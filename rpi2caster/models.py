# -*- coding: utf-8 -*-
"""Fundamental models for rpi2caster, not depending on database.
Classes-only module. All constants come from definitions."""

import json
from collections import namedtuple, OrderedDict
from pkg_resources import resource_string as rs

# some named tuples for easier attribute addressing
WedgeLimits = namedtuple('WedgeLimits', 'shrink stretch')
Matrix = namedtuple('Matrix', 'column row units row_units code wedges')
ParsedRecord = namedtuple('ParsedRecord',
                          ('raw signals comment column row has_signals is_char'
                           ' uses_row_16 has_0005 has_0075 has_s_needle '
                           'is_pump_start is_pump_stop is_newline'))

# constant wedge definitions data

# Wedge definitions: {WEDGE_SERIES: [row1_units, row2_units...]...}
WEDGES_JSON = rs('rpi2caster.data', 'wedge_units.json').decode()
WEDGE_DEFINITIONS = json.loads(WEDGES_JSON)
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


class Wedge:
    """Default S5-12E wedge, unless otherwise specified"""
    __slots__ = ('series', 'set_width', 'is_brit_pica', '_units')
    S5 = [5, 6, 7, 8, 9, 9, 9, 10, 10, 11, 12, 13, 14, 15, 18]
    definitions = WEDGE_DEFINITIONS
    aliases = WEDGE_ALIASES

    def __init__(self, wedge_name='', wedge_data=None):
        w_data = wedge_data or {}
        if wedge_name:
            self.name = wedge_name
        else:
            self.series = w_data.get('series', '5')
            self.set_width = w_data.get('set_width', 12.0)
            self.is_brit_pica = w_data.get('is_brit_pica', True)
            self._units = w_data.get('units', Wedge.S5)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Wedge: {}>'.format(self.name)

    def __getitem__(self, row):
        return self.units[row]

    def __bool__(self):
        return True

    @property
    def pica(self):
        """Get the pica base of the wedge. Two values were used:
            .1667" (old British pica, European wedges), also: DTP pica,
            .1660" (new British, American), also: TeX pica."""
        return 0.1667 if self.is_brit_pica else 0.166

    @property
    def name(self):
        """Gets a wedge name - for example S5-12.25E.
        S (for stopbar) is prepended by convention.
        E is appended whenever the wedge is based on pica = .1667".
        """
        # Truncate the fractional part of the set width if it's an integer
        set_w = self.set_width if self.set_width % 1 else int(self.set_width)

        name = 'S{series}-{set_width}{european_suffix}'
        return name.format(series=self.series, set_width=set_w,
                           european_suffix=self.is_brit_pica * 'E')

    @name.setter
    def name(self, wedge_name):
        """Parse the wedge name to get series, set width, unit values
        and whether the wedge is British pica."""
        if not wedge_name:
            # use default S5
            return
        try:
            # For countries that use comma as decimal delimiter,
            # convert to point:
            wedge_name = str(wedge_name).replace(',', '.').upper().strip()
            # Check if this is an European wedge
            # (these were based on pica = .1667" )
            is_brit_pica = wedge_name.endswith('E')
            # Away with the initial S, final E and any spaces before and after
            # Make it work with space or dash as delimiter
            wedge = wedge_name.strip('SE ').replace('-', ' ').split(' ')
            series, raw_set_w = wedge
            # get the set width i.e. float approximated to .25
            set_w_str = ''.join(x for x in raw_set_w
                                if x.isnumeric() or x == '.')
            set_width = float(set_w_str) // 0.25 * 0.25
            if set_width > 25:
                raise ValueError
            # try to get the unit values, otherwise S5
            units = WEDGE_DEFINITIONS.get(series, Wedge.S5)
            # update the attributes
            self.series, self.set_width = series, set_width
            self.is_brit_pica, self.units = is_brit_pica, units
        except (TypeError, AttributeError, ValueError):
            # In case parsing goes wrong
            raise ValueError('Cannot parse wedge name {}'.format(wedge_name))

    @property
    def parameters(self):
        """Gets a list of parameters"""
        em_inches = round(self.pica * self.set_width / 12, 5)
        parameters = OrderedDict()
        parameters['Wedge designation'] = self.name
        parameters['Inch width of 18 units [1em]'] = em_inches
        parameters['Units per row'] = ' '.join(str(x) for x in self.units if x)
        return parameters

    @property
    def units(self):
        """Gets the unit values for the wedge's rows"""
        units = self._units or Wedge.S5
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
        self._units = units

    def units_to_inches(self, units=1):
        """Convert units to inches, based on wedge's set width and pica def"""
        return round(units / 18 * self.set_width / 12 * self.pica, 4)

    def inches_to_units(self, inches=1):
        """Convert inches to units"""
        return round(18 * inches / self.pica * 12 / self.set_width, 2)

    def get_adjustment_limits(self):
        """Get the unit adjustment limits for this wedge.
        Without adjustment, the character has the same width as if the
        wedges were at 3/8.

        lower limit is reached at 1/1 0075 and 0005 wedge positions,
        max shrink is 3/8 - 1/1 = 2/7 => 2 * 0.0075 + 7 * 0.0005 = 0.0185"

        upper limit is reached at 15/15,
        max stretch is 15/15 - 3/8 = 12/7 => 12 * 0.0075 + 7 * 0.0005 = 0.0935"

        Constraints:
            Single-cell matrices have max .18" width for safety.
            Double-cell (large composition, wide characters) are .38"
            Otherwise the mould opening would not be covered by the matrix,
            leading to lead splashing over the diecase.

            Low spaces don't have this constraint as the upper mould blade
            prevents the lead from even reaching the diecase.

        Calculate this to wedge set units.
        Return positive integers.
        """
        # upper limit based on parameters
        stretch_inches = 0.0935
        cap = 0.18
        maximum = min(stretch_inches, cap)
        # calculate adjustment range in units
        shrink = int(18 * 12 * 0.0185 / self.pica / self.set_width)
        stretch = int(18 * 12 * maximum / self.pica / self.set_width)
        return WedgeLimits(shrink, stretch)

    def corrections(self, row, units):
        """Calculate the 0075 and 0005 wedge positions for this matrix
        based on the current wedge used.

        matrix - a Matrix object
        correction - units of self.wedge's set to add/subtract,
        units - arbitrary character width in units of self.wedge's set"""
        def steps(unit_width=0):
            """get a width (in .0005" steps) of a character
            for a given number of units or diecase row"""
            inches = unit_width / 18 * self.set_width / 12 * self.pica
            # return a number of 0.0005" steps
            return int(2000 * inches)

        def limits_exceeded():
            """raise an error if width can't be adjusted with wedges"""
            limits = self.get_adjustment_limits()
            minimum = row_units - limits.shrink
            maximum = row_units + limits.stretch
            message = ('{} units exceed adjustment limits (min: {} / max: {})')
            error_msg = message.format(units, minimum, maximum)
            raise ValueError(error_msg)

        # absolute width: how many .0005" steps is it?
        char_width = steps(units)
        # how wide would a character from the given row normally be?
        # (using self.wedge, not self.diecase.wedge!)
        row_units = self[row]
        row_width = steps(row_units)
        # calculate the difference and wedge positions
        # 1 step of 0075 wedge is 15 steps of 0005; neutral positions are 3/8
        # 3 * 15 + 8 = 53, so any increment/decrement is relative to this
        increments = char_width - row_width + 53
        # Upper limit: 15/15 => 15*15=225 + 15 = 240;
        # lower limit:  1/ 1 => 1 * 15 + 1 = 16
        if increments < 16 or increments > 240:
            limits_exceeded()
        # calculate wedge positions from the increments
        pos_0005, pos_0075 = increments % 15, increments // 15
        if not pos_0005:
            # wedge positions cannot be zero
            pos_0005, pos_0075 = 15, pos_0075 - 1
        return (pos_0075, pos_0005)


class Ribbon:
    """Ribbon model for the rpi2caster casting program"""

    def __init__(self, description='', diecase='', wedge='', contents=''):
        self.description = description
        self.diecase = diecase
        self.wedge = wedge
        self.contents = contents

    def __iter__(self):
        return iter(self.contents)

    def __next__(self):
        yield from self.contents

    def __repr__(self):
        return ('<Ribbon: {} diecase: {}, wedge: {}>'
                .format(self.description, self.diecase, self.wedge))

    def __bool__(self):
        return bool(self.contents)

    def __call__(self):
        return self

    @property
    def parameters(self):
        """Gets a list of parameters"""
        parameters = OrderedDict()
        parameters['Description'] = self.description
        parameters['Diecase'] = self.diecase
        parameters['Wedge'] = self.wedge
        return parameters
