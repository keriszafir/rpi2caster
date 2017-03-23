# -*- coding: utf-8 -*-
"""Functions for parsing layouts and ribbons"""
import json
from collections import namedtuple
from . import constants as c


class ParsedRecord:
    """Parsed record data structure stores row numbers, column numbers,
    justification signals and S-needle signal.
    Properties:
        signals - returns signals list
        signals_string - returns ' '.join(signals),
        adjusted_signals - returns signals adjusted to row_16_addressing,
        adjusted_signals_string - returns ' '.join(adjusted_signals),
        code - perform additional checks on signals and return a namedtuple,
        comment - comment found in code,
        row_pin - a row pin the caster jaws will stop on (1...15),
        column_pin - a column pin the caster jaws will stop on (NI, NL, A...O).
    Methods:
        _parse_record(code) - sets the comment, columns, rows, justification,
                              use_s_needle instance attributes
    """
    comment, rows, columns, justification, use_s_needle = '', [], [], [], False

    def __init__(self, signals_iterable, signal_o15=False, default_o15=False,
                 row_16_addressing=None):
        self._parse_record(signals_iterable)
        self.row_16_addressing = row_16_addressing or None
        self.signal_o15, self.default_o15 = signal_o15, default_o15

    @property
    def signals(self):
        """Return a list of all signals"""
        # Add O15 if it was desired (explicit O or 15, lack of rows/columns)
        # only if signal_o15 flag was enabled.
        use_o15 = any(('O' in self.columns, 15 in self.rows,
                       self.default_o15 and not self.columns,
                       self.default_o15 and not self.rows))
        es_needle = ['S'] * self.use_s_needle
        o15 = ['O15'] * self.signal_o15 and use_o15
        rows = [str(x) for x in self.rows]
        return self.justification + self.columns + es_needle + rows + o15

    @property
    def adjusted_signals(self):
        """Return a list of signals adjusted to HMN/KMN/unit-shift addressing
        modes."""
        def do_not_convert(column_set):
            """No mode conversion needed"""
            return column_set

        def hmn(column_set):
            """HMN addressing mode - developed by Monotype, based on KMN.
            Uncommon."""
            # detect the signals as they appear in the pin block
            if 16 in self.rows:
                if column_set.issuperset('NI') or column_set.issuperset('NL'):
                    # NI, NL -> add H -> HNI, HNL
                    column_set.update('H')
                elif column_set.intersection('ABCDEFG'):
                    # {ABCDEFG} -> add HM -> HM{ABCDEFG}
                    column_set.update('HM')
                elif 'H' in column_set:
                    # H -> add N -> HN
                    column_set.update('N')
                elif column_set.intersection('IJKLM'):
                    # {IJKL} -> add HM -> HM{IJKL}
                    # M -> add H -> HM
                    column_set.update('HM')
                elif 'N' in column_set:
                    # N -> add M -> MN
                    column_set.update('M')
                elif not column_set or 'O' in column_set:
                    # O -> HMN
                    column_set.update('HMN')
            return column_set

        def kmn(column_set):
            """KMN addressing mode - invented by a British printshop.
            Very uncommon."""
            if 16 in self.rows:
                if column_set.issuperset('NI') or column_set.issuperset('NL'):
                    # NI, NL -> add K -> KNI, KNL
                    column_set.update('K')
                elif column_set.intersection('ABCDEFGHIJ'):
                    # {ABCDEFGHIJ} -> add KM -> KM{ABCDEFGHIJ}
                    column_set.update('HM')
                elif 'K' in column_set:
                    # K -> add N -> KN
                    column_set.update('N')
                elif 'L' in column_set:
                    # L -> add KM -> KML
                    column_set.update('KM')
                elif 'N' in column_set:
                    # N -> add M -> MN
                    column_set.update('M')
                elif not column_set or 'O' in column_set:
                    # O -> KMN
                    column_set.update('KMN')
            return column_set

        def unit_shift(column_set):
            """Unit-shift addressing mode - rather common,
            designed by Monotype and introduced in 1963"""
            if 'D' in column_set:
                # when the attachment is on, the D signal is routed
                # to unit-shift activation piston instead of column D air pin
                # this pin is activated by EF combination instead
                column_set.discard('D')
                column_set.update('EF')
            if set(self.rows) == {16}:
                # use unit shift if, and only if, the only row signal is 16
                column_set.update('D')
            return column_set

        routine = {None: do_not_convert, c.UNIT_SHIFT: unit_shift, c.HMN: hmn,
                   c.KMN: kmn}.get(self.row_16_addressing, do_not_convert)
        # determine if explicit O15 would be used
        use_o15 = any(('O' in self.columns, 15 in self.rows,
                       self.default_o15 and not self.columns,
                       self.default_o15 and not self.rows))
        converted_columns = routine(set(self.columns))
        columns = [x for x in c.COLUMNS_15 if x in converted_columns]
        rows = [str(x) for x in self.rows if x < 15]
        es_needle = ['S'] * self.use_s_needle
        o15 = ['O15'] * self.signal_o15 and use_o15
        return self.justification + columns + es_needle + rows + o15

    @property
    def signals_string(self):
        """Return signals as string."""
        return ' '.join(self.signals) or 'no signals'

    @property
    def adjusted_signals_string(self):
        """Return adjusted signals as string"""
        return ' '.join(self.adjusted_signals) or 'no signals'

    @property
    def code(self):
        """Check signals for control codes"""
        j_codes = self.justification
        is_row_16 = 16 in self.rows
        has_0005 = '0005' in j_codes or {'N', 'J'}.issubset(self.columns)
        has_0075 = '0075' in j_codes or {'N', 'K'}.issubset(self.columns)
        is_pump_start = has_0075
        is_pump_stop = has_0005 and not has_0075
        is_pump_hold = has_0005 or has_0075
        is_newline = has_0005 and has_0075
        is_char = any(self.signals) and not is_pump_hold
        fields = ('has_0005', 'has_0075', 'is_pump_start', 'is_pump_stop',
                  'is_pump_hold', 'is_newline', 'is_char', 'is_row_16')
        result = namedtuple('check_results', fields)
        return result(has_0005, has_0075, is_pump_start, is_pump_stop,
                      is_pump_hold, is_newline, is_char, is_row_16)

    @property
    def row_pin(self):
        """Get the earliest row pin from the signals. This row will normally
        be cast on a Monotype composition caster."""
        # row 16 will not be cast
        return str(min([*self.rows, 15]))

    @property
    def column_pin(self):
        """Get the earliest column from the signals. This column will normally
        be cast on a Monotype composition caster."""
        try:
            first_signal = self.columns[0]
        except IndexError:
            # this happens if not self.columns
            first_signal = 'O'
        # NI, NL, A...O (no column means O)
        column_set = set(self.columns)
        return ('NI' if column_set.issuperset('NI')
                else 'NL' if column_set.issuperset('NL') else first_signal)

    def _parse_record(self, input_data):
        """Parses the record and gets its row, column and justification codes.
        First split the input data into two parts:
        -the Monotype signals (unprocessed),
        -any comments delimited by symbols from COMMENT_SYMBOLS list.

        Looks for any comment symbols defined here - **, *, ##, #, // etc.
        splits the line at it and saves the comment to return it later on.
        If it's an inline comment (placed after Monotype code combination),
        this combination will be returned for casting.

        signal_o15  - include additional "O15" signal if O or 15 is desired
        default_o15 - lack of row or column means O15, e.g. in ribbon punching
                      (explicit_o15 decides whether it's visible in output)"""
        def split_on_delimiter(sequence):
            """Iterate over known comment delimiter symbols to find
            whether a record has a comment; split on that delimiter
            and normalize the signals"""
            source = ''.join(str(x) for x in sequence)
            for symbol in c.COMMENT_SYMBOLS:
                if symbol in input_data:
                    # Split on the first encountered symbol
                    raw_signals, comment = source.split(symbol, 1)
                    break
            else:
                # no comment symbol encountered, so we only have signals
                raw_signals, comment = source, ''

            return raw_signals.upper().strip(), comment.strip()

        def find_and_delete(value):
            """Detect and dispatch known signals in source string"""
            nonlocal sigs
            string = str(value)
            if string in sigs:
                sigs = sigs.replace(string, '')
                return True
            else:
                return False

        # we know comment right away
        sigs, self.comment = split_on_delimiter(input_data)
        self.use_s_needle = 'S' in sigs
        self.columns = [x for x in c.COLUMNS_15 if find_and_delete(x)]
        self.justification = [x for x in ('0075', '0005')
                              if find_and_delete(x)]
        rows = [x for x in range(16, 0, -1) if find_and_delete(x)]
        self.rows = [x for x in reversed(rows)]


