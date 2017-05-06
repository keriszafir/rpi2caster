# -*- coding: utf-8 -*-
"""Contains functions used for justification, control sequences etc."""


def single_justification(pos_0075=3, pos_0005=8,
                         comment='Single justification'):
    """Add 0075 + pos_0075, then 0005 + pos_0005"""
    return (pump_start(pos_0075, comment) if pos_0075 == pos_0005
            else pump_start(pos_0075, comment) + pump_stop(pos_0005))


def double_justification(pos_0075=3, pos_0005=8,
                         comment='Double justification'):
    """Add 0075 + pos_0075, then 0005-0075 + pos_0005"""
    return (galley_trip(pos_0075, comment) if pos_0075 == pos_0005
            else pump_start(pos_0075, comment) + galley_trip(pos_0005))


def galley_trip(pos_0005=8, comment='Line to the galley'):
    """Put the line to the galley"""
    attach = (' // ' + comment) if comment else ''
    return ['NKJS 0075 0005 {}{}'.format(pos_0005, attach)]


def pump_start(pos_0075=3, comment='Starting the pump'):
    """Start the pump and set 0075 wedge"""
    attach = (' // ' + comment) if comment else ''
    return ['NKS 0075 {}{}'.format(pos_0075, attach)]


def pump_stop(pos_0005=8, comment='Stopping the pump'):
    """Stop the pump"""
    attach = (' // ' + comment) if comment else ''
    return ['NJS 0005 {}{}'.format(pos_0005, attach)]


def end_casting():
    """Alias for ending the casting job"""
    return (pump_stop(comment='End casting') +
            galley_trip(comment='Last line out'))
