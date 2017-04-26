# -*- coding: utf-8 -*-
"""Fundamental models for rpi2caster, not depending on database.
Classes-only module. All constants come from definitions."""

from collections import OrderedDict
from contextlib import suppress
from copy import copy
from functools import singledispatch
from itertools import chain, product
import json
from math import ceil
from . import definitions as d
from .data import LETTER_FREQUENCIES, WEDGE_DEFINITIONS


class Matrix:
    """A class for single matrices - all matrix data"""
    __slots__ = ('char', '_units', 'row', 'column', '_styles', 'diecase')

    def __init__(self, char='', styles='*', pos='', units=0, diecase=None):
        self.diecase = diecase
        self.char = char
        self.row, self.column, self.pos = None, None, pos
        self._units = units
        self._styles = Styles(styles).string

    def __len__(self):
        return 0 if self.isspace() else len(self.char)

    def __bool__(self):
        return True

    def __repr__(self):
        return ('<Matrix: {m.pos} ({m.char} {styles}, {m.units} units wide)>'
                .format(m=self, styles=self.styles.names))

    def __str__(self):
        return '{mat.code}   //   {mat.comment}'.format(mat=self)

    @property
    def code(self):
        """Code present in ribbon"""
        if self.column and self.row:
            s_signal = (self.units != self.get_row_units) * 'S'
            return '{mat.column}{es}{mat.row}'.format(mat=self, es=s_signal)
        else:
            return ''

    @code.setter
    def code(self, code):
        """Alternative to self.pos"""
        self.pos = code

    @property
    def comment(self):
        """Generate a comment based on matrix character and style."""
        retval = ('low space {mat.ems:.2f} ems' if self.islowspace()
                  else 'high space {mat.ems:.2f} ems' if self.ishighspace()
                  else '{mat.char} {mat.styles.names}')
        return retval.format(mat=self)

    def __call__(self, units):
        """Returns a copy of self with a corrected width"""
        new_mat = copy(self)
        new_mat.units += units
        return new_mat

    @property
    def units(self):
        """Gets the specific or default number of units"""
        # If units are assigned to the matrix, return the value
        # Otherwise, wedge default
        return (self._units or self.get_units_from_arrangement() or
                self.get_row_units())

    @units.setter
    def units(self, units):
        """Sets the unit width value. Do nothing with non-int values"""
        with suppress(TypeError):
            self._units = int(units)

    @property
    def ems(self):
        """Get the ems for matrix; 1em = 18 units"""
        return round(self.units / 18, 2)

    @property
    def pos(self):
        """Gets the matrix code"""
        return ('{m.column}{m.row}'.format(m=self) if self.column and self.row
                else '')

    @pos.setter
    def pos(self, codes):
        """Sets the coordinates for the matrix"""
        def row_generator():
            """Generate matching rows, removing them from input sequence"""
            # first is None as the sequence generated will be reversed
            # and None is to be used as a last resort if no row is found
            yield None
            nonlocal sigs
            for number in range(16, 0, -1):
                string = str(number)
                if string in sigs:
                    sigs = sigs.replace(string, '')
                    yield number

        def column_generator():
            """Generate column numbers"""
            nonlocal sigs
            for column in d.COLUMNS_17:
                if column in sigs:
                    sigs = sigs.replace(column, '')
                    yield column
            yield None

        # needs to work with strings and iterables
        try:
            sigs = ''.join(codes).upper()
        except TypeError:
            # in case not every iterable element is a string => convert
            sigs = ''.join(str(l) for l in codes).upper()

        # get a first possible row (caveat: recognize double-digit numbers)
        all_rows = [x for x in row_generator()]
        rows = (x for x in reversed(all_rows))
        # get the first possible column -> NI, NL, A...O
        columns = column_generator()
        self.column, self.row = next(columns), next(rows)

    @property
    def styles(self):
        """Get the matrix's styles or an empty string if matrix has no char"""
        if self.isspace() or not self.char:
            # all styles no matter what
            return Styles('*')
        else:
            return Styles(self._styles)

    @styles.setter
    def styles(self, styles):
        """Sets the matrix's style string"""
        self._styles = Styles(styles).string

    def islowspace(self):
        """Checks whether this is a low space: char is present"""
        return self.char.isspace()

    def set_lowspace(self, value):
        """Update self.char with " " for low spaces"""
        if value:
            self.char = ' '

    def ishighspace(self):
        """Checks whether this is a high space: "_" is present"""
        # Any number of _ is present, no other characters
        return ('_' in self.char and not
                [x for x in self.char.strip() if x is not '_'])

    def set_highspace(self, value):
        """Set the character to _"""
        if value:
            self.char = '_'

    def isspace(self):
        """Check if it's a low or high space"""
        return self.islowspace() or self.ishighspace()

    def get_row_units(self, wedge=None):
        """Gets a number of units for characters in the diecase row"""
        used_wedge = wedge or self.diecase.wedge
        try:
            return used_wedge.units[self.row]
        except (AttributeError, TypeError, IndexError):
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
        return full_width if self.islowspace() else min(full_width, width_cap)

    def get_units_from_arrangement(self):
        """Try getting the unit width value from diecase's unit arrangement,
        if that fails, return 0"""
        for style in self.styles:
            with suppress(UnitValueNotFound, UnitArrangementNotFound):
                arrangement = self.diecase.unit_arrangements.get(style)
                if not arrangement:
                    continue
                return arrangement[self.char]
        return 0

    def wedge_positions(self, unit_correction=0, wedge=None):
        """Calculate the 0075 and 0005 wedge positions for this matrix
        based on the current wedge used"""
        other_wedge = wedge or self.diecase.wedge
        # we need to have the other wedge's units
        # convert unit width to other wedge's value
        conv = wedge.units_to_units(self.units, other_wedge=self.diecase.wedge)
        # Units of alternative wedge's set to add or subtract
        diff = conv + unit_correction - self.get_row_units(wedge=other_wedge)
        # The following calculations are done in 0005 wedge steps
        # 1 step = 1/2000"
        steps_0005 = int(other_wedge.units_to_inches(diff) * 2000) + 53
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
        return d.WedgePositions(steps_0075, steps_0005)

    def get_mat_record(self, pos=True):
        """Returns a record suitable for JSON-dumping and storing in DB."""
        return d.MatrixRecord(self.char, self.styles.string,
                              self.pos if pos else '', self.units)


