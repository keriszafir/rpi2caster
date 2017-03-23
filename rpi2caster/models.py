# -*- coding: utf-8 -*-
"""models - all data models for diecases, ribbons"""

from collections import OrderedDict
from contextlib import suppress
from copy import copy
import json
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
from . import constants as c, exceptions as e, parsing as p
from . import unit_arrangements as ua, wedge_unit_values as wu
from .misc import PubSub, singleton
from .global_config import Config
from .styles import StylesCollection
# rpi2caster configuration, message queue, decl. base
CFG, MQ, BASE = Config(), PubSub(), declarative_base()


class LayoutSize:
    """Layout size structure. Monotype matrix cases come in three sizes:
        15x15 (oldest), 15x17 (introduced in 1925, very common) and 16x17
        (introduced in 1950s/60s, newest and largest).
        Monophoto and Monomatic systems were even larger, but they're rare
        and not supported by this software."""

    def __init__(self, rows=15, columns=17, *_):
        self.rows = 16 if rows > 15 else 15
        self.columns = 17 if rows >= 16 or columns > 15 else 15

    def __iter__(self):
        return (x for x in (self.rows, self.columns,
                            self.row_numbers, self.column_numbers))

    def __repr__(self):
        return '<LayoutSize: %s rows, %s columns>' % (self.rows, self.columns)

    def __call__(self):
        return self

    @property
    def row_numbers(self):
        """A tuple of row numbers"""
        return tuple(range(1, self.rows + 1))

    @row_numbers.setter
    def row_numbers(self, row_numbers):
        """Row numbers setter"""
        with suppress(TypeError):
            self.rows = 16 if len(row_numbers) > 15 else 15

    @property
    def column_numbers(self):
        """A tuple of column numbers."""
        return (c.COLUMNS_17 if self.columns > 15 or self.rows > 15
                else c.COLUMNS_15)

    @column_numbers.setter
    def column_numbers(self, column_numbers):
        """Column numbers setter."""
        with suppress(TypeError):
            self.columns = 17 if len(column_numbers) > 15 else 15

    @property
    def positions(self):
        """Gets all matrix positions for this layout"""
        return ((x, y) for y in self.row_numbers for x in self.column_numbers)


