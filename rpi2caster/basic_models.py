# -*- coding: utf-8 -*-
"""Fundamental models for rpi2caster, not depending on database.
Classes-only module. All constants come from definitions."""

from collections import defaultdict, OrderedDict
from contextlib import suppress
from functools import singledispatch
from itertools import chain, product
from math import ceil
from . import data, definitions as d


class Stats:
    """Casting statistics gathering and displaying functions"""
    def __init__(self):
        self._ribbon = defaultdict(int)
        self._run, self._session = defaultdict(int), defaultdict(int)
        self._current = defaultdict(lambda: defaultdict(str))
        self._previous = defaultdict(lambda: defaultdict(str))

    def update(self, **kwargs):
        """Update parameters"""
        def session_line_skip(lines):
            """skip lines for every run in the session"""
            self._session['lines_skipped'] = lines

        def run_line_skip(lines):
            """skip lines for a single run"""
            self._run['lines_skipped'] = lines

        def add_runs(delta):
            """change a number of runs in casting session"""
            old_value = self._session['runs']
            runs = old_value + delta
            self._session['runs'] = runs
            self._session['codes'] = runs * self._ribbon['codes']
            self._session['chars'] = runs * self._ribbon['chars']
            self._session['lines'] = runs * self._ribbon['lines']

        def end_run(success):
            """Updates the info about the runs"""
            if success:
                # update the counters
                self._session['runs_done'] += 1
                self._session['current_run'] += 1
            else:
                # reset last run stats - don't update the counters
                self._session['failed_runs'] += 1
                for par in ('current_line', 'current_code', 'current_char'):
                    self._session[par] -= self._run[par]

        parameters = dict(ribbon=self.update_session_stats,
                          queue=self.update_run_stats,
                          record=self.update_record_stats,
                          session_line_skip=session_line_skip,
                          run_line_skip=run_line_skip,
                          runs=add_runs,
                          casting_success=end_run)
        for argument, value in kwargs.items():
            routine = parameters.get(argument)
            if not routine:
                continue
            return routine(value)

    @property
    def runs(self):
        """Gets the runs (repetitions) number"""
        return self._session['runs']

    def get_ribbon_lines(self):
        """Gets number of lines per ribbon"""
        return self._ribbon['lines']

    def get_run_lines_skipped(self):
        """Get a number of lines to skip - decide whether to use
        the run or ribbon skipped lines"""
        return self._run['lines_skipped'] or self._session['lines_skipped']

    @property
    def ribbon_parameters(self):
        """Gets ribbon parameters"""
        parameters = OrderedDict({'': 'Ribbon parameters'})
        parameters['Combinations in ribbon'] = self._ribbon['codes']
        parameters['Characters incl. spaces'] = self._ribbon['chars']
        parameters['Lines to cast'] = self._ribbon['lines']
        return parameters

    @property
    def session_parameters(self):
        """Displays the ribbon data"""
        # display this only for multi-run sessions
        if self._session['runs'] < 2:
            return {}
        parameters = OrderedDict({'': 'Casting session parameters'})
        parameters['Casting runs'] = self._session['runs']
        parameters['All codes'] = self._session['codes']
        parameters['All chars'] = self._session['chars']
        parameters['All lines'] = self._session['lines']
        return parameters

    @property
    def code_parameters(self):
        """Displays info about the current combination"""
        def build_info(source, name):
            """Builds data to display based on the given parameter"""
            current_name = 'current_{}'.format(name)
            current_value = source[current_name]
            total_name = '{}s'.format(name)
            total_value = source[total_name]
            if not total_value:
                return '{current}'.format(current=current_value)
            done = max(0, current_value - 1)
            remaining = total_value - current_value
            percent = done / total_value * 100
            desc = ('{current} of {total} [{percent:.2f}%], '
                    '{done} done, {left} left')
            return desc.format(current=current_value, total=total_value,
                               percent=percent, done=done, left=remaining)

        record = self._current['record']
        runs_number = self._session['runs']
        # display comment as a header
        info = OrderedDict({'': record.comment})
        # display codes
        info['Raw signals from ribbon'] = record.signals
        if record.is_newline:
            info['Starting a new line'] = self._run['current_line']
        if runs_number > 1:
            info['Code / run'] = build_info(self._run, 'code')
            info['Char / run'] = build_info(self._run, 'char')
            info['Line / run'] = build_info(self._run, 'line')
            info['Run / job'] = build_info(self._session, 'run')
            info['Failed runs'] = self._session['failed_runs']
        info['Code / job'] = build_info(self._session, 'code')
        info['Char / job'] = build_info(self._session, 'char')
        info['Line / job'] = build_info(self._session, 'line')
        return info

    def update_session_stats(self, ribbon):
        """Parses the ribbon, counts combinations, lines and characters"""
        # first, reset counters
        self._session, self._ribbon = defaultdict(int), defaultdict(int)
        self._current = defaultdict(lambda: defaultdict(str))
        self._previous = defaultdict(lambda: defaultdict(str))
        # parse the ribbon to read its stats
        records = [record for record in ribbon if record.has_signals]
        # number of codes is just a number of valid combinations
        num_codes = len(records)
        # ribbon starts and ends with newline, so lines = newline codes - 1
        num_lines = sum(1 for record in records if record.is_newline) - 1
        # characters: if combination has no justification codes
        num_chars = sum(1 for record in records if record.is_char)
        # Set ribbon and session counters
        self._ribbon.update(codes=num_codes, chars=num_chars,
                            lines=max(0, num_lines))
        self._session.update(lines_skipped=0, current_run=1,
                             current_line=0, current_code=0, current_char=0)

    def update_run_stats(self, queue):
        """Parses the ribbon, counts combinations, lines and characters"""
        records = [record for record in queue if record.has_signals]
        # all codes is a number of valid signals
        num_codes = len(records)
        # clear and start with -1 line for the initial galley trip
        n_lines = sum(1 for record in records if record.is_newline) - 1
        num_lines = max(n_lines, 0)
        # determine number of characters
        num_chars = sum(1 for record in records if record.is_char)
        # update run statistics
        self._run.update(lines_skipped=0,
                         current_line=0, current_code=0, current_char=0,
                         lines=num_lines, codes=num_codes, chars=num_chars)

    def update_record_stats(self, record):
        """Updates the stats based on parsed signals."""
        # Update previous stats and current record
        self._previous, self._current['record'] = self._current.copy(), record
        # advance or set the run and session code counters
        self._run['current_code'] += 1
        self._session['current_code'] += 1
        # detect 0075+0005(+pos_0005)->0075(+pos_0075) = double justification
        # this means starting new line
        with suppress(AttributeError):
            was_newline = self._previous['record'].is_newline
            if was_newline and record.is_pump_start:
                self._run['current_line'] += 1
                self._session['current_line'] += 1
        # advance or set the character counters
        self._run['current_char'] += 1 * record.is_char
        self._session['current_char'] += 1 * record.is_char

    def get_runs_left(self):
        """Gets the runs left number"""
        diff = self._session['runs'] - self._session['runs_done']
        return max(0, diff)

    def get_lines_done(self):
        """Gets the current run line number"""
        return max(0, self._run['current_line'] - 1)