class Styles:
    """Styles collection grouping styles and allowing for edit.
    styles: any iterable containing styles to parse,
            valid options: r, b, i, s, l, u; (add. sizes: 1, 2, 3, 4, 5)
            a or * denotes all styles.
    """
    definitions = d.STYLES
    __slots__ = ('_styles', 'default')

    def __init__(self, styles='*', default=d.STYLES.roman):
        self._styles = ()
        self._parse(styles, default)

    def __iter__(self):
        return (x for x in self._styles)

    def __str__(self):
        return self.string

    def __repr__(self):
        return '<Styles: {}>'.format(self.string)

    def __add__(self, other):
        if not other:
            return self
        try:
            return Styles(self.string + other.string)
        except AttributeError:
            return Styles(self.string)

    def __radd__(self, other):
        if not other:
            return self
        try:
            return Styles(other.string + self.string)
        except AttributeError:
            return Styles(self.string)

    def __contains__(self, what):
        return what in self._styles or what in self.string

    @property
    def string(self):
        """Return the string of all style short names"""
        return ''.join(style.short for style in self._styles)

    @property
    def names(self):
        """Get the long names of styles"""
        return ('all styles' if self.use_all
                else ', '.join(style.name for style in self._styles))

    @property
    def all_names(self):
        """Get all names including alternatives"""
        names = ('{} ({})'.format(styledef.name, styledef.alternatives)
                 if styledef.alternatives else styledef.name
                 for styledef in self._styles)
        return 'all styles' if self.use_all else ', '.join(names)

    @property
    def use_all(self):
        """Check if the collection has every style"""
        return set(self.string) == set('rbislu')

    @property
    def is_single(self):
        """Check if only one style is in collection"""
        return len(self._styles) == 1

    @property
    def is_default(self):
        """Check if this is a default style and nothing else"""
        return set(self._styles) == {self.default}

    @property
    def first(self):
        """Get the first style from the collection"""
        for style in self._styles:
            return style
        return self.default

    def items(self):
        """Get items - so that the object can be iterated like a dict"""
        return ((style.name, style) for style in self._styles)

    def ansi_format(self, formatted_string):
        """Use ANSI escape sequences to format a string"""
        params = (str(style.ansi) for style in self._styles)
        par_string = ';'.join(params)
        if self.use_all or not par_string:
            return formatted_string
        else:
            start, end = '\033[', '\033[0m'
            return ''.join([start, par_string, 'm', formatted_string, end])

    def _parse(self, raw_data, default=d.STYLES.roman):
        """Parse the source (any iterable) for valid styles
        and update the styles set"""
        def s_collection():
            """Parse all styles in a Styles object or an iterable of styles"""
            with suppress(TypeError, AttributeError):
                return [x.short for x in raw_data]

        def style():
            """A single style is supplied."""
            with suppress(AttributeError):
                return raw_data.short

        def iterable():
            """A string, dict, list, set, tuple, generator etc. is supplied"""
            with suppress(TypeError):
                defs = [style.short for style in self.definitions]
                if '*' in raw_data or 'a' in raw_data:
                    return defs
                return [short for short in defs if short in raw_data]

        source = s_collection() or style() or iterable() or default.short
        # Got the styles string, now make the set
        found = tuple(s for s in self.definitions if s.short in source)
        self._styles, self.default = found, default


