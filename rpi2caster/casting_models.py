# -*- coding: utf-8 -*-
"""Casting data models."""

from collections import defaultdict, OrderedDict
from contextlib import suppress
from functools import lru_cache
from . import definitions as d


class Record:
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
        self.content = self.parse_record(signals_iterable)
        # generate when needed
        self._report = None

    def __repr__(self):
        data = self.signals_string, self.adjusted_signals_string, self.comment
        return '<Record: {} -> {}, comment: {}>'.format(*data)

    def __str__(self):
        comment = ' [{}]'.format(self.comment) if self.comment else ''
        data = self.signals_string, self.adjusted_signals_string, comment
        return 'source signals: {}, sending: {}{}'.format(*data)

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
    def signals(self):
        """Get pure signals with no correction for row 16."""
        return self.get_signals(adjust=False)

    @property
    def adjusted_signals(self):
        """Return a list of signals adjusted to HMN/KMN/unit-shift addressing
        modes."""
        return self.get_signals(adjust=True)

    def get_signals(self, adjust=False):
        """Return a list of signals with possible correction based on
        desired row 16 addressing mode."""
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
            is_row_16 = set(self.content.rows) == {16}
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
            is_row_16 = set(self.content.rows) == {16}
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
            is_row_16 = set(self.content.rows) == {16}
            if is_row_16:
                # use unit shift if, and only if, the only row signal is 16
                column_set.update('D')

        # register these functions
        functions = {d.ROW16_ADDRESSING.off: do_not_convert,
                     d.ROW16_ADDRESSING.hmn: hmn,
                     d.ROW16_ADDRESSING.kmn: kmn,
                     d.ROW16_ADDRESSING.unitshift: unit_shift}

        # determine if explicit O15 would be used
        use_o15 = ('O' in self.content.columns, 15 in self.content.rows,
                   not self.content.columns and self.settings.add_missing_o15,
                   not self.content.rows and self.settings.add_missing_o15)
        column_set = set(self.content.columns)
        column_set.discard('O')

        if adjust:
            # choose and apply signals conversion
            modify = functions.get(self.settings.row_16_mode, do_not_convert)
            modify()

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
            uses_row_16 = set(rows) == {16}

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

    @staticmethod
    @lru_cache(maxsize=350)
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

        def find(value):
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
        justification = tuple(x for x in ('0075', '0005') if find(x))
        parsed_rows = [x for x in range(16, 0, -1) if find(x)]
        rows = tuple(x for x in reversed(parsed_rows))
        columns = tuple(x for x in d.COLUMNS_15 if find(x))

        # return the data
        return d.Content(original_entry=input_data,
                         raw_signals=raw_signals, comment=comment,
                         use_s_needle='S' in signals,
                         columns=columns, rows=rows,
                         justification=justification)


class Stats:
    """Casting statistics gathering and displaying functions"""
    def __init__(self, machine):
        self.machine = machine
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
        def build_data(source, name):
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
        data = OrderedDict({'': record.comment})
        # display codes
        data['Raw signals from ribbon'] = record.raw_signals
        data['Parsed signals'] = record.signals_string
        data['Sending signals'] = record.adjusted_signals_string
        if record.code.is_newline:
            data['Starting a new line'] = self._run['current_line']
        if runs_number > 1:
            data['Code / run'] = build_data(self._run, 'code')
            data['Char / run'] = build_data(self._run, 'char')
            data['Line / run'] = build_data(self._run, 'line')
            data['Run / job'] = build_data(self._session, 'run')
            data['Failed runs'] = self._session['failed_runs']
        data['Code / job'] = build_data(self._session, 'code')
        data['Char / job'] = build_data(self._session, 'char')
        data['Line / job'] = build_data(self._session, 'line')
        data['Wedge 0075 now at'] = self._current['0075'] or '15'
        data['Wedge 0005 now at'] = self._current['0005'] or '15'
        data['Pump is'] = 'ON' if self._current['pump_working'] else 'OFF'

        return data

    def update_session_stats(self, ribbon):
        """Parses the ribbon, counts combinations, lines and characters"""
        # first, reset counters
        self._session, self._ribbon = defaultdict(int), defaultdict(int)
        self._current = defaultdict(lambda: defaultdict(str))
        self._previous = defaultdict(lambda: defaultdict(str))
        # parse the ribbon to read its stats and determine if we need
        # to use a 16-row addressing system
        records_gen = (Record(string) for string in ribbon)
        records = [record for record in records_gen if record.code.has_signals]
        # Check if row 16 addressing is needed
        row_16_needed = any((record.code.uses_row_16 for record in records))
        self.machine.check_row_16(row_16_needed)
        # number of codes is just a number of valid combinations
        num_codes = len(records)
        # ribbon starts and ends with newline, so lines = newline codes - 1
        num_lines = sum(1 for record in records if record.code.is_newline) - 1
        # characters: if combination has no justification codes
        num_chars = sum(1 for record in records if record.code.is_char)
        # Set ribbon and session counters
        self._ribbon.update(codes=num_codes, chars=num_chars,
                            lines=max(0, num_lines))
        self._session.update(lines_skipped=0, current_run=1,
                             current_line=0, current_code=0, current_char=0)

    def update_run_stats(self, queue):
        """Parses the ribbon, counts combinations, lines and characters"""
        # get all signals and filter those that are valid
        records = (Record(string) for string in queue)
        # check all valid signals
        reports = [rec.code for rec in records if rec.code.has_signals]
        # all codes is a number of valid signals
        num_codes = len(reports)
        # clear and start with -1 line for the initial galley trip
        n_lines = sum(1 for code in reports if code.is_newline) - 1
        num_lines = max(n_lines, 0)
        # determine number of characters
        num_chars = sum(1 for code in reports if code.is_char)
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
            was_newline = self._previous['record'].code.is_newline
            if was_newline and record.code.is_pump_start:
                self._run['current_line'] += 1
                self._session['current_line'] += 1
        # advance or set the character counters
        self._run['current_char'] += 1 * record.code.is_char
        self._session['current_char'] += 1 * record.code.is_char
        self._update_wedge_positions()
        self._check_pump()

    def get_runs_left(self):
        """Gets the runs left number"""
        diff = self._session['runs'] - self._session['runs_done']
        return max(0, diff)

    def get_lines_done(self):
        """Gets the current run line number"""
        return max(0, self._run['current_line'] - 1)

    def _check_pump(self):
        """Checks pump based on current and previous combination"""
        was_working = self.machine.pump_working
        was_started, is_started, is_stopped = False, False, False
        with suppress(AttributeError):
            was_started = self._previous['record'].code.is_pump_start
        with suppress(AttributeError):
            is_started = self._current['record'].code.is_pump_start
            is_stopped = self._current['record'].code.is_pump_stop
        # Was it running until now? Get it from the caster
        is_working = (was_working or was_started) and not is_stopped
        self._current['pump_working'] = is_started or is_working

    def _update_wedge_positions(self):
        """Gets current positions of 0005 and 0075 wedges"""
        with suppress(AttributeError):
            if self._current['record'].code.has_0005:
                self._current['0005'] = self._current['record'].row_pin
            if self._current['record'].code.has_0075:
                self._current['0075'] = self._current['record'].row_pin
