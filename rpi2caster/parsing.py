# -*- coding: utf-8 -*-
"""Functions and classes for parsing strings/iterables for usable data."""
from . import definitions as d


class ParsedRecord:
    """Parsed record data structure stores row numbers, column numbers,
    justification signals and S-needle signal.
    Properties:
        signals - returns signals list
        signals_string - returns ' '.join(signals),
        adjusted_signals - returns signals adjusted to row_16_mode,
        adjusted_signals_string - returns ' '.join(adjusted_signals),
        code - perform additional checks on signals and return a namedtuple,
        comment - comment found in code,
        row_pin - a row pin the caster jaws will stop on (1...15),
        column_pin - a column pin the caster jaws will stop on (NI, NL, A...O)
    Methods:
        _parse_record(code) - sets the comment, columns, rows, justification,
                              use_s_needle instance attributes
    """
    __slots__ = ('content', 'settings', '_report')

    def __init__(self, signals_iterable,
                 signal_o15=False, default_o15=False, row_16_mode=0):
        # get the content and settings
        self.settings = d.Settings(row_16_mode=row_16_mode,
                                   explicit_o15=signal_o15,
                                   add_missing_o15=default_o15)
        self.content = parse_record(signals_iterable)
        # generate when needed
        self._report = None

    @property
    def signals(self):
        """Return a list of all signals"""
        # Add O15 if it was desired (explicit O or 15, lack of rows/columns)
        # only if signal_o15 flag was enabled.
        use_o15 = ('O' in self.content.columns, 15 in self.content.rows,
                   not self.content.columns and self.settings.add_missing_o15,
                   not self.content.rows and self.settings.add_missing_o15)
        column_set = set(self.content.columns)
        column_set.discard('O')

        # build the output list
        justification = [x for x in self.content.justification]
        columns = [x for x in d.COLUMNS_15 if x in column_set]
        es_needle = ['S'] * self.content.use_s_needle
        rows = [str(x) for x in self.content.rows if x < 15]
        o15 = ['O15'] * (self.settings.explicit_o15 and any(use_o15))

        return justification + columns + es_needle + rows + o15

    @property
    def comment(self):
        """Getter for a comment string."""
        return self.content.comment

    @property
    def raw_signals(self):
        """Getter for raw (unparsed) signals string."""
        return self.content.raw_signals

    @property
    def original_entry(self):
        """Getter for unparsed ribbon entry."""
        return self.content.original_entry

    @property
    def adjusted_signals(self):
        """Return a list of signals adjusted to HMN/KMN/unit-shift addressing
        modes."""
        def do_not_convert():
            """No mode conversion needed"""

        def hmn():
            """HMN addressing mode - developed by Monotype, based on KMN.
            Uncommon."""
            # NI, NL, M -> add H -> HNI, HNL, HM
            # H -> add N -> HN
            # N -> add M -> MN
            # O -> add HMN
            # {ABCDEFGIJKL} -> add HM -> HM{ABCDEFGIJKL}
            additional = {'NI': 'H', 'NL': 'H',
                          'H': 'N', 'M': 'H', 'N': 'M', 'O': 'HMN'}
            if is_row_16:
                extra_signals = additional.get(self.column_pin, 'HM')
                column_set.update(extra_signals)

        def kmn():
            """KMN addressing mode - invented by a British printshop.
            Very uncommon."""
            # NI, NL, M -> add K -> KNI, KNL, KM
            # K -> add N -> KN
            # N -> add M -> MN
            # O -> add KMN
            # {ABCDEFGHIJL} -> add KM -> KM{ABCDEFGHIJL}
            additional = {'NI': 'K', 'NL': 'K',
                          'K': 'N', 'M': 'K', 'N': 'M', 'O': 'KMN'}
            if is_row_16:
                extra_signals = additional.get(self.column_pin, 'KM')
                column_set.update(extra_signals)

        def unit_shift():
            """Unit-shift addressing mode - rather common,
            designed by Monotype and introduced in 1963"""
            if 'D' in column_set:
                # when the attachment is on, the D signal is routed
                # to unit-shift activation piston instead of column D air pin
                # this pin is activated by EF combination instead
                column_set.discard('D')
                column_set.update('EF')
            if is_row_16:
                # use unit shift if, and only if, the only row signal is 16
                column_set.update('D')

        functions = {d.OFF: do_not_convert, d.UNIT_SHIFT: unit_shift,
                     d.HMN: hmn, d.KMN: kmn}

        # determine which conversion routine to use based on addressing mode
        conversion = functions.get(self.settings.row_16_mode, do_not_convert)
        column_set = set(self.content.columns)
        column_set.discard('O')

        # determine if explicit O15 would be used
        use_o15 = ('O' in self.content.columns, 15 in self.content.rows,
                   not self.content.columns and self.settings.add_missing_o15,
                   not self.content.rows and self.settings.add_missing_o15)

        # check if this combination is row 16 and not earlier
        is_row_16 = set(self.content.rows) == {16}
        # apply signals conversion
        conversion()

        # compose the output signal list
        justification = [x for x in self.content.justification]
        columns = [x for x in d.COLUMNS_15 if x in column_set]
        es_needle = ['S'] * self.content.use_s_needle
        rows = [str(x) for x in self.content.rows if x < 15]
        o15 = ['O15'] * (self.settings.explicit_o15 and any(use_o15))

        # got result
        return justification + columns + es_needle + rows + o15

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
        if self._report:
            return self._report
        else:
            # report was not cached, so generate it
            # get the attributes
            columns, rows = self.content.columns, self.content.rows
            justification = self.content.justification

            # basic signals checks
            has_signals = any((*rows, *columns, *justification))
            uses_row_16 = True if set(rows) == {16} else False

            # detect the justification signals (also for unit-adding mode)
            has_0005 = '0005' in justification or {'N', 'J'}.issubset(columns)
            has_0075 = '0075' in justification or {'N', 'K'}.issubset(columns)

            # what do these signals mean?
            is_pump_start = has_0075
            is_pump_stop = has_0005 and not has_0075
            is_pump_hold = has_0005 or has_0075
            is_newline = has_0005 and has_0075
            is_char = has_signals and not any(justification)

            # time to put it all together
            report = d.Report(has_signals, uses_row_16, has_0005, has_0075,
                              is_pump_start, is_pump_stop, is_pump_hold,
                              is_newline, is_char)

            # cache the calculated report so it doesn't have to be generated
            self._report = report
            return report

    @property
    def row_pin(self):
        """Get the earliest row pin from the signals. This row will normally
        be cast on a Monotype composition caster."""
        # row 16 will not be cast
        return str(min([*self.content.rows, 15]))

    @property
    def column_pin(self):
        """Get the earliest column from the signals. This column will normally
        be cast on a Monotype composition caster."""
        try:
            first_signal = self.content.columns[0]
        except IndexError:
            # this happens if not self.columns
            first_signal = 'O'
        # NI, NL, A...O (no column means O)
        column_set = set(self.content.columns)
        return ('NI' if column_set.issuperset('NI')
                else 'NL' if column_set.issuperset('NL') else first_signal)


