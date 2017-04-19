# -*- coding: utf-8 -*-
"""Functions and classes for parsing strings/iterables for usable data."""
from contextlib import suppress
from . import definitions as d


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
