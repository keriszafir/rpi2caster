# -*- coding: utf-8 -*-
"""Casting stats model"""
from collections import defaultdict, OrderedDict
from contextlib import suppress

# Dictionaries storing the casting statistics
RIBBON, SESSION, RUN = defaultdict(int), defaultdict(int), defaultdict(int)
CURRENT = defaultdict(lambda: defaultdict(str))
PREVIOUS = defaultdict(lambda: defaultdict(str))


def update(**kwargs):
    """Update parameters"""
    def session_line_skip(lines):
        """skip lines for every run in the session"""
        SESSION['lines_skipped'] = lines

    def run_line_skip(lines):
        """skip lines for a single run"""
        RUN['lines_skipped'] = lines

    def add_runs(delta):
        """change a number of runs in casting session"""
        old_value = SESSION['runs']
        num_runs = old_value + delta
        SESSION['runs'] = num_runs
        SESSION['codes'] = num_runs * RIBBON['codes']
        SESSION['chars'] = num_runs * RIBBON['chars']
        SESSION['lines'] = num_runs * RIBBON['lines']

    def end_run(success):
        """Updates the info about the runs"""
        if success:
            # update the counters
            SESSION['runs_done'] += 1
            SESSION['current_run'] += 1
        else:
            # reset last run stats - don't update the counters
            SESSION['failed_runs'] += 1
            for par in ('current_line', 'current_code', 'current_char'):
                SESSION[par] -= RUN[par]

    parameters = dict(ribbon=update_session_stats,
                      queue=update_run_stats,
                      record=update_record_stats,
                      session_line_skip=session_line_skip,
                      run_line_skip=run_line_skip,
                      runs=add_runs,
                      casting_success=end_run)
    for argument, value in kwargs.items():
        routine = parameters.get(argument)
        if not routine:
            continue
        return routine(value)


def reset():
    """Resets all the statistics"""
    RUN.clear()
    SESSION.clear()
    RIBBON.clear()
    CURRENT.clear()
    PREVIOUS.clear()


def runs():
    """Gets the runs (repetitions) number"""
    return SESSION['runs']


def runs_left():
    """Gets the runs left number"""
    diff = SESSION['runs'] - SESSION['runs_done']
    return max(0, diff)


def lines_done():
    """Gets the current run line number"""
    return max(0, RUN['current_line'] - 1)


def ribbon_lines():
    """Gets number of lines per ribbon"""
    return RIBBON['lines']


def run_lines_skipped():
    """Get a number of lines to skip - decide whether to use
    the run or ribbon skipped lines"""
    return RUN['lines_skipped'] or SESSION['lines_skipped']


def ribbon_parameters():
    """Gets ribbon parameters"""
    parameters = OrderedDict({'': 'Ribbon parameters'})
    parameters['Combinations in ribbon'] = RIBBON['codes']
    parameters['Characters incl. spaces'] = RIBBON['chars']
    parameters['Lines to cast'] = RIBBON['lines']
    return parameters


def session_parameters():
    """Displays the ribbon data"""
    # display this only for multi-run sessions
    if SESSION['runs'] < 2:
        return {}
    parameters = OrderedDict({'': 'Casting session parameters'})
    parameters['Casting runs'] = SESSION['runs']
    parameters['All codes'] = SESSION['codes']
    parameters['All chars'] = SESSION['chars']
    parameters['All lines'] = SESSION['lines']
    return parameters


def code_parameters():
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

    record = CURRENT['record']
    runs_number = SESSION['runs']
    # display comment as a header
    info = OrderedDict({'': record.comment})
    # display codes
    info['Raw signals from ribbon'] = record.signals
    if record.is_newline:
        info['Starting a new line'] = RUN['current_line']
    if runs_number > 1:
        info['Code / run'] = build_info(RUN, 'code')
        info['Char / run'] = build_info(RUN, 'char')
        info['Line / run'] = build_info(RUN, 'line')
        info['Run / job'] = build_info(SESSION, 'run')
        info['Failed runs'] = SESSION['failed_runs']
    info['Code / job'] = build_info(SESSION, 'code')
    info['Char / job'] = build_info(SESSION, 'char')
    info['Line / job'] = build_info(SESSION, 'line')
    return info


def update_session_stats(ribbon):
    """Parses the ribbon, counts combinations, lines and characters"""
    # first, reset counters
    SESSION.clear()
    RIBBON.clear()
    PREVIOUS.clear()
    CURRENT.clear()
    # parse the ribbon to read its stats
    records = [record for record in ribbon if record.has_signals]
    # number of codes is just a number of valid combinations
    num_codes = len(records)
    # ribbon starts and ends with newline, so lines = newline codes - 1
    num_lines = sum(1 for record in records if record.is_newline) - 1
    # characters: if combination has no justification codes
    num_chars = sum(1 for record in records if record.is_char)
    # Set ribbon and session counters
    RIBBON.update(codes=num_codes, chars=num_chars, lines=max(0, num_lines))
    SESSION.update(lines_skipped=0, current_run=1,
                   current_line=0, current_code=0, current_char=0)


def update_run_stats(queue):
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
    RUN.update(lines_skipped=0,
               current_line=0, current_code=0, current_char=0,
               lines=num_lines, codes=num_codes, chars=num_chars)


def update_record_stats(record):
    """Updates the stats based on parsed signals."""
    # Update previous stats and current record
    PREVIOUS.clear()
    PREVIOUS.update(CURRENT)
    CURRENT['record'] = record
    # advance or set the run and session code counters
    RUN['current_code'] += 1
    SESSION['current_code'] += 1
    # detect 0075+0005(+pos_0005)->0075(+pos_0075) = double justification
    # this means starting new line
    with suppress(AttributeError):
        was_newline = PREVIOUS['record'].is_newline
        if was_newline and record.is_pump_start:
            RUN['current_line'] += 1
            SESSION['current_line'] += 1
    # advance or set the character counters
    RUN['current_char'] += 1 * record.is_char
    SESSION['current_char'] += 1 * record.is_char
