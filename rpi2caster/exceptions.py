# -*- coding: utf-8 -*-
"""
Exceptions

Contains custom exceptions for the rpi2caster package.
"""

class CastingAborted(Exception):
    """CastingAborted

    Raised when casting is aborted due to machine stop.
    """
    pass


class EmergencyStop(Exception):
    """EmergencyStop

    Raised when user pushes the emergency stop button to abort.
    """
    pass


class ReturnToMenu(Exception):
    """ReturnToMenu

    Raised when a method wants to exit to menu.
    """
    pass


class ExitProgram(Exception):
    """ExitProgram

    Raised when user decides to exit program.
    """
    pass


class ChangeParameters(Exception):
    """ChangeParameters

    Raised when user decides to change parameters in a current routine.
    """
    pass


class ConfigFileUnavailable(Exception):
    """ConfigFileUnavailable

    Raised when a config file does not exist or cannot be read.
    """
    pass


class WrongConfiguration(Exception):
    """WrongConfiguration

    Raised when a parameter is not configured correctly.
    """
    pass


class NoMatchingData(Exception):
    """NoMatchingData
    
    Raised when a database query yields no matches.
    """