class DiecaseLayout:
    """Matrix case layout and outside characters data structure.
    layout : a tuple/list of tuples/lists denoting matrices:
              [(char, styles_string, position, units),...]
    diecase : a Diecase() class object

    Mats without position (None or empty string) will end up in the
    outside characters collection."""
    __slots__ = ('used_mats', 'outside_mats', '_diecase')

    def __init__(self, layout=None, diecase=None):
        self.used_mats, self.outside_mats = {}, []
        self._diecase = diecase
        try:
            self.json_encoded = layout
        except (TypeError, json.JSONDecodeError):
            self.raw = layout

    def __repr__(self):
        return ('<DiecaseLayout ({} rows, {} columns)>'
                .format(self.size.rows, self.size.columns))

    def __iter__(self):
        return (mat for mat in self.used_mats.values())

    def __contains__(self, obj):
        return obj in self.used_mats.values()

    @property
    def diecase(self):
        """Diecase class object associated with this layout"""
        return self._diecase

    @diecase.setter
    def diecase(self, diecase):
        """Diecase to use this layout with"""
        self._diecase = diecase
        for mat in self.all_mats:
            mat.diecase = diecase

    @property
    def size(self):
        """Get the LayoutSize for this diecase layout."""
        rows = len({row for (_, row) in self.used_mats})
        columns = len({column for (column, _) in self.used_mats})
        return LayoutSize(rows=rows, columns=columns)

    @size.setter
    def size(self, size):
        """Resize the diecase layout"""
        self.resize(*size)

    @property
    def all_mats(self):
        """A list of all matrices - both used and outside"""
        return list(self.used_mats.values()) + self.outside_mats

    @property
    def styles(self):
        """Get all available character styles from the diecase layout."""
        return sum(mat.styles for mat in self.all_mats
                   if not mat.styles.use_all)

    @property
    def charset(self, diecase_chars=True, outside_chars=False):
        """Diecase character set"""
        charset = {}
        used = list(self.used_mats.values()) if diecase_chars else []
        unused = self.outside_mats if outside_chars else []
        for mat in used + unused:
            for style in mat.styles:
                charset.setdefault(style, {})[mat.char] = mat
        return charset

    @property
    def raw(self):
        """Raw layout i.e. list of tuples with matrix parameters"""
        in_diecase = [mat.get_mat_record() for mat in self.all_mats]
        outside = [mat.get_mat_record(pos=False) for mat in self.outside_mats]
        return in_diecase + outside

    @raw.setter
    def raw(self, raw_layout):
        """Sort the raw layout into matrices in diecase and outside chars.
        Accepts any iterator of (char, style_string, position, units)"""
        size = LayoutSize(15, 15)
        try:
            # Get matrices from supplied layout's canonical form
            raw_records = (d.MatrixRecord(*record) for record in raw_layout)
            mats = [Matrix(char=rec.char, styles=rec.styles, pos=rec.pos,
                           units=rec.units, diecase=self.diecase)
                    for rec in raw_records]
            # parse the source layout to get its size,
            # reversing the order increases the chance of finding row 16 faster
            for matrix in reversed(mats):
                if matrix.row == 16:
                    # finish here as the only 16-row diecases were 16x17
                    size.rows, size.columns = 16, 17
                    break
                if matrix.column in ('NI', 'NL'):
                    # update the columns number
                    # iterate further because we can still find 16th row
                    size.columns = 17
        except (TypeError, ValueError):
            # Layout supplied is incorrect; use a default size of 15x17
            mats, size.rows, size.columns = [], 15, 17
        # Build empty layout determining its size
        used_mats = self.get_clean_layout(size)
        # Fill it with matrices for existing positions
        for mat in mats[:]:
            pos = mat.column, mat.row
            if used_mats.get(pos):
                used_mats[pos] = mat
                mats.remove(mat)
        # The remaining mats will be stored in outside layout
        self.used_mats, self.outside_mats = used_mats, mats

    @property
    def json_encoded(self):
        """JSON-encoded list of tuples denoting matrices in the diecase."""
        return json.dumps(self.raw)

    @json_encoded.setter
    def json_encoded(self, layout_json):
        """Parse a JSON-encoded list to read a layout"""
        self.raw = json.loads(layout_json)

    def get_clean_layout(self, layout_size):
        """Generate an empty layout of a given size."""
        # get coordinates to iterate over and build dict keys
        new_layout = OrderedDict().fromkeys(layout_size.positions)
        # fill it with new empty matrices and define low/high spaces
        for position in new_layout:
            mat = Matrix(char='', styles='*', diecase=self.diecase)
            mat.column, mat.row = position
            # preset spaces
            mat.set_lowspace(position in d.DEFAULT_LOW_SPACE_POSITIONS)
            mat.set_highspace(position in d.DEFAULT_HIGH_SPACE_POSITIONS)
            new_layout[position] = mat
        return new_layout

    def purge(self):
        """Resets the layout to an empty one of the same size"""
        self.outside_mats = []
        self.used_mats = self.get_clean_layout(self.size)

    def resize(self, rows=15, columns=17):
        """Rebuild the layout to adjust it to the new diecase format"""
        # manipulate data structures locally
        old_layout = self.used_mats
        new_size = LayoutSize(rows, columns)
        new_layout = self.get_clean_layout(new_size)
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
        self.used_mats = new_layout
        self.outside_mats = old_extras + new_extras

    def select_many(self, char=None, styles=None, position=None, units=None,
                    islowspace=None, ishighspace=None):
        """Get all matrices with matching parameters"""
        def match(matrix):
            """Test the matrix for conditions unless they evaluate to False"""
            # guard against returning True if no conditions are valid
            # end right away
            wants = (char, styles, position, units, islowspace, ishighspace)
            if not any(wants):
                return False
            finds = (matrix.char, matrix.styles, matrix.pos, matrix.units,
                     matrix.islowspace(), matrix.ishighspace())
            # check all that apply and break on first mismatch
            for wanted, found in zip(wants, finds):
                if wanted and wanted != found:
                    return False
            # all conditions match
            return True

        results = [mat for mat in self.used_mats.values() if match(mat)]
        return results

    def select_one(self, *args, **kwargs):
        """Get a matrix with denoted parameters"""
        with suppress(IndexError):
            search_results = self.select_many(*args, **kwargs)
            return search_results[0]
        raise MatrixNotFound

    def get_space(self, units=6, low=True):
        """Find a suitable space in the diecase layout"""
        high = not low
        space = self.select_one(units=units, islowspace=low, ishighspace=high)
        space.units = units
        return space

    def select_row(self, row_number):
        """Get all matrices from a given row"""
        row_num = int(row_number)
        return [mat for (_, r), mat in self.used_mats.items() if r == row_num]

    def select_column(self, column):
        """Get all matrices from a given column"""
        col_num = column.upper()
        return [mat for (c, _), mat in self.used_mats.items() if c == col_num]

    def by_rows(self):
        """Get all matrices row by row"""
        return [self.select_row(row) for row in self.size.row_numbers]

    def by_columns(self):
        """Get all matrices column by column"""
        return [self.select_column(col) for col in self.size.column_numbers]