def parse_layout_size(canonical_layout):
    """Get a size of a layout JSON-encoded or not"""
    # The smallest layout is 15x15, later on it was extended to 15x17
    # (+2 columns: NI, NL), ultimately to 16x17 (+1 row).
    # Monophoto and Monomatic layouts could be even bigger, but these machines
    # were not common and won't be supported in our software.
    size = namedtuple('Size', ('rows', 'columns'))
    rows, columns = 15, 15
    try:
        layout = json.loads(canonical_layout)
    except (TypeError, json.JSONDecodeError):
        layout = canonical_layout
    # Layout stores records for each matrix: [(char, styles, pos, units)...]
    # Iterate in reverse order, because for 16-row diecases it's quicker
    # to determine the size.
    for record in reversed(layout):
        (_, _, position_string, _) = record
        # low-level parse the position string to determine the highest row/col
        position = get_coordinates(position_string)
        assert '%s%s' % (position.column, position.row) == position_string
        if position.row == 16:
            # finish here as the only 16-row diecases were 16x17
            # no need to iterate further
            return size(16, 17)
        if position.column in ('NI', 'NL'):
            # update the columns number (iterate further because
            # we still can find 16th row)
            columns = 17
    return size(rows, columns)


def stop_comes_first(contents):
    """Detects ribbon direction so that we can use the ribbons generated
    with different software and still cast them in correct order.
    This function loops over the ribbon to test if the stop sequence
    (NJ or 0005) comes before the newline sequence (NKJ or 0075+0005).
    If so, returns True (the ribbon needs to be rewound for casting).
    Otherwise, False."""
    for line in contents:
        # code parameters checker
        code = ParsedRecord(line).code
        if code.is_pump_stop:
            return True
        elif code.is_pump_start:
            return False
        else:
            continue


def get_column(signals, default='O'):
    """Gets the lowest column number from the signals list."""
    signals_string = ''.join(str(l).upper() for l in signals)
    for column in c.COLUMNS_17:
        # iterate from left (NI, NL) to right (O)
        if set(column).issubset(signals_string):
            return column
    return default


def get_row(source, default=15):
    """Gets the lowest row number from the signal list. Returns int."""
    sigs = ''.join(str(x) for x in source)
    rows = []
    for number in range(16, 0, -1):
        str_number = str(number)
        if str_number in sigs:
            # remove the number from signals to prevent adding its digits
            sigs = sigs.replace(str_number, '')
            rows.append(number)
    # try to get the earliest row if rows are not empty; otherwise - default
    try:
        return min(rows)
    except ValueError:
        return default


def get_coordinates(signals):
    """Get the column and row from signals"""
    coordinates = namedtuple('position', ('column', 'row'))
    column = get_column(signals, default=None)
    row = get_row(signals, default=None)
    return coordinates(column, row)
