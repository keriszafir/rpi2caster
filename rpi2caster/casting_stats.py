# -*- coding: utf-8 -*-
"""Casting stats - implements stats getting and setting"""
from contextlib import suppress
from . import parsing as p


class Stats(object):
    """Casting statistics gathering and displaying functions"""
    def __init__(self, session):
        self.__dict__['_current'] = {}
        self.__dict__['_previous'] = {}
        self.__dict__['_run'] = {}
        self.__dict__['_ribbon'] = {}
        self.__dict__['_session'] = {}
        self.session = session

    def end_run(self):
        """Updates the info about the runs"""
        session = self.__dict__['_session']
        # Current run will always be runs done +1
        session['runs_done'] = session.get('current_run', 1)
        session['current_run'] += 1

    def reset_last_run_stats(self):
        """Subtracts the current run stats from all runs stats;
        this is called before repeating a failed casting run."""
        session = self.__dict__['_session']
        run = self.__dict__['_run']
        session['failed_runs'] = session.get('failed_runs', 0) + 1
        for par in ('current_line', 'current_code', 'current_char'):
            session[par] = (session.get(par, 1) - run.get(par, 0))

    def get_lines_done(self):
        """Gets the current run line number"""
        current_line = self.__dict__.get('_run', {}).get('current_line', 1)
        return max(0, current_line - 1)

    def get_ribbon_lines(self):
        """Gets number of lines per ribbon"""
        return self.__dict__.get('_ribbon', {}).get('lines', 1)

    def get_current_run(self):
        """Gets the current run number"""
        return self.__dict__.get('_session').get('current_run', 1)

    @property
    def runs(self):
        """Gets the runs (repetitions) number"""
        return self.__dict__.get('_session', {}).get('runs', 1)

    @runs.setter
    def runs(self, runs=1):
        """Sets the runs (repetitions) number"""
        session = self.__dict__['_session']
        ribbon = self.__dict__['_ribbon']
        # Update whenever we change runs number via one_more_run
        session['runs'] = runs
        session['codes'] = runs * ribbon.get('codes', 1)
        session['chars'] = runs * ribbon.get('chars', 1)
        session['lines'] = runs * ribbon.get('lines', 1)

    @property
    def runs_remaining(self):
        """Gets the runs left number"""
        session = self.__dict__['_session']
        diff = session.get('runs', 1) - session.get('runs_done', 0)
        return diff if diff > 0 else 0

    @property
    def lines_skipped(self):
        """Get a number of lines to skip - decide whether to use
        the run or ribbon skipped lines"""
        return (self.__dict__.get('_run').get('lines_skipped') or
                self.__dict__.get('_session').get('lines_skipped') or 0)

    @lines_skipped.setter
    def session_lines_skipped(self, lines):
        """Set the number of lines that will be skipped for every run
        in the casting session, unless overridden by the run lines skipped"""
        self.__dict__['_session']['lines_skipped'] = lines

    @lines_skipped.setter
    def run_lines_skipped(self, lines):
        """Set the number of lines that will be skipped for the following run
        (used mostly for continuing the interrupted casting job)"""
        self.__dict__['_run']['lines_skipped'] = lines

    @property
    def ribbon_parameters(self):
        """Gets ribbon parameters"""
        ribbon = self.__dict__.get('_ribbon', {})
        return ([] if self.session.caster.mode.diagnostics
                else [(ribbon.get('codes', 1), 'Combinations in ribbon'),
                      (ribbon.get('lines', 1), 'Lines to cast'),
                      (ribbon.get('chars', 1), 'Characters incl. spaces')])

    @property
    def session_parameters(self):
        """Displays the ribbon data"""
        session = self.__dict__.get('_session', {})
        mode = self.session.caster.mode
        # Don't display in single-run sessions or calibration mode
        return ([] if mode.diagnostics or session.get('runs', 1) < 2
                else [(session.get('runs', 1), 'Casting runs'),
                      (session.get('codes', 1), 'All codes'),
                      (session.get('chars', 1), 'All chars'),
                      (session.get('lines', 1), 'All lines')])

    @property
    def code_parameters(self):
        """Displays info about the current combination"""
        # Aliases to keep code a bit cleaner:
        current = self.__dict__.get('_current', {})
        run = self.__dict__.get('_run', {})
        session = self.__dict__.get('_session', {})
        # Some options are viable only if we have more than one repetition
        multiple_runs = session.get('runs', 1) > 1
        # Process the data to display, starting with general data
        data = []
        with suppress(AttributeError):
            data.append((current.get('record').signals_string,
                         'Signals found in ribbon'))
            data.append((current.get('record').adjusted_signals_string,
                         'Sending signals'))
        # For casting and punching:
        if not self.session.caster.mode.diagnostics:
            # Codes per run
            if multiple_runs:
                data.append(build_data(run, 'code', 'Code / run'))
            # Codes per session
            data.append(build_data(session, 'code', 'Code / job'))
            # Runs per session
            if multiple_runs:
                data.append(build_data(session, 'run', 'Run / job'))
            data.append((session.get('failed_runs', 0), 'Failed runs'))
        # Casting-only stats
        if self.session.caster.mode.casting:
            # Displayed pump status
            pump_working = current.get('pump_working', False)
            with suppress(AttributeError, KeyError):
                if current.get('record').code.is_new_line:
                    data.append((run.get('current_line', 1),
                                 'Starting a new line'))
            # Characters per run
            if multiple_runs:
                data.append(build_data(run, 'char', 'Character / run'))
            # Characters per session
            data.append(build_data(session, 'char', 'Character / job'))
            # Lines per session
            if multiple_runs:
                data.append(build_data(run, 'line', 'Line / run'))
            # Lines per run
            data.append(build_data(session, 'line', 'Line / job'))
            data.append((current.get('0075', '15'), 'Wedge 0075 now at'))
            data.append((current.get('0005', '15'), 'Wedge 0005 now at'))
            data.append(('ON' if pump_working else 'OFF', 'Pump is'))
        return data

    @session_parameters.setter
    def ribbon(self, ribbon):
        """Parses the ribbon, counts combinations, lines and characters"""
        parsed_records = (p.ParsedRecord(string) for string in ribbon)
        checks = [rec.code for rec in parsed_records if rec.signals]
        # number of codes is just a number of valid combinations
        codes = len(checks)
        # number of lines in ribbon: there's always a starting and
        # ending newline (0075+0005), so num. of lines is 1 less,
        # safeguard against negative number
        lines = max(sum(1 for code in checks if code.is_newline), 0)
        # Reset counters
        self.__dict__['_ribbon'] = {'lines': lines, 'codes': codes, 'chars': 0}
        self.__dict__['_session'] = {'lines': 0, 'codes': 0, 'chars': 0,
                                     'lines_skipped': 0, 'current_run': 1,
                                     'runs_done': 0}
        self.__dict__['_current'], self.__dict__['_previous'] = {}, {}
        # Check if row 16 addressing is needed
        needs_row_16 = any((code.is_row_16 for code in checks))
        self.session.caster.mode.needs_row_16 = needs_row_16

    @ribbon_parameters.setter
    def queue(self, queue):
        """Parses the ribbon, counts combinations, lines and characters"""
        # get all signals and filter those that are valid
        records = (p.ParsedRecord(string) for string in queue)
        # check all valid signals
        checks = [rec.code for rec in records if rec.signals]
        # all codes is a number of valid signals
        codes = len(checks)
        # clear and start with -1 line for the initial galley trip
        lines = max(sum(1 for code in checks if code.is_newline) - 1, 0)
        # determine number of characters
        chars = sum(1 for code in checks if code.is_char)
        # update run statistics
        self.__dict__['_run'] = {'lines': lines, 'codes': codes,
                                 'chars': chars, 'lines_skipped': 0}

    @code_parameters.setter
    def parsed_record(self, parsed_record):
        """Updates the stats based on parsed signals.
        parsed_record - namedtuple(signals_list, comment, signals_string)
        """
        current = self.__dict__['_current']
        run, session = self.__dict__['_run'], self.__dict__['_session']
        # Save previous state
        self.__dict__['_previous'] = {k: v for k, v in current.items()}
        previous = self.__dict__['_previous']
        # Update record info
        current['record'] = parsed_record
        # advance or set the run and session code counters
        run['current_code'] = run.get('current_code', 0) + 1
        session['current_code'] = session.get('current_code', 0) + 1
        # detect 0075+0005(+pos_0005)->0075(+pos_0075) = double justification
        # this means starting new line
        try:
            double_justification = (previous['record'].code.is_newline and
                                    current['record'].code.is_pump_start)
        except(KeyError, AttributeError):
            double_justification = False
        if parsed_record.code.is_char:
            # advance or set the character counters
            run['current_char'] = run.get('current_char', 0) + 1
            session['current_char'] = session.get('current_char', 0) + 1
        elif double_justification:
            # advance or set the line counters
            run['current_line'] = run.get('current_line', 0) + 1
            session['current_line'] = session.get('current_line', 0) + 1
        # Check the pump working/non-working status in the casting mode
        if self.session.caster.mode.casting:
            self._update_wedge_positions()
            self._check_pump()

    def _check_pump(self):
        """Checks pump based on current and previous combination"""
        previous = self.__dict__.get('_previous', {}).get('record', [])
        current = self.__dict__.get('_current', {}).get('record', [])
        was_working = self.session.caster.pump_working
        was_started, is_started, is_stopped = False, False, False
        with suppress(AttributeError):
            was_started = previous.code.is_pump_start
        with suppress(AttributeError):
            is_started = current.code.is_pump_start
            is_stopped = current.code.is_pump_stop
        # Was it running until now? Get it from the caster
        pump_on = (was_working or was_started) and not is_stopped or is_started
        self.__dict__.setdefault('_current', {})['pump_working'] = pump_on
        # Feed it back to the caster object
        self.session.caster.pump_working = pump_on

    def _update_wedge_positions(self):
        """Gets current positions of 0005 and 0075 wedges"""
        record = self.__dict__.get('_current', {}).get('record')
        if not record:
            return
        if record.code.has_0005:
            self.__dict__['_current']['0005'] = record.row_pin
        if record.code.has_0075:
            self.__dict__['_current']['0075'] = record.row_pin


def build_data(source, parameter, data_name=''):
    """Builds data to display based on the given parameter"""
    def progress_str():
        """Get the current and all values progress"""
        current = source.get('current_%s' % parameter, 1)
        try:
            total = source['%ss' % parameter]
            return '%s / %s' % (current, total)
        except KeyError:
            return '%s' % current

    def percentage_str():
        """Get a % value of things done"""
        try:
            value = ((source.get('current_%s' % parameter, 'not set') - 1) /
                     source.get('%ss' % parameter, 'not set') * 100)
            return ' [%.1f%% done]' % value
        except (TypeError, ValueError, ZeroDivisionError):
            return ''

    def remaining_str():
        """Get a value of things left"""
        try:
            value = (source.get('%ss' % parameter, 'not set') -
                     source.get('current_%s' % parameter, 'not set') + 1)
            return ', %s left' % value
        except (TypeError, ValueError):
            return ''

    return ('%s%s%s' % (progress_str(), percentage_str(), remaining_str()),
            data_name or parameter.capitalize())