class Matrix:
    """A class for single matrices - all matrix data"""
    __slots__ = ('char', '_units', 'row', 'column', '_styles', 'diecase',
                 'position', 'size')

    def __init__(self, char='', styles='*', code='', units=0, diecase=None):
        self.diecase = diecase
        self.char = char
        self.size = d.MatrixSize(horizontal=1, vertical=1)
        self.position, self.code = d.Coordinates(None, None), code
        self._units = units
        self._styles = Styles(styles).string

    def __len__(self):
        return 0 if self.isspace() else len(self.char)

    def __bool__(self):
        return True

    def __repr__(self):
        return ('<Matrix: {m.position.column}{m.position.row} '
                '({m.char} {styles}, {m.units} units wide)>'
                .format(m=self, styles=self.styles.names))

    def __str__(self):
        if self.ishighspace():
            tmpl = 'high space at {pos.column}{pos.row}'
        elif self.islowspace():
            tmpl = 'low space at {pos.column}{pos.row}'
        else:
            tmpl = '{m.char} ({m.styles.names}) at {pos.column}{pos.row}'
        return tmpl.format(m=self, pos=self.position)

    @property
    def comment(self):
        """Generate a comment based on matrix character and style."""
        retval = ('low space {mat.ems:.2f} ems' if self.islowspace()
                  else 'high space {mat.ems:.2f} ems' if self.ishighspace()
                  else '{mat.char} ({mat.styles.names})')
        return retval.format(mat=self)

    @property
    def units(self):
        """Gets the specific or default number of units"""
        # If units are assigned to the matrix, return the value
        # Otherwise, wedge default
        return (self._units or self.get_units_from_arrangement() or
                self.get_units_from_row())

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
    def code(self):
        """Gets the matrix code"""
        try:
            return '{pos.column}{pos.row}'.format(pos=self.position)
        except AttributeError:
            return ''

    @code.setter
    def code(self, codes):
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
            for column in ['NI', 'NL', *'ABCDEFGHIJKLMNO']:
                if column in sigs:
                    sigs = sigs.replace(column, '')
                    yield column
            yield None

        # needs to work with strings and iterables
        codes = codes or ''
        sigs = ''.join(str(l) for l in codes).upper()

        # get a first possible row (caveat: recognize double-digit numbers)
        all_rows = [x for x in row_generator()]
        rows = (x for x in reversed(all_rows))
        # get the first possible column -> NI, NL, A...O
        columns = column_generator()
        self.position = d.Coordinates(column=next(columns), row=next(rows))

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
        return self.char and self.char.isspace()

    def set_lowspace(self, value):
        """Update self.char with " " for low spaces"""
        if value:
            self.char = ' '

    def ishighspace(self):
        """Checks whether this is a high space: "_" is present"""
        # Any number of _ is present, no other characters
        return (self.char and '_' in self.char and not
                [x for x in self.char.strip() if x != '_'])

    def set_highspace(self, value):
        """Set the character to _"""
        if value:
            self.char = '_'

    def isspace(self):
        """Check if it's a low or high space"""
        return self.islowspace() or self.ishighspace()

    def get_units_from_row(self, wedge_used=None):
        """Gets a number of units for characters in the diecase row"""
        wedge = wedge_used or self.diecase.wedge
        try:
            return wedge.units[self.position.row]
        except (AttributeError, TypeError, IndexError):
            return 0

    def get_min_units(self):
        """Gets the minimum unit value for a given wedge, based on the
        matrix row and wedge unit value, for wedges at 1/1"""
        wedge = self.diecase.wedge
        limits = wedge.get_adjustment_limits(low_space=self.islowspace())
        # at least one unit
        return round(max(self.get_units_from_row() - limits.shrink, 1), 2)

    def get_max_units(self):
        """Gets the minimum unit value for a given wedge, based on the
        matrix row and wedge unit value, for wedges at 1/1"""
        wedge = self.diecase.wedge
        limits = wedge.get_adjustment_limits(low_space=self.islowspace())
        return round(self.get_units_from_row() + limits.stretch, 2)

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

    def get_layout_record(self, pos=True):
        """Returns a record suitable for JSON-dumping and storing in DB."""
        code = '{p.column}{p.row}'.format(p=self.position) if pos else ''
        return d.MatrixRecord(self.char, self.styles.string, code, self.units)

    def get_ribbon_record(self, s_needle=False, comment=True):
        """Returns a signals record for adding to ribbon.

        s_needle : whether to add "S" signal or not,
        comment : False or None for no comment,
                  True to auto-generate the comment,
                  any other value to use it as a comment
        """
        _comment = ('' if not comment
                    else self.comment if comment is True
                    else comment)
        code = ('{pos.column}{es}{pos.row}'
                .format(pos=self.position, es='S' * s_needle))
        commented = '{:<20} // {}'
        return commented.format(code, _comment) if _comment else code