class UnitArrangement:
    """Unit arrangement for a diecase.
    Has two dictionaries:
    {unit_value1: [char1, char2...]...} for getting all chars of given units,
    {char1: unit_value1, char2: unit_value2...} for char unit value lookups.
    """
    __slots__ = ('by_units', 'by_char', 'number', 'variant', 'style')

    def __init__(self, arrangement, number=None, variant=None, style=None):
        def get_char_list(units):
            """make a list of characters with given units"""
            return [c for c, u in by_char.items() if u == units]

        if not arrangement:
            raise UnitArrangementNotFound
        by_char = {c: int(u) for c, u in arrangement.items() if c and u}
        by_units = {units: get_char_list(units) for units in range(4, 22)}
        filtered = {units: chars for units, chars in by_units.items() if chars}
        # store the result
        self.by_char, self.by_units = by_char, filtered
        self.number, self.variant, self.style = number, variant, style

    def __str__(self):
        template = '{ua.font_style.name}: {ua.number} {ua.ua_style.name}'
        return template.format(ua=self)

    def __repr__(self):
        return '<UnitArrangement {}>'.format(self)

    def __getitem__(self, item):
        """Get a unit arrangement for a given style"""
        @singledispatch
        def getter(_):
            """dispatch on type, accept only strings or numeric values"""
            raise TypeError('Unknown type')

        getter.register(int, self.get_chars)
        getter.register(float, self.get_chars)
        getter.register(str, self.get_units)
        return getter(item)

    def get_chars(self, unit_value):
        """Get the characters list for a given unit value"""
        value = int(unit_value)
        return sorted(self.by_units.get(value))

    def get_units(self, char):
        """Get unit value from an arrangement"""
        # first try to look it up in arrangement
        with suppress(KeyError):
            return self.by_char[char]
        # might be an accented version
        char_gen = (l for l, acc in d.ACCENTS.items() if char in acc)
        for unaccented_char in char_gen:
            with suppress(KeyError):
                return self.by_char[unaccented_char]
        # fell off the end of the loop
        raise UnitValueNotFound

    def get_mat_units(self, matrix):
        """Get unit value for a Matrix object"""
        return self.get_units(matrix.char)


