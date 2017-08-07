# -*- coding: utf-8 -*-
"""Functions and classes for parsing strings/iterables for usable data."""
from collections import namedtuple
from contextlib import suppress
from functools import lru_cache
from itertools import zip_longest
import re

from .definitions import ALIGN_COMMANDS

# parsing delimiters
COMMENT_SYMBOLS = ['**', '*', '//', '##', '#']
ASSIGNMENT_SYMBOLS = ['=', ':', ' ']

# definitions
ParsedRecord = namedtuple('ParsedRecord',
                          ('raw signals comment column row has_signals is_char'
                           ' uses_row_16 has_0005 has_0075 has_s_needle '
                           'is_pump_start is_pump_stop is_newline'))


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
        for symbol in COMMENT_SYMBOLS:
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

    def analyze():
        """Check if signals perform certain functions"""
        has_signals = any((columns, rows, justification))
        column = (None if not has_signals
                  else 'NI' if set('NI').issubset(columns)
                  else 'NL' if set('NL').issubset(columns)
                  else columns[0] if columns else 'O')
        row = None if not has_signals else rows[0] if rows else 15
        has_0005 = '0005' in justification or set('NJ').issubset(columns)
        has_0075 = '0075' in justification or set('NK').issubset(columns)
        uses_row_16 = row == 16
        is_pump_start = has_0075
        is_pump_stop = has_0005 and not has_0075
        is_newline = has_0005 and has_0075
        is_char = not justification
        has_s_needle = 'S' in signals

        return dict(has_signals=has_signals, column=column, row=row,
                    has_0005=has_0005, has_0075=has_0075, is_char=is_char,
                    is_newline=is_newline, uses_row_16=uses_row_16,
                    is_pump_start=is_pump_start, is_pump_stop=is_pump_stop,
                    has_s_needle=has_s_needle)

    # we know signals and comment right away
    raw_signals, comment = split_on_delimiter(input_data)
    signals = raw_signals

    # read the signals to know what's inside
    justification = tuple(x for x in ('0075', '0005') if find(x))
    parsed_rows = [x for x in range(16, 0, -1) if find(x)]
    rows = tuple(x for x in reversed(parsed_rows))
    columns = tuple(x for x in [*'ABCDEFGHIJKLMNO'] if find(x))

    return ParsedRecord(signals=raw_signals, comment=comment,
                        raw=input_data, **analyze())


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
                for sym in ASSIGNMENT_SYMBOLS:
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


def cut_to_paragraphs(text):
    """Cut a source text into paragraphs."""
    # split on all control codes for alignment/justification,
    # as well as a double newline
    commands = ['\n\n', *ALIGN_COMMANDS.keys()]
    tokens = '({})'.format('|'.join(re.escape(cmd) for cmd in commands))
    regex = re.compile(tokens)
    chunks = regex.split(text)
    # group the chunks by two to get (text, justification_code) pairs
    # if chunks has odd length, use '\n\n' (default justification)
    # as the alignment code for the last item
    return [(t, ALIGN_COMMANDS.get(c))
            for t, c in zip_longest(*[iter(chunks)] * 2, fillvalue='\n\n')]


def token_parser(source, *token_sources, skip_unknown=True):
    """Yields tokens (characters, control sequences), one by one,
    as they are found in the source.
    input_stream - iterable;
    skip_unknown - yield only the characters found in token_sources (default),
                   otherwise, unknown characters are also yielded
    token_sources - any number of iterables containing the tokens
                    we are looking for"""
    # Collect all tokens (characters, control sequences) from token_sources
    tokens = [token for sequence in token_sources for token in sequence]
    # Determine the maximum length of a token
    max_len = max(len(t) for t in tokens)
    # We have to skip a number of subsequent input stream characters
    # after a multi-character token is encountered
    skip_steps = 0
    # Characters which will be ignored and not redirected to output
    ignored_tokens = ('\n',)
    # What if char in text not present in diecase? Hmmm...
    for index, _ in enumerate(source):
        if skip_steps:
            # Skip the characters to be skipped
            skip_steps -= 1
            continue
        for i in range(max_len, 0, -1):
            # Start from longest, end with shortest
            with suppress(TypeError, AttributeError, ValueError):
                chunk = source[index:index+i]
                skip_steps = i - 1
                if chunk in ignored_tokens:
                    break
                elif chunk in tokens or i == 1 and not skip_unknown:
                    # Make sure that the function will yield chunks of 1 char
                    yield chunk
                    break
