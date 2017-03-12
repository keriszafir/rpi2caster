# -*- coding: utf-8 -*-
"""Module containing functions for diecase retrieval and parsing,
diecase storing, parameter searches.
"""
# File operations
import json
from copy import copy
from contextlib import suppress
from sqlalchemy import Column, Text
# Some functions raise custom exceptions
from . import exceptions as e
# Constants module
from . import constants as c
# Parsing module
from . import parsing as p
# Unit arrangement handling
from . import unit_arrangements as ua
# Styles manager
from .styles import StylesCollection
# Wedge operations for several matrix-case management functions
from .wedge_data import Wedge
# User interface, configuration and database backends
from .database import Base
from .rpi2caster import UI, MQ


SPACE_NAMES = {'   ': 'low em quad', '  ': 'low en quad', ' ': 'low space',
               '___': 'high em quad', '__': 'high en quad', '_': 'high space'}


class Diecase(Base):
    """Diecase: matrix case attributes and operations"""
    __tablename__ = 'matrix_cases'
    diecase_id = Column('diecase_id', Text, primary_key=True)
    typeface = Column('typeface', Text)
    _wedge_name = Column('wedge', Text, nullable=False, default='S5-12E')
    _ua_mappings = Column('unit_arrangements', Text)
    _layout = Column('layout', Text, nullable=False)
    _outside_chars = Column('outside_characters', Text)

    def __init__(self, **kwargs):
        MQ.subscribe(self, 'diecase_updates')
        self.update(kwargs)

    def __iter__(self):
        return iter(self.matrices)

    def __repr__(self):
        return '<diecase: %s %s>' % (self.diecase_id, self.typeface)

    def __bool__(self):
        return bool(self.diecase_id)

    @property
    def matrices(self):
        """Gets an iterator of mats, read-only, immutable"""
        # first check if we have matrices cache
        # this will save us from generating it all anew
        cached = self.__dict__.get('_matrices')
        if cached:
            return (x for x in cached)
        else:
            # no cache - need to check if we have the diecase layout in store
            mats = [Matrix(char=char, styles=styles, code=code,
                           units=units, diecase=self)
                    for (char, styles, code, units) in self.layout]
            # cache the generated sequence
            self.__dict__['_matrices'] = mats
            return (x for x in self.__dict__['_matrices'])

    @matrices.setter
    def matrices(self, matrices):
        """Sets a collection of matrices"""
        self.__dict__['_matrices'] = [mat for mat in matrices]

    @property
    def charset(self):
        """Diecase character set"""
        charset = {}
        for mat in self.matrices:
            for style in mat.styles:
                try:
                    charset[style][mat.char] = mat
                except KeyError:
                    # Initialize the empty style dictionary
                    charset[style] = {}
                    charset[style][mat.char] = mat
        return charset

    @property
    def outside_chars(self):
        """Outside characters i.e. matrices defined for this diecase, but
        stored outside (because they don't fit in etc.)."""
        # outside layout is stored as:
        # [(char1, styles1, units1), (char2, styles2, units2)...]
        raw_outside_chars = json.loads(self._outside_chars)
        return [(char, StylesCollection(stylestring), units)
                for (char, stylestring, units) in raw_outside_chars]

    @outside_chars.setter
    def outside_chars(self, outside_chars):
        """Set the outside/additional chars for the diecase"""
        raw_outside_chars = [(char, styles.string, units)
                             for (char, styles, units) in outside_chars]
        self._outside_chars = json.dumps(raw_outside_chars)

    @property
    def spaceset(self):
        """Return an iterator of all spaces, low and high"""
        symbols = {' ': 5, '  ': 9, '   ': 18, '_': 5, '__': 9, '___': 18}
        return {symbol: Space(width=units, diecase=self,
                              is_low_space=' ' in symbol)
                for symbol, units in symbols.items()}

    @property
    def layout(self):
        """Gets a diecase layout as a list of lists"""
        layout_15_17 = (('', '', '%s%s' % (column, row), self.wedge[row])
                        for row in (num + 1 for num in range(15))
                        for column in c.COLUMNS_17)
        return json.loads(self._layout) or [rec for rec in layout_15_17]

    @layout.setter
    def layout(self, layout):
        """Translates the layout to a list of matrix objects"""
        if layout:
            self.matrices = []
            self._layout = json.dumps(layout)

    @property
    def parameters(self):
        """Gets a list of parameters"""
        return [(self.diecase_id, 'Diecase ID'),
                (self.typeface, 'Typeface'),
                (self.wedge, 'Assigned wedge')]

    @property
    def styles(self):
        """Parses the diecase layout and gets available typeface styles.
        Returns a list of them."""
        return sum(mat.styles for mat in self if not mat.styles.use_all)

    @property
    def unit_arrangements(self):
        """Unit arrangements for each style"""
        # raw: {'r': 53, 'b': 123} etc
        raw_mapping = json.loads(self._ua_mappings)
        # needs to be: {Roman: 53, Bold: 123}
        return {StylesCollection(stylestring): ua_number
                for stylestring, ua_number in raw_mapping.items()}

    @unit_arrangements.setter
    def unit_arrangements(self, unit_arrangements):
        """Set a dict of unit arrangements for styles in the diecase"""
        try:
            # u_a with style classes as keys: {Roman: 53, Bold: 123}
            raw_mapping = {style.string: ua_number
                           for style, ua_number in unit_arrangements}
        except AttributeError:
            # u_a with stylestrings as keys: {'r': 53, 'b': 123}
            raw_mapping = unit_arrangements
        # store it as {'r': 53, 'b': 123}
        self._ua_mappings = json.dumps(raw_mapping)

    @property
    def wedge(self):
        """Get a wedge based on wedge name stored in database"""
        cached_wedge = self.__dict__.get('_wedge')
        if cached_wedge:
            return cached_wedge
        else:
            # instantiate and store in cache until changed
            wedge = Wedge(self._wedge_name)
            self.__dict__['_wedge'] = wedge
            return wedge

    @wedge.setter
    def wedge(self, wedge):
        """Set a different wedge"""
        with suppress(AttributeError, TypeError):
            self.__dict__['_wedge'] = wedge
            self._wedge_name = wedge.name

    def update(self, source):
        """Update the attributes with data found in the source"""
        try:
            UI.display('Processing diecase data...', min_verbosity=2)
            self.diecase_id = source.get('diecase_id') or self.diecase_id
            self.typeface = source.get('typeface') or self.typeface
            wedge_name = source.get('wedge_name')
            self.wedge = Wedge(wedge_name) if wedge_name else self.wedge
            self.layout = source.get('layout') or self.layout
            self.outside_characters = (source.get('outside_characters') or
                                       self.outside_characters)
            self.unit_arrangements = (source.get('unit_arrangements') or
                                      self.unit_arrangements)
        except AttributeError:
            UI.display('Cannot process the diecase data - wrong source',
                       min_verbosity=1)
            UI.display(source, min_verbosity=1)

    def decode_matrix(self, code):
        """Finds the matrix based on the column and row in layout"""
        matrices = (mat for mat in self.matrices
                    if mat.pos.upper() == code.upper())
        try:
            mat = next(matrices)
        except StopIteration:
            mat = Matrix(pos=code.upper(), diecase=self)
        return mat