class DiecaseLayout:
    """Matrix case layout and outside characters data structure.
    layout - a tuple/list of tuples/lists denoting matrices:
        [(char, styles_string, position, units),...]
    diecase - a Diecase() class object

    Mats without position (None or empty string) will end up in the
    outside characters collection."""
    layout_dict, outside_mats = {}, []

    def __init__(self, layout=None, diecase=None):
        try:
            self.json_encoded = layout
        except (TypeError, json.JSONDecodeError):
            self.raw = layout
        self.diecase = diecase

    def __call__(self):
        return self

    def __repr__(self):
        return ('<DiecaseLayout diecase_id: %s, size: %s rows, %s columns>'
                % (self.diecase.diecase_id, self.size.rows, self.size.columns))

    def __iter__(self):
        return (mat for mat in self.layout_dict.values())

    def __contains__(self, obj):
        return obj in self.layout_dict.values()

    @property
    def diecase(self):
        """Diecase class object associated with this layout"""
        return self.__dict__.get('_diecase')

    @diecase.setter
    def diecase(self, diecase):
        """Diecase to use this layout with"""
        self.__dict__['_diecase'] = diecase
        for mat in self.all_mats:
            mat.diecase = diecase

    @property
    def size(self):
        """Get the LayoutSize for this diecase layout."""
        rows = len({row for (_, row) in self.layout_dict})
        columns = len({column for (column, _) in self.layout_dict})
        return LayoutSize(rows=rows, columns=columns)

    @size.setter
    def size(self, size):
        """Resize the diecase layout"""
        self.resize(*size)

    @property
    def all_mats(self):
        """A list of all matrices - both used and outside"""
        return list(self.layout_dict.values()) + self.outside_mats

    @property
    def styles(self):
        """Get all available character styles from the diecase layout."""
        return sum(mat.styles for mat in self.all_mats
                   if not mat.styles.use_all)

    @property
    def charset(self, diecase_chars=True, outside_chars=False):
        """Diecase character set"""
        charset = {}
        used = list(self.layout_dict.values()) if diecase_chars else []
        unused = self.outside_mats if outside_chars else []
        for mat in used + unused:
            for style in mat.styles:
                charset.setdefault(style, {})[mat.char] = mat
        return charset

    @property
    def raw(self):
        """Raw layout i.e. list of tuples with matrix parameters"""
        in_diecase = [mat.get_record() for mat in self.all_mats]
        outside = [mat.get_record(pos=False) for mat in self.outside_mats]
        return in_diecase + outside

    @raw.setter
    def raw(self, raw_layout):
        """Sort the raw layout into matrices in diecase and outside chars.
        Accepts any iterator of (char, style_string, position, units)"""
        try:
            # Get matrices from supplied layout's canonical form
            mats = [Matrix(char=char, styles=styles, pos=pos,
                           units=units, diecase=self)
                    for (char, styles, pos, units) in raw_layout]
            size = LayoutSize(p.parse_layout_size(raw_layout))
        except (TypeError, ValueError):
            # Layout supplied is incorrect; can't update it
            mats, size = [], LayoutSize(15, 17)
        # Build empty layout determining its size
        layout_dict = self.get_clean_layout(*size)
        # Fill it with matrices for existing positions
        for mat in mats[:]:
            position = mat.column, mat.row
            if layout_dict.get(position):
                layout_dict[position] = mat
                mats.remove(mat)
        # The remaining mats will be stored in outside layout
        self.layout_dict = layout_dict
        self.outside_mats = mats

    @property
    def json_encoded(self):
        """JSON-encoded list of tuples denoting matrices in the diecase."""
        return json.dumps(self.raw)

    @json_encoded.setter
    def json_encoded(self, layout_json):
        """Parse a JSON-encoded list to read a layout"""
        self.raw = json.loads(layout_json)

    def get_clean_layout(self, rows=15, columns=17, *_):
        """Generate an empty layout of a given size."""
        # get coordinates to iterate over and build dict keys
        layout_size = LayoutSize(rows, columns)
        new_layout = OrderedDict().fromkeys(layout_size.positions)
        # fill it with new empty matrices and define low/high spaces
        for position in new_layout:
            mat = Matrix(char='', styles='*', diecase=self.diecase)
            mat.column, mat.row = position
            if position in c.DEFAULT_LOW_SPACE_POSITIONS:
                mat.is_low_space = True
            elif position in c.DEFAULT_HIGH_SPACE_POSITIONS:
                mat.is_high_space = True
            new_layout[position] = mat
        return new_layout

    def purge(self):
        """Resets the layout to an empty one of the same size"""
        self.outside_mats = []
        self.layout_dict = self.get_clean_layout(self.size)

    def resize(self, rows=15, columns=17):
        """Rebuild the layout to adjust it to the new diecase format"""
        # manipulate data structures locally
        old_layout = self.layout_dict
        new_layout = self.get_clean_layout(rows, columns)
        # new list of outside characters
        old_extras = self.outside_mats
        new_extras = []
        # preserve mats as outside characters when downsizing the layout
        for position, mat in old_layout.items():
            if new_layout.get(position):
                # the new layout has a position for this matrix
                new_layout[position] = mat
            else:
                # no place for it = put it in outside chars
                new_extras.append(mat)
        # pull the mats from outside layout to diecase automatically
        # if so, remove them from outside layout
        for mat in old_extras[:]:
            position = (mat.column, mat.row)
            if new_layout.get(position):
                # there is something at this position
                new_layout[position] = mat
                old_extras.remove(mat)
        # finally update the instance attributes
        self.layout_dict = new_layout
        self.outside_mats = old_extras + new_extras

    def select_many(self, char=None, styles=None, position=None, units=None,
                    is_low_space=None, is_high_space=None):
        """Get all matrices with matching parameters"""
        def match(matrix):
            """Test the matrix for conditions unless they evaluate to False"""
            # guard against returning True if no conditions are valid
            retval = any((char, styles, position, units,
                          is_low_space, is_high_space))
            for attr, value in ((matrix.char, char),
                                (matrix.styles, styles),
                                (matrix.pos, position),
                                (matrix.units, units),
                                (matrix.is_low_space, is_low_space),
                                (matrix.is_high_space, is_high_space)):
                if value and attr != value:
                    # end right away on first mismatch = speed up
                    return False
            # all conditions match
            return retval

        results = [mat for mat in self.layout_dict.values() if match(mat)]
        return results

    def select_one(self, char=None, styles=None, position=None, units=None,
                   is_low_space=None, is_high_space=None):
        """Get a matrix with denoted parameters"""
        candidates = self.select_many(char, styles, position, units,
                                      is_low_space, is_high_space)
        try:
            mat = candidates[0]
            return mat
        except IndexError:
            raise e.MatrixNotFound

    def get_space(self, units=6, low=True):
        """Find a suitable space in the diecase layout"""
        high = not low
        space = self.select_one(units=units,
                                is_low_space=low, is_high_space=high)
        space.units = units
        return space

    def select_row(self, row_number):
        """Get all matrices from a given row"""
        row_num = int(row_number)
        return [mat for (_, row), mat in self.layout_dict.items()
                if row == row_num]

    def select_column(self, column):
        """Get all matrices from a given column"""
        column_name = column.upper()
        return [mat for (col, _), mat in self.layout_dict.items()
                if col == column_name]

    def by_rows(self):
        """Get all matrices row by row"""
        rows = [n + 1 for n in range(self.size.rows)]
        return [self.select_row(row) for row in rows]

    def by_columns(self):
        """Get all matrices column by column"""
        columns = c.COLUMNS_17 if self.size.columns == 17 else c.COLUMNS_15
        return [self.select_column(column) for column in columns]


