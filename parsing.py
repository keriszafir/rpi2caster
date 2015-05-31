# -*- coding: utf-8 -*-
"""Parser methods.

This module contains file- and line-parsing methods."""

def read_file(filename):
    """Tries to read a file.
    
    Returns its contents (if file is readable), or False otherwise.
    """
# Open a file with signals, test if it's readable and return its contents
    try:
        content = []
        with open(filename, 'r') as inputfile:
            contentGenerator = inputfile.readlines()
            for line in contentGenerator:
                content.append(line)
            return content
    except IOError:
        return False

def comments_parser(inputData):
    """comments_parser(inputData):

    Parses an input string, and returns a list with two elements:
    -the Monotype signals (unprocessed),
    -any comments delimited by symbols from commentSymbols list.
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
    try:
        ' '.join(inputData)
    except:
        inputData = str(inputData)

    commentSymbols = ['**', '*', '//', '##', '#']
    # Assume we don't have a comment...
    rawSignals = inputData
    comment = ''
    # ...then look for comment symbols and parse them:
    for symbol in commentSymbols:
        if symbol in inputData:
        # Split on the first encountered symbol
            [rawSignals, comment] = inputData.split(symbol)
            break
    # Return a list with unprocessed signals and comment
    return [rawSignals.strip(), comment.strip()]

def count_lines_and_characters(contents):
    """Count newlines and characters+spaces in ribbon file.

    This is usually called when pre-processing the file.
    """
    linesAll = 0
    charsAll = 0
    for line in contents:
    # Strip comments
        signals = comments_parser(line)[0]
    # Parse the signals part of the line
        signals = signals_parser(signals)
        if check_character(signals):
            charsAll += 1
        elif check_newline(signals):
            linesAll += 1
    return [linesAll, charsAll]

def count_combinations(contents):
    """Count all combinations in ribbon file.

    This is usually called when pre-processing the file."""
    combinationsAll = 0
    for line in contents:
    # Strip comments
        signals = comments_parser(line)[0]
    # If there are signals, increment the combinations counter
        if signals_parser(signals):
            combinationsAll += 1
    # Return the number
    return combinationsAll

def signals_parser(rawSignals):
    """signals_parser(rawSignals):

    Parses a string with Monotype signals on input.
    Skips all but the "useful" signals: A...O, 1...15, 0005, S, 0075.
    Outputs a list of signals to be processed by send_signals_to_caster
    in Monotype (or MonotypeSimulation) classes.

    Filter out all non-alphanumeric characters and whitespace.
    Convert to uppercase.
    """
    rawSignals = filter(str.isalnum, rawSignals).upper()
    # Codes for columns, rows and justification will be stored
    # separately and sorted on output
    columns = []
    rows = []
    justification = []
    for sig in ['0005', '0075', 'S']:
    # First, detect justification signals: 0005, 0075, S.
    # We can't append a signal more than once (i.e. double 0005 etc.)
        if sig in rawSignals and sig not in justification:
            justification.append(sig)
        # We operate on a string, so cannot remove the item...
            rawSignals = rawSignals.replace(sig, '')
    # Look for any numbers between 16 and 100, remove them
    for n in range(100, 15, -1):
        rawSignals = rawSignals.replace(str(n), '')
    # From remaining numbers, determine row numbers.
    # Don't repeat yourself - if number is found twice, it'll be appended
    # to the rows only once.
    for n in range(15, 0, -1):
        if str(n) in rawSignals and str(n) not in rows:
            rows.append(str(n))
        rawSignals = rawSignals.replace(str(n), '')
    # Treat signals as a list from now on
    rawSignals = list(rawSignals)
    # Filter the list, dump all letters beyond O
    # (S was taken care of earlier). That will be the column signals.
    columns = filter(lambda s: s in list('ABCDEFGHIJKLMNO'), rawSignals)
    # Make sure no signal appears more than once, and sort them
    columns = sorted(set(columns))
    # Return a list containing all signals
    return columns + rows + justification

def strip_O_and_15(signals):
    # Strip O and 15 signals from input sequence, we don't cast them
    return filter(lambda s: s not in ['O', '15'], signals)

def convert_O15(inputSignals):
    """Convert O or 15 to O15.

    Combines O and 15 signals to a single O15 signal that can be fed
    to keyboard control routines when punching the ribbon.
    """
    signals = inputSignals
    if 'O' in signals or '15' in signals:
        signals.append('O15')
    # Now remove the individual O and 15 signals
    strip_O_and_15(signals)
    return signals

def check_newline(signals):
    """check_newline(signals):

    Checks if the newline (0005, 0075 or NKJ) is present in combination.
    This is called for each new line when parsing the ribbon file
    during casting.
    """
    return (set(['0005', '0075']).issubset(signals)
            or set(['N', 'K', 'J']).issubset(signals))

def check_character(signals):
    """Check if the combination is a character.

    Not-characters (no type is cast) are:
    0005 (pump off) or NJ (pump off, unit-adding),
    0075 (pump on) or NK (pump on, unit-adding),
    0005 0075 (galley trip) or NKJ (galley trip, unit-adding),
    empty sequence.
    """
    return (signals
            and not '0005' in signals
            and not '0075' in signals
            and not set(['N', 'K']).issubset(signals)
            and not set(['N', 'J']).issubset(signals))