class Matrix(object):
    """A class for single matrices - all matrix data"""
    def __init__(self, **kwargs):
        print(kwargs)
        self.diecase = kwargs.get('diecase') or Diecase()
        self.char = kwargs.get('char', '')
        self.styles = StylesCollection(kwargs.get('styles', 'r'))
        self.pos = kwargs.get('code') or kwargs.get('pos') or 'O15'
        self.units = kwargs.get('units') or self.get_row_units()

    def __len__(self):
        return len(self.char)

    def __bool__(self):
        return True

    def __repr__(self):
        return self.pos

    def __str__(self):
        return ''.join([self.code, '   //  ', self.comment])

    @property
    def code(self):
        """Code present in ribbon"""
        s_signal = 'S' if self.units != self.get_row_units() else ''
        return ''.join([self.column, s_signal, self.row])

    @property
    def comment(self):
        """Generate a comment based on matrix character and style."""
        comment = (' // low space %.2f points wide' % self.points
                   if self.is_low_space
                   else ' // high space %.2f points wide' % self.points
                   if self.is_high_space
                   else ' // %s %s' % (self.styles.names, self.char)
                   if self.char else '')
        return comment

    def __call__(self, units):
        """Returns a copy of self with a corrected width"""
        new_mat = copy(self)
        new_mat.units += units
        return new_mat

    @property
    def char(self):
        """Matrix character"""
        return self.get_char()

    @char.setter
    def char(self, char):
        """Set the matrix character"""
        self.__dict__['_char'] = char

    @property
    def units(self):
        """Gets the specific or default number of units"""
        # If units are assigned to the matrix, return the value
        # Otherwise, wedge default
        units = (self.__dict__.get('_units', 0) or
                 self.get_units_from_arrangement() or
                 self.diecase.wedge.units[self.row])
        return units

    @units.setter
    def units(self, units):
        """Sets the unit width value"""
        if units:
            self.__dict__['_units'] = units

    @property
    def ems(self):
        """Get the ems for matrix; 1em = 18 units"""
        return round(self.units / 18, 2)

    @property
    def points(self):
        """Gets a DTP point (=.1667"/12) width for the matrix"""
        return round(self.diecase.wedge.unit_point_width * self.units, 2)

    @property
    def row(self):
        """Gets the row number"""
        return self.__dict__.get('_row', 15)

    @row.setter
    def row(self, value):
        """Sets the row number"""
        value = int(value)
        if value in range(1, 17):
            self.__dict__['_row'] = value

    @property
    def column(self):
        """Gets the matrix column"""
        return self.__dict__.get('_column', 'O')

    @column.setter
    def column(self, value):
        """Sets the column"""
        column = value.upper()
        if column in c.COLUMNS_17:
            self.__dict__['_column'] = column
        else:
            self.__dict__['_column'] = 'O'

    @property
    def pos(self):
        """Gets the matrix code"""
        return '%s%s' % (self.column, self.row)

    @pos.setter
    def pos(self, code_string):
        """Sets the coordinates for the matrix"""
        signals = p.parse_signals(code_string)
        self.row = p.get_row(signals)
        self.column = p.get_column(signals)

    @property
    def styles(self):
        """Get the matrix's styles or an empty string if matrix has no char"""
        if self.is_space or not self.char:
            # all styles no matter what
            return StylesCollection()
        else:
            return StylesCollection(self.__dict__.get('_styles'))

    @styles.setter
    def styles(self, styles):
        """Sets the matrix's style string"""
        try:
            self.__dict__['_styles'] = styles.string
        except AttributeError:
            self.__dict__['_styles'] = StylesCollection(styles).string

    @property
    def is_low_space(self):
        """Checks whether this is a low space: char is present"""
        return self.char.isspace()

    @is_low_space.setter
    def is_low_space(self, value):
        """Update self.char with " " for low spaces"""
        if value:
            self.char = ' '

    @property
    def is_high_space(self):
        """Checks whether this is a high space: "_" is present"""
        # Any number of _ is present, no other characters
        return ('_' in self.char and not
                [x for x in self.char.strip() if x is not '_'])

    @is_high_space.setter
    def is_high_space(self, value):
        """Set the character to _"""
        if value:
            self.char = '_'

    @property
    def is_space(self):
        """Check if it's a low or high space"""
        return self.is_low_space or self.is_high_space

    @is_space.setter
    def is_space(self, value):
        """Ask whether it's a high or low space"""
        if value:
            prompt = 'Y = low space, N = high space?'
            self.char = ' ' if UI.confirm(prompt, True) else '_'

    def get_char(self):
        """Get the matrix character. For spaces, this will be overloaded
        with a custom method."""
        return self.__dict__.get('_char') or ''

    def edit(self):
        """Edits the matrix data"""
        styles = self.styles
        # TODO accommodate spaces here
        char = 'char: "%s"' % self.char if self.char else 'character unknown'
        styles = 'styles: %s ' % styles.names if not styles.use_all else ''
        UI.display('\n' + '*' * 80 + '\n')
        UI.display('%s %s%s, units: %s'
                   % (self.pos, styles, char, self.units))
        self.edit_char()
        self.choose_styles()
        self.specify_units()
        return self

    def edit_char(self):
        """Edit the matrix character"""
        prompt = ('Char? (" ": low / "_": high space, '
                  'blank = keep, ctrl-C to exit)?')
        self.char = UI.enter(prompt,
                             blank_ok=not self.char, default=self.char)

    def edit_code(self):
        """Edit the matrix code"""
        # display char only if matrix is not space and has specified char
        char = self.char
        if char and SPACE_NAMES.get(char) is None:
            ch_str = '"%s"' % char
            # for matrices with all/unspecified styles don't display these
            style_str = (self.styles.names if not self.styles.use_all
                         else '')
        else:
            ch_str = SPACE_NAMES.get(char) or ''
            style_str = ''
        f_str = ' for ' if ch_str or style_str else ''
        # display style string only if char is there
        prompt_list = ['Enter the matrix position', f_str, style_str, ch_str]
        self.pos = UI.enter_data_or_default(''.join(prompt_list), self.pos,
                                            def_word='current')

    def specify_units(self):
        """Give a user-defined unit value for the matrix;
        mostly used for matrices placed in a different row than the
        unit arrangement indicates; this will make the program set the
        justification wedges and cast the character with the S-needle"""
        desc = '"%s" at ' % self.char if self.char else ''
        ua_units = self.get_units_from_arrangement()
        row_units = self.get_row_units()
        if ua_units:
            UI.display('%s%s unit values: %s by UA, %s by row'
                       % (desc, self.pos, ua_units, row_units))
            prompt = 'New unit value? (0 = UA units, blank = current)'
        else:
            UI.display('%s%s row unit value: %s' % (desc, self.pos, row_units))
            prompt = 'New unit value? (0 = row units, blank = current)'
        self.units = UI.enter_data_or_default(prompt, self.units, float)

    def choose_styles(self):
        """Choose styles for the matrix"""
        styles = self.styles
        styles.choose()
        self.styles = styles

    def get_row_units(self):
        """Gets a number of units for characters in the diecase row"""
        # Try wedges in order:
        # diecase's temporary wedge, diecase's default wedge, standard S5-12E
        return self.diecase.wedge.units[self.row]

    def get_min_units(self):
        """Gets the minimum unit value for a given wedge, based on the
        matrix row and wedge unit value, for wedges at 1/1"""
        shrink = self.diecase.wedge.adjustment_limits[0]
        return round(max(self.get_row_units() - shrink, 0), 2)

    def get_max_units(self):
        """Gets the minimum unit value for a given wedge, based on the
        matrix row and wedge unit value, for wedges at 1/1"""
        stretch = self.diecase.wedge.adjustment_limits[1]
        full_width = self.get_row_units() + stretch
        width_cap = 20
        return full_width if self.is_low_space else min(full_width, width_cap)

    def get_units_from_arrangement(self):
        """Try getting the unit width value from diecase's unit arrangement,
        if that fails, return 0"""
        retval = 0
        for style, ua_id in self.diecase.unit_arrangements:
            if style in self.styles:
                with suppress(AttributeError, TypeError, KeyError, ValueError,
                              e.UnitArrangementNotFound, e.UnitValueNotFound):
                    retval = ua.get_unit_value(ua_id, self.char, self.styles)
                    break
        return retval

    def wedge_positions(self, unit_correction=0):
        """Calculate the 0075 and 0005 wedge positions for this matrix
        based on the current wedge used"""
        wedge = self.diecase.wedge
        # Units of alternative wedge's set to add or subtract
        diff = self.units + unit_correction - self.get_row_units()
        # The following calculations are done in 0005 wedge steps
        # 1 step = 1/2000"
        steps_0005 = int(diff * wedge.unit_inch_width * 2000) + 53
        # 1 step of 0075 wedge is 15 steps of 0005; neutral positions are 3/8
        # 3 * 15 + 8 = 53, so any increment/decrement is relative to this
        # Add or take away a number of inches; diff is in units of wedge's set
        # Upper limit: 15/15 => 15*15=225 + 15 = 240
        # Unsafe for casting from mats - .2x.2 size - larger leads to splash!
        # Adding a high space for overhanging character is the way to do it
        # Space casting is fine, we can open the mould as far as possible
        steps_0005 = min(steps_0005, 240)
        # Lower limit: 1/1 wedge positions => 15 + 1 = 16:
        steps_0005 = max(16, steps_0005)
        steps_0075 = 0
        while steps_0005 > 15:
            steps_0005 -= 15
            steps_0075 += 1
        # Got the wedge positions, return them
        return (steps_0075, steps_0005)

    def get_record(self):
        """Returns a record suitable for JSON-dumping and storing in DB"""
        return [self.char, self.styles.string, self.pos, self.units]