class LayoutSize:
    """Layout size class, used for accessing row and column number iterators.

    Layout size structure. Monotype matrix cases come in three sizes:
    15x15 (oldest), 15x17 (introduced in 1925, very common)
    and 16x17 (introduced in 1950s/60s, newest and largest).
    Monophoto and Monomatic systems were even larger, but they're rare
    and not supported by this software.
    """
    __slots__ = ('rows', 'columns')

    def __init__(self, rows=15, columns=17, *_):
        self.rows = 16 if rows > 15 else 15
        self.columns = 17 if rows >= 16 or columns > 15 else 15

    def __iter__(self):
        return self.positions

    def __repr__(self):
        return '<LayoutSize: {s.rows}x{s.columns}>'.format(s=self)

    def __str__(self):
        name = ('HMN, KMN or unit-shift' if self.rows == 16
                else 'NI, NL' if self.columns == 17 else 'small')
        return '{} rows, {} columns - {}'.format(self.rows, self.columns, name)

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
        if self.columns > 15 or self.rows > 15:
            return d.COLUMNS_17
        else:
            return d.COLUMNS_15

    @column_numbers.setter
    def column_numbers(self, column_numbers):
        """Column numbers setter."""
        with suppress(TypeError):
            self.columns = 17 if len(column_numbers) > 15 else 15

    @property
    def positions(self):
        """Gets all matrix positions for this layout"""
        return (x for x in product(self.column_numbers, self.row_numbers))


