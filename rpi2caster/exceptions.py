# -*- coding: utf-8 -*-
"""Contains custom exceptions for the rpi2caster package. """


class ExceptionRoot(Exception):
    """Superclass for all custom exceptions defined for rpi2caster"""


class DatabaseOops(ExceptionRoot):
    """Superclass for database exceptions"""


class ConfigOops(ExceptionRoot):
    """Config-related exceptions"""


class CastingOops(ExceptionRoot):
    """Superclass for errors in the casting process"""


class MissingDependency(ExceptionRoot):
    """Raised when dependencies are not satisfied."""
    pass


class UIOops(ExceptionRoot):
    """Exceptions raised and caught by the UI"""
    pass


class TypesettingOops(ExceptionRoot):
    """Exceptions raised in the typpesetting process"""


class CastingAborted(CastingOops):
    """Raised when casting is aborted due to machine stop."""
    pass


class MachineStopped(CastingOops):
    """Raised by the caster control routines, when the machine stops."""
    pass


class EmergencyStop(CastingOops):
    """Raised when user pushes the emergency stop button to abort."""
    pass


class ReturnToMenu(UIOops):
    """Raised when a method wants to exit to menu."""
    pass


class MenuLevelUp(UIOops):
    """Raised in submenus, to go up to a higher level"""
    pass


class ExitProgram(UIOops):
    """Raised when user decides to exit program."""
    pass


class ChangeParameters(UIOops):
    """Raised when user decides to change parameters in a current routine. """
    pass


class Row16(ChangeParameters):
    """Raised when row 16 found in parsing - turn on HMN/KMN/unit-shift"""
    pass


class ConfigFileUnavailable(ConfigOops):
    """Raised when a config file does not exist or cannot be read."""
    pass


class WrongConfiguration(ConfigOops):
    """Raised when a parameter is not configured correctly."""
    pass


class NotConfigured(ConfigOops):
    """Raised when a section or parameter is missing."""


class NoMatchingData(DatabaseOops):
    """Raised when a database query yields no matches."""
    pass


class DatabaseQueryError(DatabaseOops):
    """Raised by the low-level database module as a general exception
    if a SQL query fails to execute.
    """
    pass


class MatrixNotFound(TypesettingOops):
    """Raised when the typesetting program could not find a desired
    character in the diecase layout."""
    pass


class DuplicateError(TypesettingOops):
    """DuplicateError

    Raised when trying to add a duplicate item:
    matrix (with identical coordinates), diecase (with identical ID).
    """
    pass

# Little helper functions that raise the exceptions


def return_to_menu():
    """Wrapper for raising ReturnToMenu where a function is needed"""
    raise ReturnToMenu


def abort_casting():
    """Wrapper for raising CastingAborted where a function is needed"""
    raise CastingAborted


def menu_level_up():
    """Wrapper for raising MenuLevelUp where a function is needed"""
    raise MenuLevelUp


def exit_program():
    """Wrapper for raising ReturnToMenu where a function is needed"""
    raise ExitProgram


def change_parameters():
    """Wrapper for raising ChangeParameters where a function is needed"""
    raise ChangeParameters