class Diecase(BASE):
    """Diecase: matrix case attributes and operations"""
    __tablename__ = 'matrix_cases'
    diecase_id = sa.Column('diecase_id', sa.Text, primary_key=True)
    typeface = sa.Column('typeface', sa.Text)
    _wedge_name = sa.Column('wedge_name', sa.Text,
                            nullable=False, default='S5-12E')
    _ua_mappings = sa.Column('unit_arrangements', sa.Text)
    _layout_json = sa.Column('layout', sa.Text, nullable=False)

    def __iter__(self):
        return iter(self.matrices)

    def __repr__(self):
        return ('<Diecase: diecase_id: %s typeface: %s>'
                % (self.diecase_id, self.typeface))

    def __str__(self):
        return self.diecase_id

    def __bool__(self):
        return bool(self.diecase_id)

    def __call__(self):
        return self

    @property
    def matrices(self):
        """Gets an iterator of mats, read-only, immutable"""
        return (mat for mat in self.layout)

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
        return self.layout.styles

    @property
    def unit_arrangements(self):
        """Unit arrangements for each style"""
        # raw: {'r': 53, 'b': 123} etc
        raw_mapping = json.loads(self._ua_mappings or "{}")
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
        # store it as '{"r": 53, "b": 123}'
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

    @property
    def layout(self):
        """Diecase layout model based on _layout_json.
        If needed, lazily initialize the empty layout."""
        layout = self.__dict__.get('_layout')
        if not layout:
            layout = DiecaseLayout(self._layout_json, self)
            self.__dict__['_layout'] = layout
        return layout

    @layout.setter
    def layout(self, layout_object):
        """Set the diecase layout object"""
        self.__dict__['_layout'] = layout_object

    @orm.reconstructor
    def load_layout(self, layout=None):
        """Build a DiecaseLayout() and store it on init"""
        new_layout = layout or self._layout_json
        self.layout = DiecaseLayout(layout=new_layout, diecase=self)

    def store_layout(self):
        """Save the layout canonical form to ORM"""
        self._layout_json = self.layout.json_encoded