class Space(Matrix):
    """Space - low or high, with a given position"""
    def __init__(self, width='', is_low_space=None, diecase=None):
        super().__init__(diecase=diecase)
        if is_low_space is None:
            self.is_space = True
        else:
            self.is_low_space = is_low_space
        # Enter the space width
        self.specify_width(width)
        try:
            self.closest_match()
        except AttributeError:
            self.pos = 'G1'

    @property
    def get_char(self):
        """Get a character for the space, for compatibility with Matrix"""
        if self.units >= 18:
            # "   " (low) or "___" (high) for em-quads and more
            multiple = 3
        elif self.units >= 9:
            # "  " (low) or "__" (high) for 1/2em...1em
            multiple = 2
        else:
            # " " (low) or "_" (high) for spaces less than 1/2em
            multiple = 1
        return multiple * self.__dict__.get('_char')

    def closest_match(self):
        """Automatically choose a matrix from diecase to get a most
        suitable space for the desired width"""
        def spaces_match(mat):
            """The candidate matrix is a space"""
            return mat.is_space and mat.is_low_space == self.is_low_space

        def can_adjust(mat):
            """The matrix units can be adjusted in -2...+10 range"""
            return mat.units - shrink <= self.units <= mat.units + stretch

        def unit_difference(mat):
            """Unit width difference between desired width and row width"""
            return abs(self.units - mat.units)

        # How many units can we take away or add?
        shrink, stretch = self.diecase.wedge.adjustment_limits
        try:
            matrices = sorted([mat for mat in self.diecase
                               if spaces_match(mat) and can_adjust(mat)],
                              key=unit_difference)
            # The best-matched candidate is the one with least unit difference
            mat = matrices[0]
            self.pos = mat.pos
        except (AttributeError, TypeError, IndexError):
            # No diecase or no matches; use default values
            if self.units >= 18 - shrink:
                self.pos = 'O15'
            elif self.units >= 9:
                self.pos = 'G5'
            else:
                self.pos = 'G1'

    def specify_width(self, width='5u'):
        """Specify the space's width"""
        def parse_value(raw_string):
            """Parse the entered value with units"""
            # By default, use DTP points = 1/72"
            factor = 1
            string = raw_string.strip()
            for symbol in symbols:
                # End after first match
                if string.endswith(symbol):
                    string = string.replace(symbol, '')
                    # Default unit - 1pt
                    factor = meas.get(symbol, 1)
                    break
            # Filter the string
            string.replace(',', '.')
            num_string = ''.join(x for x in string if x.isdigit() or x is '.')
            # Convert the value with known unit to units
            units = float(num_string) * factor
            return round(units, 2)
        try:
            # Point to unit conversion factor
            ptu = 1 / self.diecase.wedge.unit_point_width
        except AttributeError:
            # Assume set width = 12; 18 units is 12 points
            ptu = 1.33
        help_text = ('\n\nAvailable units:\n'
                     '    dd - European Didot point,\n'
                     '    cc - cicero (=12dd, .1776"),\n'
                     '    ff - Fournier point,\n'
                     '    cf - Fournier cicero (=12ff, .1628"),\n'
                     '    pp - TeX / US printer\'s pica point,\n'
                     '    Pp - TeX / US printer\'s pica (=12pp, .1660"),\n'
                     '    pt - DTP / PostScript point = 1/72",\n'
                     '    pc - DTP / PostScript pica (=12pt, .1667"),\n'
                     '    u - unit of wedge\'s set\n'
                     '    en - 9 units of wedge\'s set\n'
                     '    em - 18 units of wedge\'s set\n\n')

        meas = {'pc': 12.0 * ptu, 'pt': 1.0 * ptu,
                'Pp': 12 * 0.166 / 0.1667 * ptu, 'pp': 0.166 / 0.1667 * ptu,
                'cc': 12 * 0.1776 / 0.1667 * ptu, 'dd': 0.1776 / 0.1667 * ptu,
                'cf': 12 * 0.1628 / 0.1667 * ptu, 'ff': 0.1628 / 0.1667 * ptu,
                'u': 1, 'en': 9, 'em': 18}
        symbols = ['pc', 'pt', 'Pp', 'pp', 'cc', 'dd', 'cf', 'ff',
                   'en', 'em', 'u']
        prompt = 'Enter the space width value and unit (or "?" for help)'
        while True:
            if width is None:
                raw_string = UI.enter_data_or_default(prompt, '1en')
            elif not width:
                # If 0, use default 5 units
                raw_string = '9u'
            else:
                raw_string = str(width)
            if '?' in raw_string:
                # Display help message and start again
                UI.display(help_text)
            try:
                self.units = parse_value(raw_string)
                return
            except (TypeError, ValueError):
                UI.display('Incorrect value - enter again...')
                raw_string = None
