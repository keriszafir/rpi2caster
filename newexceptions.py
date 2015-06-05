# -*- coding: utf-8 -*-
"""
Exceptions

Contains custom exceptions for all rpi2caster modules.
"""
class CastingAborted(Exception):
    """CastingAborted

    Exception which is raised when casting is aborted due to machine stop.
    """
    pass


class ReturnToMenu(Exception):
    """ReturnToMenu

    Exception raised when a method wants to exit to menu.
    """
    pass

class ExitProgram(Exception):
    """ExitProgram

    Exception raised when user decides to exit program.
    """
    pass

class ChangeParameters(Exception):
    """ChangeParameters

    Exception raised when user decides to change parameters
    in a current routine.
    """
    pass
