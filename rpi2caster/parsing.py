# -*- coding: utf-8 -*-
"""Parser functions.

This module contains file- and line-parsing functions for the casting program.
"""
import io
from . import constants
# Check if alternate comment symbols are configured
from .constants import COMMENT_SYMBOLS


def read_file(filename):
    """Returns file contents (if file is readable), or False otherwise.
    Strips whitespace and removes empty lines."""
    # Open a file with signals, test if it's readable and return its contents
    try:
        with io.open(filename, 'r') as input_file:
            return [l.strip() for l in input_file if l.strip()]
    except (IOError, FileNotFoundError):
        return False


def parse_record(input_data):
    """Parses an input string, and returns a list with two elements:
    -the Monotype signals (unprocessed),
    -any comments delimited by symbols from COMMENT_SYMBOLS list.
    We need to work on strings. Convert any lists, integers etc.

    Looks for any comment symbols defined here - **, *, ##, #, // etc.
    splits the line at it and saves the comment to return it later on.
    If it's an inline comment (placed after Monotype code combination),
    this combination will be returned for casting.

    If a line in file contains a comment only, returns no combination.

    In case of column O and row 15 (no signals fed to machine), we still
    need to have the signals listed explicitly in the input sequence.
    The signals_parser will later remove them and convert to O15.

    Example:
    O15 //comment      <-- casts from O+15 matrix, displays comment
                       <-- nothing to do
    //comment          <-- displays comment, no casting
    0005 5 //comment   <-- sets 0005 justification wedge to 5,
                           turns pump off, displays comment.
    """
    # Should work both on lists and strings
    input_data = ''.join([str(x) for x in input_data])
    # Assume we don't have a comment...
    raw_signals = input_data
    comment = ''
    # ...then look for comment symbols and parse them:
    for symbol in COMMENT_SYMBOLS:
        if symbol in input_data:
            # Split on the first encountered symbol
            [raw_signals, comment] = input_data.split(symbol, 1)
            break
    # Parse the signals and return a list with processed signals and comment
    return [parse_signals(raw_signals), comment.strip()]


def parse_signals(input_signals):
    """Parses a string with Monotype signals on input.
    Skips all but the "useful" signals: A...O, 1...15, 0005, S, 0075.
    Outputs a list of signals to be processed by the machine control routines.
    Filter out all non-alphanumeric characters and whitespace.
    Convert to uppercase.
    """
    col_sigs = 'ABCDEFGHIJKLMNS'
    signals = (str(x).upper().strip() for x in input_signals)
    signals = (x for x in signals if x.isdigit() or x in col_sigs + 'O')
    signals = ''.join(signals)
    # Find O+15 or 16th row
    o15_found = 'O15' in signals or 'O' in signals or '15' in signals
    row_16_found = '16' in signals
    # Build a list of justification signals
    justification = [sig for sig in ['0005', '0075'] if sig in signals]
    # Remove these signals from the input string
    for sig in justification + [str(i) for i in range(100, 14, -1)]:
        # We operate on a string, so cannot remove the item...
        signals = signals.replace(sig, '')
    # From remaining numbers, determine row numbers.
    # The highest number will be removed from the raw_signals to avoid
    # erroneously adding its digits as signals.
    rows = row_16_found and ['16'] or []
    for row in range(14, 0, -1):
        if str(row) in signals:
            rows.append(str(row))
            signals = signals.replace(str(row), '')
    # Columns + S justification signal
    columns = [s for s in col_sigs if s in signals]
    # Return a list containing all signals and O15 if needed, if the input
    # string or list contained any useful combinations
    return justification + columns + rows + ['O15'] * o15_found or []


def count_lines_and_chars(contents):
    """Count newlines and characters+spaces in ribbon file.
    This is usually called when pre-processing the file for casting.
    """
    all_lines = 0
    all_chars = 0
    for line in contents:
        # Strip comments
        signals = parse_record(line)[0]
        # Parse the signals part of the line
        if check_character(signals):
            all_chars += 1
        elif check_newline(signals):
            all_lines += 1
    # -1 lines because of the starting galley trip / double justification code
    # Cannot be negative
    all_lines = max(0, all_lines - 1)
    return [all_lines, all_chars]


def count_combinations(contents):
    """Count all combinations in ribbon file.
    This is usually called when pre-processing the file for punching."""
    all_combinations = 0
    for line in contents:
        # Get signals list. Increase counter if we have signals.
        if parse_record(line)[0]:
            all_combinations += 1
    # Return the number
    return all_combinations


def stop_comes_first(contents):
    """Detects ribbon direction so that we can use the ribbons generated
    with different software and still cast them in correct order.
    This function loops over the ribbon to test if the stop sequence
    (NJ or 0005) comes before the newline sequence (NKJ or 0075+0005).
    If so, returns True (the ribbon needs to be rewound for casting).
    Otherwise, False."""
    start_found = False
    for line in contents:
        # Get the signals part of a line, discard the comment
        signals, _ = parse_record(line)
        # Toggle this to True if newline combinations are found
        start_found = start_found or check_newline(signals)
        # Determine the result the first time pump stop combination is found
        if check_pump_stop(signals) and not start_found:
            return True
        elif start_found:
            return False


def get_column(signals):
    """Gets the lowest column number from the signals list."""
    decoded_signals = ({'N', 'I'}.issubset(signals) and 'NI' or
                       {'N', 'L'}.issubset(signals) and 'NL' or signals)
    generator = (x for x in constants.COLUMNS_17 if x in decoded_signals)
    try:
        return next(generator)
    except StopIteration:
        return 'O'


def get_row(signals):
    """Gets the lowest row number from the signal list. Returns int."""
    generator = (row for row in range(17) if str(row) in signals)
    try:
        return next(generator)
    except StopIteration:
        return 15


def check_0075(signals):
    """Checks if signals contain 0075 or NK."""
    return '0075' in signals or {'N', 'K'}.issubset(signals)


def check_0005(signals):
    """Checks if signals contain 0005 or NJ."""
    return '0005' in signals or {'N', 'J'}.issubset(signals)


def check_newline(signals):
    """Checks if the newline (0005, 0075 or NKJ) is present in combination.
    This is called for each new line when parsing the ribbon file when casting.
    """
    return check_0075(signals) and check_0005(signals)


def check_pump_stop(signals):
    """Checks if the signals will stop the pump"""
    return check_0005(signals) and not check_0075(signals)


def check_pump_start(signals):
    """Checks if the signals will stop the pump"""
    return check_0075(signals)


def check_character(signals):
    """Check if this is a character i.e. no 0005/NJ and no 0075/NK in code."""
    return signals and not check_0005(signals) and not check_0075(signals)
