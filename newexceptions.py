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

class ExitProgram(Exception):
    """ExitProgram

    Exception raised when user decides to exit program.
    """