# -*- coding: utf-8 -*-
"""Fundamental models for rpi2caster, not depending on database.
Classes-only module. All constants come from definitions."""

from collections import defaultdict, OrderedDict
from contextlib import suppress
from itertools import chain
from math import ceil
from . import data, definitions as d

# Style and variant definitions for lookup
STYLES = {s.short: s for s in d.STYLES}
STYLES.update({s: s for s in d.STYLES})
STYLES.update({s.name: s for s in d.STYLES})


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
            tmpl = ('{m.char} ({m.styles.names}) at {pos.column}{pos.row}, '
                    '{m.units} wide')
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
        if self.isspace() or not self.char:
            return self.get_units_from_row()
        else:
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
        sigs = ''.join(str(l) for l in codes or '').upper()

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
        try:
            wedge = wedge_used or self.diecase.wedge
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
            with suppress(ValueError, KeyError, AttributeError):
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
        mat = self.diecase.get_space(units=self.units, low=self.islowspace())
        self.position = mat.position

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
    styles: a) string, b) iterable of Style namedtuples, c) Styles object
    default: single Style namedtuple, or style short
    mask: input same as styles; this limits the choice of styles present
          to what is contained in the mask.
    """
    definitions = d.STYLES
    __slots__ = ('_styles', 'default', 'mask')

    def __init__(self, styles='*', default=None, mask=None):
        # which style is default, in case nothing is given?
        self.default = STYLES.get(default, d.STYLES.roman)
        # get a limiting mask: iterable, styles, single style
        try:
            style_mask = {STYLES.get(s) for s in mask}
            style_mask.discard(None)
        except TypeError:
            style_mask = {STYLES.get(mask)}
            style_mask.discard(None)
        self.mask = tuple(style_mask or self.definitions)

        # get styles from source and filter only the non-None ones
        try:
            source = (set(self.definitions) if styles == '*'
                      else {STYLES.get(s) for s in styles})
        except TypeError:
            source = {STYLES.get(styles)}
        # allow only non-None items, and if nothing is found, use default
        source.discard(None)
        source = source or {self.default}

        self._styles = tuple(s for s in self.definitions
                             if s in source and s in self.mask)

    def __iter__(self):
        return (x for x in self._styles)

    def __bool__(self):
        return True if self._styles else False

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
        _style = STYLES.get(what)
        return _style in self._styles

    def __eq__(self, other):
        try:
            # two styles collections having common elements compare equal
            # should work with strings and Styles objects as well
            return (set(self).intersection(other) or
                    set(str(self)).intersection(str(other)))
        except (TypeError, ValueError, AttributeError):
            return False

    def __getitem__(self, index):
        return self._styles[index]

    @property
    def string(self):
        """Return the string of all style short names"""
        return ('*' if self.use_all
                else ''.join(style.short for style in self._styles))

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
        return set(self) == set(self.mask)

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


class TypesettingError(Exception):
    """Various exceptions raised when typesetting"""