class Matrix(object):
    """A class for single matrices - all matrix data"""
    def __init__(self, **kwargs):
        self.diecase = kwargs.get('diecase')
        self.char = kwargs.get('char', '')
        self.styles = StylesCollection(kwargs.get('styles', 'a'))
        self.pos = kwargs.get('code') or kwargs.get('pos', '')
        self.units = kwargs.get('units', 0)

    def __len__(self):
        return len(self.char)

    def __bool__(self):
        return True

    def __repr__(self):
        return ('Matrix: %s (%s %s %s units wide)'
                % (self.pos, self.char, self.styles.names, self.units))

    def __str__(self):
        return ''.join([self.code, '   //  ', self.comment])

    @property
    def code(self):
        """Code present in ribbon"""
        if self.column and self.row:
            s_signal = 'S' if self.units != self.get_row_units() else ''
            return ''.join([self.column, s_signal, self.row])
        else:
            return ''

    @code.setter
    def code(self, code):
        """Alternative to self.pos"""
        self.pos = code

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
        return self.__dict__.get('_char') or ''

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
                 self.get_units_from_arrangement() or self.get_row_units())
        return units

    @units.setter
    def units(self, units):
        """Sets the unit width value. Do nothing with non-int values"""
        with suppress(TypeError):
            self.__dict__['_units'] = int(units)

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
        return self.__dict__.get('_row')

    @row.setter
    def row(self, value):
        """Sets the row number"""
        if value:
            with suppress(TypeError, ValueError):
                value = int(value)
                if value in range(1, 17):
                    self.__dict__['_row'] = value
        else:
            self.__dict__['_row'] = None

    @property
    def column(self):
        """Gets the matrix column"""
        return self.__dict__.get('_column')

    @column.setter
    def column(self, value):
        """Sets the column"""
        column = str(value).upper()
        if column in c.COLUMNS_17:
            self.__dict__['_column'] = column
        else:
            self.__dict__['_column'] = None

    @property
    def pos(self):
        """Gets the matrix code"""
        if self.column and self.row:
            return '%s%s' % (self.column, self.row)
        else:
            return ''

    @pos.setter
    def pos(self, code_string):
        """Sets the coordinates for the matrix"""
        self.column, self.row = p.get_coordinates(code_string)

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
            self.char, self.styles = ' ', ''

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
            self.char, self.styles = '_', ''

    @property
    def is_space(self):
        """Check if it's a low or high space"""
        return self.is_low_space or self.is_high_space

    @is_space.setter
    def is_space(self, value):
        """Default low space"""
        if value:
            self.char, self.styles = ' ', ''

    def get_row_units(self):
        """Gets a number of units for characters in the diecase row"""
        # Try wedges in order:
        # diecase's temporary wedge, diecase's default wedge, standard S5-12E
        try:
            return self.diecase.wedge.units[self.row]
        except (TypeError, IndexError):
            return 0

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
        try:
            for style, ua_id in self.diecase.unit_arrangements.items():
                if style in self.styles:
                    with suppress(AttributeError, TypeError,
                                  KeyError, ValueError,
                                  e.UnitArrangementNotFound,
                                  e.UnitValueNotFound):
                        return ua.get_unit_value(ua_id, self.char, self.styles)
        except AttributeError:
            return 0

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

    def get_record(self, pos=True):
        """Returns a record suitable for JSON-dumping and storing in DB."""
        return (self.char, self.styles.string,
                self.pos if pos else '', self.units)


