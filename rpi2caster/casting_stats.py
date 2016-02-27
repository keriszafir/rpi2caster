# -*- coding: utf-8 -*-
"""Casting stats - implements stats getting and setting"""
from . import parsing as p


class Stats(object):
    """Casting statistics gathering and displaying functions"""
    def __init__(self, session):
        self.__dict__['_current'] = {}
        self.__dict__['_previous'] = {}
        self.__dict__['_run_data'] = {}
        self.session = session
        self.ribbon = session.ribbon.contents

    def next_run(self):
        """Updates the info about the runs"""
        self.__dict__['_current']['run'] = self.current_run_number + 1
        self.__dict__['_runs_left'] = self.runs_left - 1

    def next_line(self):
        """Updates the info about the runs"""
        self.__dict__['_current']['line'] = self.current_line_number + 1
        self.__dict__['_run_data']['lines_left'] = self.lines_left - 1

    def next_char(self):
        """Updates the characters info"""
        self.__dict__['_current']['char'] = self.current_char_number + 1

    def add_run(self):
        """Adds one to all_runs number - in case of repeating the job"""
        self.runs += 1
        self.runs_left += 1

    @property
    def parameters(self):
        """Gets ribbon parameters"""
        source = self.__dict__.get('_run_data', {})
        return [('\n', '\nRibbon statistics'),
                (source.get('codes', 0), 'Combinations in ribbon'),
                (source.get('lines', 0), 'Lines to cast'),
                (source.get('chars', 0), 'Characters incl. spaces')]

    @property
    def session_parameters(self):
        """Displays the ribbon data"""
        source = self.__dict__.get('_run_data', {})
        runs = self.runs
        return [(runs, 'Casting runs'),
                (source.get('codes', 0) * runs, 'All codes'),
                (source.get('chars', 0) * runs, 'All chars'),
                (source.get('lines', 0) * runs, 'All lines')]

    @property
    def run_parameters(self):
        """Displays info at the beginning of each run"""
        source = self.__dict__.get('_run_data', {})
        data = []
        if not self.session.caster.mode.testing:
            data.append((source.get('run_codes', 0), 'Codes in the run'))
        if self.session.caster.mode.casting:
            data.append((source.get('run_chars', 0), 'Chars in the run'))
            data.append((source.get('run_lines', 0), 'Lines in the run'))
        return data

    @property
    def code_parameters(self):
        """Displays info about the current combination"""
        # General stats for all modes:
        current = self.__dict__.get('_current', {})
        new_line = p.check_newline(current.get('signals', []))
        char = p.check_character(current.get('signals', []))
        data = [(new_line and self.current_line_number, 'Starting a new line')]
        data.append((new_line and self.lines_left, 'Lines left'))
        data.append((' '.join(current.get('signals', [])), 'Combination'))
        data.append((current.get('code', []), 'Current code'))
        pump = {True: 'ON', False: 'OFF'}[current.get('pump_status', False)]
        # For casting and punching:
        if not self.session.caster.mode.diagnostics:
            data.append((char and self.current_char_number, 'Current char'))
        if self.session.caster.mode.casting:
            data.append((current.get('0075', '15'), 'Wedge 0075 now at'))
            data.append((current.get('0005', '15'), 'Wedge 0005 now at'))
            data.append((pump, 'Pump is'))
        return data

    @property
    def runs(self):
        """Gets the runs (repetitions) number"""
        return self.__dict__.get('_runs', 1)

    @runs.setter
    def runs(self, runs=1):
        """Sets the runs (repetitions) number"""
        self.__dict__['_runs'] = isinstance(runs, int) and runs or 1

    @property
    def runs_left(self):
        """Gets the runs (repetitions) number"""
        return self.__dict__.get('_runs_left', 1)

    @runs_left.setter
    def runs_left(self, runs=1):
        """Gets the runs (repetitions) number"""
        self.__dict__['_runs_left'] = isinstance(runs, int) and runs or 1

    @property
    def lines_left(self):
        """Gets the lines number"""
        return self.__dict__.get('_run_data', {}).get('lines_left', 1)

    @property
    def current_char_number(self):
        """Gets the current character number"""
        return self.__dict__.get('_current', {}).get('char', 0)

    @property
    def current_run_number(self):
        """Gets the current run number"""
        return self.__dict__.get('_current', {}).get('run', 1)

    @property
    def current_line_number(self):
        """Gets the current line number"""
        return self.__dict__.get('_current', {}).get('line', 0)

    @property
    def ribbon_lines(self):
        """Gets number of lines per ribbon"""
        return self.__dict__.get('_run_data', {}).get('lines', 1)

    @code_parameters.setter
    def signals(self, signals):
        """Updates the stats based on current combination"""
        # Save previous state
        current_dict = self.__dict__.get('_current', {})
        self.__dict__['_previous'] = {k: v for k, v in current_dict.items()}
        # Update combination info
        current_dict['signals'] = signals
        current_dict['code'] = current_dict.get('code', 0) + 1
        if p.check_character(signals):
            self.next_char()
        elif p.check_newline(signals):
            self.next_line()
        # Check the pump working/non-working status in the casting mode
        if self.session.caster.mode.casting:
            self._update_wedge_positions()
            self._check_pump()

    @session_parameters.setter
    def ribbon(self, ribbon):
        """Parses the ribbon, counts combinations, lines and characters"""
        mode = self.session.caster.mode
        run_data = self.__dict__['_run_data']
        run_data['codes'] = 0
        run_data['lines'] = 0
        run_data['chars'] = 0
        # Reset the character stats
        self.__dict__['_current'] = {}
        self.__dict__['_previous'] = {}
        generator = (p.parse_record(x) for x in ribbon)
        for (signals, _) in generator:
            if signals:
                # Guards against empty combination i.e. line with comment only
                run_data['codes'] += 1
            if '16' in signals and not mode.hmn and not mode.unitshift:
                mode.choose_row16_addressing()
            if p.check_newline(signals):
                run_data['lines'] += 1
            elif p.check_character(signals):
                run_data['chars'] += 1

    @run_parameters.setter
    def queue(self, queue):
        """Parses the ribbon, counts combinations, lines and characters"""
        run_data = self.__dict__['_run_data']
        run_data['run_codes'] = 0
        run_data['run_lines'] = 0
        run_data['run_chars'] = 0
        generator = (p.parse_record(x) for x in queue)
        for (combination, _) in generator:
            if combination:
                # Guards against empty combination i.e. line with comment only
                run_data['run_codes'] += 1
            if p.check_newline(combination):
                run_data['run_lines'] += 1
            elif p.check_character(combination):
                run_data['run_chars'] += 1
        run_data['lines_left'] = run_data['run_lines'] + 1

    def _check_pump(self):
        """Checks pump based on current and previous combination"""
        prev_code = self.__dict__.get('_previous', {}).get('signals', [])
        current_code = self.__dict__.get('_current', {}).get('signals', [])
        # Was it running until now? Get it from the pump object
        running = self.session.caster.pump.is_working
        # Was it started before (0075 with or without 0005)?
        started = p.check_0075(prev_code)
        # Was it stopped (0005 without 0075)
        stopped = p.check_0005(prev_code) and not p.check_0075(prev_code)
        # Is 0005 or 0075 in current combination? (if so - temporary stop)
        on_hold = p.check_0005(current_code) or p.check_0075(current_code)
        # Determine the current status
        pump_status = (running or started) and not stopped and not on_hold
        current = self.__dict__.get('_current', {})
        pump = self.session.caster.pump
        current['pump_status'] = pump_status
        # Feed it back to pump object
        pump.is_working = current.get('pump_status', False)
        pump.current_0005 = current.get('0005', '15')
        pump.current_0075 = current.get('0075', '15')

    def _update_wedge_positions(self):
        """Gets current positions of 0005 and 0075 wedges"""
        combination = self.__dict__.get('_current', {}).get('signals', [])
        # Check 0005
        if p.check_0005(combination):
            candidates = [x for x in range(15) if str(x) in combination]
            self.__dict__['_current']['0005'] = (candidates and
                                                 str(max(candidates)) or '15')
        # Check 0075
        if p.check_0075(combination):
            candidates = [x for x in range(15) if str(x) in combination]
            self.__dict__['_current']['0075'] = (candidates and
                                                 str(max(candidates)) or '15')