def parse_record(input_data):
    """Parses the record and gets its row, column and justification codes.
    First split the input data into two parts:
    -the Monotype signals (unprocessed),
    -any comments delimited by symbols from COMMENT_SYMBOLS list.

    Looks for any comment symbols defined here - **, *, ##, #, // etc.
    splits the line at it and saves the comment to return it later on.
    If it's an inline comment (placed after Monotype code combination),
    this combination will be returned for casting."""
    def split_on_delimiter(sequence):
        """Iterate over known comment delimiter symbols to find
        whether a record has a comment; split on that delimiter
        and normalize the signals"""
        source = ''.join(str(x) for x in sequence)
        for symbol in d.COMMENT_SYMBOLS:
            if symbol in source:
                # Split on the first encountered symbol
                raw_signals, comment = source.split(symbol, 1)
                break
        else:
            # no comment symbol encountered, so we only have signals
            raw_signals, comment = source, ''

        return raw_signals.upper().strip(), comment.strip()

    def find_and_delete(value):
        """Detect and dispatch known signals in source string"""
        nonlocal signals
        string = str(value)
        if string in signals:
            signals = signals.replace(string, '')
            return True
        else:
            return False

    # we know signals and comment right away
    raw_signals, comment = split_on_delimiter(input_data)
    signals = raw_signals

    # read the signals to know what's inside
    justification = tuple(x for x in ('0075', '0005') if find_and_delete(x))
    parsed_rows = [x for x in range(16, 0, -1) if find_and_delete(x)]
    rows = tuple(x for x in reversed(parsed_rows))
    columns = tuple(x for x in d.COLUMNS_15 if find_and_delete(x))

    # return the data
    return d.Content(original_entry=input_data,
                     raw_signals=raw_signals, comment=comment,
                     use_s_needle='S' in signals,
                     columns=columns, rows=rows, justification=justification)


def parse_ribbon(ribbon):
    """Get the metadata and contents out of a sequence of lines"""
    def get_value(line, symbol):
        """Helper function - strips whitespace and symbols"""
        # Split the line on an assignment symbol, get the second part,
        # strip any whitespace or multipled symbols
        return line.split(symbol, 1)[-1].strip(symbol).strip()

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
                for sym in d.ASSIGNMENT_SYMBOLS:
                    if sym in line:
                        # Data found
                        metadata[target] = get_value(line, sym)
                        break
                break
        else:
            contents.append(line)
    # We need to add contents too
    metadata['contents'] = contents
    return metadata


def stop_comes_first(contents):
    """Detects ribbon direction so that we can use the ribbons generated
    with different software and still cast them in correct order.
    This function loops over the ribbon to test if the stop sequence
    (NJ or 0005) comes before the newline sequence (NKJ or 0075+0005).
    If so, returns True (the ribbon needs to be rewound for casting).
    Otherwise, False."""
    for line in contents:
        # code parameters checker
        parsed_record = ParsedRecord(line)
        code = parsed_record.code
        if code.is_pump_stop:
            return True
        elif code.is_pump_start:
            return False
        else:
            continue


def get_coordinates(signals):
    """Get the column and row from record"""
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
        sigs = ''.join(signals).upper()
    except TypeError:
        # in case not every iterable element is a string => convert
        sigs = ''.join(str(l) for l in signals).upper()

    # get a first possible row (caveat: recognize double-digit numbers)
    all_rows = [x for x in row_generator()]
    rows = (x for x in reversed(all_rows))

    # get the first possible column -> NI, NL, A...O
    columns = column_generator()
    column, row = next(columns), next(rows)

    return d.Coordinates(column, row)


def get_key(source):
    """Get the Key namedtuple of a key. First look it up in special keys."""
    # normalize to lowercase and strip all whitespace ('Esc' -> 'esc')
    # replace spaces and dashes to underscores ('ctrl-C -> ctrl_c)
    if source is None:
        # can be used to generate numbers on the fly
        return d.Key(getchar=None, name=None)
    else:
        key = str(source)
        normalized_key = key.lower().strip()
        normalized_key.replace('-', '_')
        normalized_key.replace(' ', '_')
        return d.KEYS.get(normalized_key) or d.Key(getchar=key, name=key)