class Ribbon(BASE):
    """Ribbon objects - no matter whether files or database entries.

    A ribbon has the following attributes:
    description, customer - strings
    diecase_id (diecase is selected automatically on casting, so user can e.g.
                view the layout or know which wedge to use)
    contents - series of Monotype codes

    Methods:
    choose_ribbon - choose ribbon automatically or manually,
        first try to get a ribbon with ribbon_id, and if that fails
        ask and select ribbon manually from database, and if that fails
        ask and load ribbon from file
    read_from_file - select a file, parse the metadata, set the attributes
    export_to_file - store the metadata and contents in text file
    store_in_db - store the metadata and contents in db
    set_[description, customer, diecase_id] - set parameters manually"""
    __tablename__ = 'ribbons'
    ribbon_id = sa.Column('ribbon_id', sa.Text, primary_key=True,
                          default='New Ribbon')
    description = sa.Column('description', sa.Text, default='')
    customer = sa.Column('customer', sa.Text, default='')
    diecase_id = sa.Column('diecase_id', sa.Text,
                           sa.schema.ForeignKey('matrix_cases.diecase_id'))
    wedge_name = sa.Column('wedge_name', sa.Text, default='', nullable=False)
    contents = sa.Column('contents', sa.Text, default='', nullable=False)

    def __iter__(self):
        return iter(self.contents)

    def __next__(self):
        yield from self.contents

    def __repr__(self):
        return self.ribbon_id or ''

    def __bool__(self):
        return bool(self.contents)

    def __call__(self):
        return self

    @property
    def parameters(self):
        """Gets a list of parameters"""
        return [(self.ribbon_id, 'Ribbon ID'),
                (self.description, 'Description'),
                (self.customer, 'Customer'),
                (self.diecase_id, 'Matrix case ID'),
                (self.wedge_name, 'Wedge')]

    def update(self, source=None):
        """Updates the object attributes with a dictionary"""
        # Allow to use this method to initialize a new empty ribbon
        if not source:
            source = {}
        with suppress(AttributeError):
            self.ribbon_id = source.get('ribbon_id', '')
            self.description = source.get('description', '')
            self.customer = source.get('customer', '')
            self.diecase_id = source.get('diecase_id', '')
            self.wedge_name = source.get('wedge_name', '')
            self.contents = source.get('contents', [])

    def import_from_file(self, ribbon_file):
        """Imports ribbon from file, parses parameters, sets attributes"""
        def get_value(line, symbol):
            """Helper function - strips whitespace and symbols"""
            # Split the line on an assignment symbol, get the second part,
            # strip any whitespace or multipled symbols
            return line.split(symbol, 1)[-1].strip(symbol).strip()

        try:
            # Try to open that and get only the lines containing non-whitespace
            with ribbon_file:
                raw_data = (line.strip() for line in ribbon_file.readlines())
                ribbon = [line for line in raw_data if line]
        except AttributeError:
            return False
        # What to look for
        keywords = ['diecase', 'description', 'desc', 'diecase_id', 'customer',
                    'wedge', 'stopbar']
        targets = ['diecase_id', 'description', 'description', 'diecase_id',
                   'customer', 'wedge_name', 'wedge_name']
        parameters = dict(zip(keywords, targets))
        # Metadata (anything found), contents (the rest)
        metadata = {}
        contents = []
        # Look for parameters line per line, get parameter value
        # If parameters exhausted, append the line to contents
        for line in ribbon:
            for keyword, target in parameters.items():
                if line.startswith(keyword):
                    for sym in c.ASSIGNMENT_SYMBOLS:
                        if sym in line:
                            # Data found
                            metadata[target] = get_value(line, sym)
                            break
                    break
            else:
                contents.append(line)
        # We need to add contents too
        metadata['contents'] = contents
        # Update the attributes with what we found
        self.update(metadata)
        return True

    def export_to_file(self, ribbon_file):
        """Exports the ribbon to a text file"""
        # Choose file, write metadata, write contents
        with ribbon_file:
            ribbon_file.write('description: ' + self.description)
            ribbon_file.write('customer: ' + self.customer)
            ribbon_file.write('diecase: ' + self.diecase_id)
            ribbon_file.write('wedge: ' + self.wedge_name)
            for line in self.contents:
                ribbon_file.write(line)