class VariableSpace(Matrix):
    """Simplified matrix-like object: variable space for justifying"""
    __slots__ = ['matrix', '_units', 'position', 'diecase', 'char']

    def __init__(self, diecase, units=0, low=True):
        super().__init__(diecase=diecase, char=' ' if low else '_',
                         units=units)

    def match(self):
        """locate the best suitable space for the given number of units"""
        matrix = self.diecase.layout.get_space(units=self.units,
                                               low=self.islowspace())
        self.position = matrix.position

    @property
    def units(self):
        """get space's unit width"""
        return self._units

    @units.setter
    def units(self, units):
        """set units and find a most suitable space"""
        with suppress(TypeError):
            self._units = float(units)
            self.match()


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

    def __eq__(self, other):
        try:
            # two styles collections having common elements compare equal
            # should work with strings and Styles objects as well
            return (set(self).intersection(other) or
                    set(str(self)).intersection(str(other)))
        except (TypeError, ValueError, AttributeError):
            return False

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
        return set(self) == set(Styles.definitions)

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


class UnitArrangement:
    """Unit arrangement for a diecase.

    haracterized by UA ID and variant (regular, small caps, italic etc.)

    Has two dictionaries:
    {unit_value1: [char1, char2...]...} for getting all chars of given units,
    {char1: unit_value1, char2: unit_value2...} for char unit value lookups.
    """
    __slots__ = ('by_units', 'by_char', 'number', 'variant')

    def __init__(self, number=0, variant=None):
        # store the number (string in case int was supplied)
        self.number = str(number)
        # variant: should work with short or full definition (namedtuple)
        variant_definitions = {v.short: v for v in d.VARIANTS}
        self.variant = variant_definitions.get(variant) or variant
        # look the arrangement up
        mappings = data.UNIT_ARRANGEMENTS.get(self.number, {})
        arrangement = mappings.get(self.variant.short)
        if not arrangement:
            raise UnitArrangementNotFound
        # parse the UA
        by_char = {c: int(u) for c, u in arrangement.items() if c and u}
        by_units = defaultdict(list)
        for char, units in sorted(by_char.items()):
            by_units[units].append(char)
        # store the result
        self.by_char, self.by_units = by_char, by_units

    def __str__(self):
        template = '{ua.number} {ua.variant.name}'
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