class Measure:
    """Chooses and represents a line length, space width etc. measures
    which can be expressed in various typographic units (for definition,
    see TYPOGRAPHIC_UNITS)."""
    __slots__ = ('unit', 'points', 'set_width')

    def __init__(self, input_value, unit='pt', set_width=12.0):
        if not input_value:
            raise ValueError('Cannot parse measure: {}'.format(input_value))
        raw = str(input_value).strip()
        # Sanitize the input value; add relative Monotype units
        string = ''.join(x for x in raw if x.isalnum() or x in ',.')
        units = d.TYPOGRAPHIC_UNITS.copy()
        units.update(em=round(set_width, 2), en=round(set_width / 2, 2),
                     u=round(set_width / 18, 2))
        # Get the unit suffix (end on first match), otherwise keep default
        self.unit = unit
        for symbol in sorted(units, reverse=True):
            if string.endswith(symbol):
                string = string.replace(symbol, '')
                self.unit = symbol
                break
        # Filter the string to remove all letters, round the value to 2
        num_string = ''.join(x for x in string if x in '.,0123456789')
        value = round(float(num_string.replace(',', '.')), 2)
        self.set_width = set_width
        self.points = value * units.get(self.unit)

    def __str__(self):
        return '{}{}'.format(self.value, self.unit)

    @property
    def value(self):
        """Get value in units defined on init"""
        return self.get_value()

    def get_value(self, unit=None):
        """Get a value expressed in specified or default units"""
        # Get the coefficient for calculation
        factor = 1 / d.TYPOGRAPHIC_UNITS.get(unit or self.unit, 1)
        return round(self.points * factor, 2)

    @property
    def ems(self):
        """Gets the number of ems of specified set width"""
        return round(self.points / self.set_width, 2)

    @property
    def units(self):
        """Calculates the line length in wedge's units"""
        return round(self.ems / 18, 2)