class Wedge(object):
    """Default S5-12E wedge, unless otherwise specified"""
    series = '5'
    set_width = 12.0

    def __init__(self, wedge_name=''):
        if wedge_name:
            self.name = wedge_name

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Wedge: %s>' % self.name

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
        return 0.1667 if self.is_brit_pica else 0.166

    @property
    def name(self):
        """Gets a wedge name - for example S5-12.25E.
        S (for stopbar) is prepended by convention.
        E is appended whenever the wedge is based on pica = .1667".
        """
        # Avoid displaying ".0" in non-fractional set widths
        s_w = int(self.set_width) if not self.set_width % 1 else self.set_width
        name = 'S%s-%s%s' % (self.series, s_w, self.is_brit_pica * 'E')
        return name

    @name.setter
    def name(self, wedge_name):
        """Parse the wedge name to get series, set width, unit values
        and whether the wedge is British pica."""
        data = {}
        try:
            # For countries that use comma as decimal delimiter,
            # convert to point:
            wedge_name = wedge_name.replace(',', '.').upper().strip()
            # Check if this is an European wedge
            # (these were based on pica = .1667" )
            data['is_brit_pica'] = wedge_name.endswith('E')
            # Away with the initial S, final E and any spaces before and after
            # Make it work with space or dash as delimiter
            wedge = wedge_name.strip('SE ').replace('-', ' ').split(' ')
            series, raw_set_w = wedge
            data['series'] = series
            # get the set width i.e. float approximated to .25
            set_w_str = ''.join(x for x in raw_set_w
                                if x.isnumeric() or x is '.')
            data['set_width'] = float(set_w_str) // 0.25 * 0.25
            # try to get the unit values, otherwise S5
            data['units'] = wu.UNITS.get(series, wu.S5)
            # update the attributes
            self.update(data)
        except (TypeError, AttributeError, ValueError):
            # In case parsing goes wrong
            raise ValueError('Cannot parse wedge name %s' % wedge_name)

    @property
    def is_brit_pica(self):
        """If True, the wedge is based on .1667" pica (1/12")
        i.e. old British pica, currently used in PostScript/DTP.

        If False, the wedge is based on .166" pica a.k.a. new British pica
        or American (ATF) pica, the same as used in TeX/LaTeX nowadays.

        Also see https://en.wikipedia.org/wiki/Pica_(typography)
        for clarification."""
        return self.__dict__.get('_is_brit_pica', True)

    @is_brit_pica.setter
    def is_brit_pica(self, value):
        """Set the is_brit_pica flag to given value evaluated to bool."""
        self.__dict__['_is_brit_pica'] = True if value else False

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
        units = self.__dict__.get('_units') or wu.S5
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
        return [round(self.unit_point_width * units, 2)
                for units in self.units]

    @property
    def unit_point_width(self):
        """Gets the factor for converting points to units and vice versa"""
        return self.set_width * self.pica / 3

    @property
    def unit_inch_width(self):
        """Get inch value of a wedge's set unit; 1 inch = 72 points"""
        return self.unit_point_width / 72

    @property
    def em_inch_width(self):
        """Get inch width of an em, i.e. 18 units"""
        return self.unit_inch_width * 18

    @property
    def adjustment_limits(self):
        """Get the unit adjustment limits for this wedge"""
        # The unit width adjustment range is limited by 0075 and 0005
        # wedge positions (min. 1/1, max. 15/15 for low spaces,
        # but less for characters - the mould has a limiter which allows
        # the upper blade to open much less than the lower blade;
        # the matrix size is .2" x .2", anything larger will lead to a splash)
        # Normal (unadjusted) position is 3/8, so we can take away 2/7
        # or add 12/7. One step of 0075 wedge is equal to 15 steps of 0005.
        # So, we can take away 2*15+7=37, or add 12*15+7=187 steps,
        # each is 0.0005" = 1/2000", so -0.0185...+0.0935
        # The increment / decrement is absolute i.e. will mean different
        # numbers of units depending on set width. Let's calculate this.
        shrink_units = 0.0185 / self.unit_inch_width
        stretch_units = 0.0935 / self.unit_inch_width
        return (shrink_units, stretch_units)

    def update(self, source):
        """Update parameters with a dictionary of values"""
        with suppress(AttributeError):
            self.series = source.get('series') or self.series
            self.set_width = source.get('set_width') or self.set_width
            self.is_brit_pica = source.get('is_brit_pica') or self.is_brit_pica
            self.units = source.get('units') or self.units


@singleton
class Database(object):
    """Database object sitting on top of SQLAlchemy"""
    Session = orm.sessionmaker()

    def __init__(self, url='', echo=False):
        self.session, self.engine = None, None
        self.url = url or CFG.get_option('url', 'database')
        self.echo = echo
        MQ.subscribe(self, 'database')
        self.make_session()

    @property
    def query(self):
        """Query the session"""
        return self.session.query

    def get_diecase(self, diecase_id):
        """Get one diecase with given id; otherwise return empty"""
        try:
            objs = self.query(Diecase).filter(Diecase.diecase_id == diecase_id)
            return objs.one()
        except orm.exc.NoResultFound:
            return Diecase(diecase_id=diecase_id)

    def get_ribbon(self, ribbon_id):
        """Get one diecase with given id; otherwise return empty"""
        try:
            objs = self.query(Ribbon).filter(Ribbon.ribbon_id == ribbon_id)
            return objs.one()
        except orm.exc.NoResultFound:
            return Ribbon(ribbon_id=ribbon_id)

    def update(self, source=None):
        """Update the connection parameters"""
        if source:
            self.url = source.get('url') or self.url
            # turn the sqlalchemy echo (i.e. debug) mode on or off
            self.echo = source.get('debug', self.echo)
            self.make_session()

    def make_session(self):
        """Allows to create a new database session"""
        self.engine = sa.create_engine(self.url, echo=self.echo)
        self.Session.configure(bind=self.engine)
        BASE.metadata.create_all(bind=self.engine)
        self.session = self.Session()
