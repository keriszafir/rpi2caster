# -*- coding: utf-8 -*-
"""Casting stats - implements stats getting and setting"""
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
        # What to do with current code: is it a char or newline?
        is_new_line = p.check_newline(current.get('signals', []))
        # Process the data to display, starting with general data
        data = [(' '.join(current.get('signals', [])), 'Signals from ribbon')]
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
        if self.session.caster.mode.casting:
            # Displayed pump status
            pump_working = current.get('pump_working', False)
            data.append((is_new_line and run.get('current_line', 1),
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
    def ribbon(self, ribbon_contents):
        """Parses the ribbon, counts combinations, lines and characters"""
        mode = self.session.caster.mode
        # Reset counters
        self.__dict__['_ribbon'] = {'lines': -1, 'codes': 0, 'chars': 0}
        self.__dict__['_session'] = {'lines': 0, 'codes': 0, 'chars': 0,
                                     'lines_skipped': 0, 'current_run': 1,
                                     'runs_done': 0}
        self.__dict__['_current'] = {}
        self.__dict__['_previous'] = {}
        ribbon = self.__dict__['_ribbon']
        code_generator = (code for (code, _) in
                          (p.parse_record(x) for x in ribbon_contents) if code)
        for code in code_generator:
            # Guards against empty combination i.e. line with comment only
            ribbon['codes'] += 1
            # When row 16 is encountered, ask user for addressing mode
            # (depends on the machine - most common is 15x17 and unit-shift)
            row_16_supported = mode.unitshift or mode.hmn or mode.kmn
            if '16' in code and not row_16_supported:
                # Do it now - before casting starts!
                mode.choose_row16_addressing()
            if p.check_newline(code):
                ribbon['lines'] += 1
            elif p.check_character(code):
                ribbon['chars'] += 1

    @ribbon_parameters.setter
    def queue(self, queue):
        """Parses the ribbon, counts combinations, lines and characters"""
        # Clear and start with -1 line for the initial galley trip
        self.__dict__['_run'] = {'lines': -1, 'codes': 0, 'chars': 0,
                                 'lines_skipped': 0}
        run = self.__dict__['_run']
        code_generator = (code for (code, _) in
                          (p.parse_record(x) for x in queue) if code)
        for code in code_generator:
            # Guards against empty combination i.e. line with comment only
            run['codes'] += 1
            if p.check_newline(code):
                run['lines'] += 1
            elif p.check_character(code):
                run['chars'] += 1

    @code_parameters.setter
    def signals(self, signals):
        """Updates the stats based on current combination"""
        if not signals:
            return
        # Save previous state
        current = self.__dict__['_current']
        run = self.__dict__['_run']
        session = self.__dict__['_session']
        self.__dict__['_previous'] = {k: v for k, v in current.items()}
        # Update combination info
        current['signals'] = signals
        run['current_code'] = run.get('current_code', 0) + 1
        session['current_code'] = session.get('current_code', 0) + 1
        if p.check_character(signals):
            run['current_char'] = run.get('current_char', 0) + 1
            session['current_char'] = session.get('current_char', 0) + 1
        elif self._check_double_justification():
            run['current_line'] = run.get('current_line', 0) + 1
            session['current_line'] = session.get('current_line', 0) + 1
        # Check the pump working/non-working status in the casting mode
        if self.session.caster.mode.casting:
            self._update_wedge_positions()
            self._check_pump()

    def _check_pump(self):
        """Checks pump based on current and previous combination"""
        prev_signals = self.__dict__.get('_previous', {}).get('signals', [])
        curr_signals = self.__dict__.get('_current', {}).get('signals', [])
        # Was it running until now? Get it from the caster
        running = self.session.caster.pump_working
        # Was it started before (0075 with or without 0005)?
        started = p.check_0075(prev_signals)
        # Was it stopped (0005 without 0075)
        stopped = p.check_0005(prev_signals) and not p.check_0075(prev_signals)
        # Is 0005 or 0075 in current combination? (if so - temporary stop)
        on_hold = p.check_0005(curr_signals) or p.check_0075(curr_signals)
        # Determine the current status
        pump_status = (running or started) and not stopped and not on_hold
        current = self.__dict__.get('_current', {})
        current['pump_working'] = pump_status
        # Feed it back to the caster object
        self.session.caster.pump_working = current.get('pump_working', False)

    def _update_wedge_positions(self):
        """Gets current positions of 0005 and 0075 wedges"""
        combination = self.__dict__.get('_current', {}).get('signals', [])
        # Check 0005
        if p.check_0005(combination):
            candidates = [x for x in range(15) if str(x) in combination]
            self.__dict__['_current']['0005'] = (str(max(candidates))
                                                 if candidates else '15')
        # Check 0075
        if p.check_0075(combination):
            candidates = [x for x in range(15) if str(x) in combination]
            self.__dict__['_current']['0075'] = (str(max(candidates))
                                                 if candidates else'15')

    def _check_double_justification(self):
        """Checks the current and previous signals for 0075+0005 -> 0075
        transition (which is used for detecting new line accurately)."""
        before = self.__dict__.get('_previous', {}).get('signals', [])
        now = self.__dict__.get('_current', {}).get('signals', [])
        return p.check_newline(before) and p.check_pump_start(now)


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