class Wedge:
    """Default S5-12E wedge, unless otherwise specified"""
    __slots__ = ('series', 'set_width', 'is_brit_pica', '_units')

    def __init__(self, wedge_name=''):
        self.series, self.set_width, self.is_brit_pica = '5', 12.0, False
        self._units = d.S5
        self.name = wedge_name

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
                                if x.isnumeric() or x is '.')
            set_width = float(set_w_str) // 0.25 * 0.25
            # try to get the unit values, otherwise S5
            units = WEDGE_DEFINITIONS.get(series, d.S5)
            # update the attributes
            self.series, self.set_width = series, set_width
            self.is_brit_pica, self.units = is_brit_pica, units
        except (TypeError, AttributeError, ValueError):
            # In case parsing goes wrong
            raise ValueError('Cannot parse wedge name {}'.format(wedge_name))

    @property
    def parameters(self):
        """Gets a list of parameters"""
        parameters = OrderedDict()
        parameters['Wedge designation'] = self.name
        parameters['Pica value'] = '{:.4f}'.format(self.pica)
        parameters['Units per row'] = ' '.join(str(x) for x in self.units if x)
        return parameters

    @property
    def units(self):
        """Gets the unit values for the wedge's rows"""
        units = self._units or d.S5
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
        return round(units * self.set_width * self.pica / 216, 2)

    def ems_to_inches(self, ems=1):
        """Get inch width of an em, i.e. 18 units"""
        return round(ems * self.units_to_inches(18), 2)

    def units_to_units(self, units=1, set_width=None, other_wedge=None):
        """Calculate other wedge's set units to own set units"""
        if other_wedge == self or set_width == self.set_width:
            return units
        elif set_width:
            return round(units * self.set_width / set_width, 2)
        elif other_wedge:
            return round(units * self.set_width / other_wedge.set_width, 2)

    @property
    def adjustment_limits(self):
        """Get the unit adjustment limits for this wedge.
        Without adjustment, the character has the same width as if the
        wedges were at 3/8.

        lower limit is reached at 1/1 0075 and 0005 wedge positions,
        max shrink is 3/8 - 1/1 = 2/7 => 2 * 0.0075 + 7 * 0.0005 = 0.0185"

        upper limit is reached at 15/15,
        max stretch is 15/15 - 3/8 = 12/7 => 12 * 0.0075 + 7 * 0.0005 = 0.0935"
        Calculate this to wedge set units.
        """
        set_factor = 12 / self.set_width
        shrink_units = 18 * set_factor * 0.0185 / self.pica
        stretch_units = 18 * set_factor * 0.0935 / self.pica
        return (shrink_units, stretch_units)

    def load(self, source):
        """Update parameters with a dictionary of values"""
        with suppress(AttributeError):
            self.series = source.get('series') or self.series
            self.set_width = source.get('set_width') or self.set_width
            self.is_brit_pica = source.get('is_brit_pica') or self.is_brit_pica
            self.units = source.get('units') or self.units


class CharFreqs:
    """Read and calculate char frequencies, translate that to casting order"""
    scale, case_ratio = 1.0, 1.0

    def __init__(self, lang=None):
        language = str(lang).strip()
        self.lang = language
        self.freqs = LETTER_FREQUENCIES[language.lower()]

    def __repr__(self):
        return '<CharFreqs for {}>'.format(d.LANGS[self.lang])

    def __str__(self):
        return d.LANGS.get(self.lang, '')

    def __iter__(self):
        return (char for char in sorted(self.freqs))

    def get_type_bill(self):
        """Returns an iterator object of tuples: (char, qty)
        for each character."""
        def quantity(char, upper=False):
            """Calculate character quantity based on frequency"""
            ratio = self.case_ratio if upper else 1
            normalized_qty = self.freqs.get(char, 0) / self.freqs.get('a', 1)
            return max(ceil(normalized_qty * self.scale * ratio), 10)

        # Start with lowercase
        lower_bill = ((char, quantity(char)) for char in sorted(self.freqs))
        upper_bill = ((char.upper(), quantity(char, upper=True))
                      for char in sorted(self.freqs) if char.isalpha())
        return chain(lower_bill, upper_bill)

    def set_scales(self, scale=1.0, case_ratio=1.0):
        """Set the scale factor and uppercase-to-lowercase ratio"""
        self.scale, self.case_ratio = scale, case_ratio


class MatrixNotFound(Exception):
    """Cannot find matrix in diecase layout."""


class UnitArrangementNotFound(Exception):
    """Cannot find an unit arrangement for a given style."""


class UnitValueNotFound(Exception):
    """Cannot find an unit value in an arrangement for a given character."""
