#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""Unit tests for parsing module"""

from rpi2caster import parsing
from rpi2caster import constants as c


def test_parser(row_16_addressing=None, default_o15=False, signal_o15=False):
    """Test the signals parser on a number of combinations of signals
    from row 0 (no row), 1 (control), 15 and 16, for a given row addressing."""
    combinations = ('%s%s' % (x, y)
                    for y in (0, 1, 15, 16) for x in c.COLUMNS_17)
    for combo in combinations:
        parser = parsing.ParsedRecord(combo, signal_o15, default_o15,
                                      row_16_addressing)
        print('raw signals', combo, 'parsed signals', parser.signals_string,
              'adjusted signals', parser.adjusted_signals_string)


def test_modes():
    print('testing no row 16 addressing')
    test_parser(None)
    print('testing HMN')
    test_parser(c.HMN)
    print('testing KMN')
    test_parser(c.KMN)
    print('testing unit shift')
    test_parser(c.UNIT_SHIFT)


def test_explicit_o15():
    print('testing O15 appending to output signals')
    test_parser(signal_o15=True)
    print('testing auto-completing implicit O and 16 signals...')
    test_parser(signal_o15=True)


if __name__ == '__main__':
    test_modes()
    test_explicit_o15()