class Typeface:
    """Typeface definition. Gets all data for the given typeface number."""
    def __init__(self, number, size):
        self.number, self.size = str(number), str(size).upper()
        raw_data = data.TYPEFACES.get(self.number)


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
                else 'extended: NI, NL' if self.columns == 17 else 'small')
        return '{}x{} - {}'.format(self.rows, self.columns, name)

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
            return ['NI', 'NL', *'ABCDEFGHIJKLMNO']
        else:
            return [*'ABCDEFGHIJKLMNO']

    @column_numbers.setter
    def column_numbers(self, column_numbers):
        """Column numbers setter."""
        with suppress(TypeError):
            self.columns = 17 if len(column_numbers) > 15 else 15

    @property
    def positions(self):
        """Gets all matrix positions for this layout"""
        by_row = product(self.row_numbers, self.column_numbers)
        return [d.Coordinates(column=col, row=row) for (row, col) in by_row]

    def clean_layout(self, diecase=None):
        """Generate an empty layout of a given size."""
        # get coordinates to iterate over and build dict keys
        new_layout = OrderedDict().fromkeys(self.positions)
        # fill it with new empty matrices and define low/high spaces
        for position in new_layout:
            mat = Matrix(char='', styles='*', diecase=diecase)
            mat.position = position
            # preset spaces
            mat.set_lowspace(position in d.DEFAULT_LOW_SPACE_POSITIONS)
            mat.set_highspace(position in d.DEFAULT_HIGH_SPACE_POSITIONS)
            new_layout[position] = mat
        return new_layout


class Measure:
    """Chooses and represents a line length, space width etc. measures
    which can be expressed in various typographic units (for definition,
    see TYPOGRAPHIC_UNITS)."""
    __slots__ = ('unit', 'points', 'set_width')

    def __init__(self, input_value, unit='pt', set_width=12.0):
        if not input_value:
            raise ValueError('Cannot parse measure: {}'.format(input_value))
        # Support parsing of the relative Monotype units, based on set width
        # We know the set width now, and need to update the unit definitions
        units = d.TYPOGRAPHIC_UNITS.copy()
        units.update(em=round(set_width, 2), en=round(set_width / 2, 2),
                     u=round(set_width / 18, 2))
        # Parse the value
        raw = str(input_value).strip()
        string = ''.join(x for x in raw if x.isalnum() or x in ',.')
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
        return round(self.ems * 18, 2)

    @property
    def inches(self):
        """An absolute width of this measure in inches"""
        return self.points / 72.0


class Wedge:
    """Default S5-12E wedge, unless otherwise specified"""
    __slots__ = ('series', 'set_width', 'is_brit_pica', '_units')

    def __init__(self, wedge_name='', wedge_data=None):
        w_data = wedge_data or {}
        if wedge_name:
            self.name = wedge_name
        else:
            self.series = w_data.get('series', '5')
            self.set_width = w_data.get('set_width', 12.0)
            self.is_brit_pica = w_data.get('is_brit_pica', True)
            self._units = w_data.get('units', d.S5)

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
            units = data.WEDGE_DEFINITIONS.get(series, d.S5)
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

    def get_adjustment_limits(self, low_space=False, cell_width=1):
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
        cap = 0.18 + (cell_width - 1) * 0.2
        maximum = stretch_inches if low_space else min(stretch_inches, cap)
        # calculate adjustment range in units
        shrink = int(18 * 12 * 0.0185 / self.pica / self.set_width)
        stretch = int(18 * 12 * maximum / self.pica / self.set_width)
        return d.WedgeLimits(shrink, stretch)


class CharFreqs:
    """Read and calculate char frequencies, translate that to casting order"""
    scale, case_ratio = 1.0, 1.0

    def __init__(self, lang=None):
        language = str(lang).strip()
        self.lang = language
        self.freqs = data.LETTER_FREQUENCIES[language.lower()]

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


class TypesettingError(Exception):
    """Various exceptions raised when typesetting"""
