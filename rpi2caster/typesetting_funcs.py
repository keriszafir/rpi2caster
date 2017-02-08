# -*- coding: utf-8 -*-
"""
typesetting_funcs:

Contains functions used for typesetting, justification, control sequences etc.
"""
from contextlib import ignored


def token_parser(source, skip_unknown=True, *token_sources):
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
            with ignored(TypeError, AttributeError, ValueError):
                chunk = source[index:index+i]
                skip_steps = i - 1
                if chunk in ignored_tokens:
                    break
                elif chunk in tokens or not skip_unknown:
                    yield chunk
                    break


def justify_left(text):
    """Adds spaces at the end of the line"""
    pass


def justify_right(text):
    """Adds spaces at the beginning of the line"""
    pass


def justify_center(text):
    """Adds spaces at both sides, centering the line"""
    pass


def justify_both(text):
    """Uses variable spaces to stretch the text between edges"""
    pass


def single_justification(wedge_positions=(3, 8),
                         comment='Single justification'):
    """Add 0075 + pos_0075, then 0005 + pos_0005"""
    (pos_0075, pos_0005) = wedge_positions
    return (pump_start(pos_0075, comment) if pos_0075 == pos_0005
            else pump_start(pos_0075, comment) + pump_stop(pos_0005))


def double_justification(wedge_positions=(3, 8),
                         comment='Double justification'):
    """Add 0075 + pos_0075, then 0005-0075 + pos_0005"""
    (pos_0075, pos_0005) = wedge_positions
    return (galley_trip(pos_0075, comment) if pos_0075 == pos_0005
            else pump_start(pos_0075, comment) + galley_trip(pos_0005))


def galley_trip(pos_0005=8, comment='Line to the galley'):
    """Put the line to the galley"""
    attach = (' // ' + comment) if comment else ''
    return ['NKJS 0075 0005 %s%s' % (pos_0005, attach)]


def pump_start(pos_0075=3, comment='Starting the pump'):
    """Start the pump and set 0075 wedge"""
    attach = (' // ' + comment) if comment else ''
    return ['NKS 0075 %s%s' % (pos_0075, attach)]


def pump_stop(pos_0005=8, comment='Stopping the pump'):
    """Stop the pump"""
    attach = (' // ' + comment) if comment else ''
    return ['NJS 0005 %s%s' % (pos_0005, attach)]


def end_casting():
    """Alias for ending the casting job"""
    return (pump_stop(comment='End casting') +
            galley_trip(comment='Last line out'))
