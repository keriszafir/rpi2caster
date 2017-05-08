# -*- coding: utf-8 -*-
"""Contains functions used for justification, control sequences etc."""


def single_j(pos_0075=3, pos_0005=8, fwd=False,
             comment='Single justification'):
    """Add 0075 + pos_0075, then 0005 + pos_0005"""
    return (pump_start(pos_0075, comment) if pos_0075 == pos_0005
            else pump_stop(pos_0005) + pump_start(pos_0075, comment) if fwd
            else pump_start(pos_0075, comment) + pump_stop(pos_0005))


def double_j(pos_0075=3, pos_0005=8, fwd=False,
             comment='Double justification'):
    """Add 0075 + pos_0075, then 0005-0075 + pos_0005"""
    return (galley_trip(pos_0075, comment) if pos_0075 == pos_0005
            else galley_trip(pos_0005) + pump_start(pos_0075, comment) if fwd
            else pump_start(pos_0075, comment) + galley_trip(pos_0005))


def galley_trip(pos_0005=8, comment='Line to the galley'):
    """Put the line to the galley"""
    code = 'NKJS 0075 0005 {}'.format(pos_0005)
    return ['{:<20} // {}'.format(code, comment or '')]


def pump_start(pos_0075=3, comment='Starting the pump'):
    """Start the pump and set 0075 wedge"""
    code = 'NKS 0075 {}'.format(pos_0075)
    return ['{:<20} // {}'.format(code, comment or '')]


def pump_stop(pos_0005=8, comment='Stopping the pump'):
    """Stop the pump"""
    code = 'NJS 0005 {}'.format(pos_0005)
    return ['{:<20} // {}'.format(code, comment or '')]


def end_casting(fwd=False):
    """Alias for ending the casting job"""
    text1, text2 = 'End casting', 'Last line out'
    return (galley_trip(comment=text2) + pump_stop(comment=text1) if fwd
            else pump_stop(comment=text1) + galley_trip(comment=text2))
