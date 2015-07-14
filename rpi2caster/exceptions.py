"""
Exceptions

Contains custom exceptions for the rpi2caster package.
"""


class MissingDependency(Exception):
    """Raised when dependencies are not satisfied."""
    pass


class CastingAborted(Exception):
    """Raised when casting is aborted due to machine stop."""
    pass


class MachineStopped(Exception):
    """Raised by the caster control routines, when the machine stops."""
    pass


class EmergencyStop(Exception):
    """Raised when user pushes the emergency stop button to abort."""
    pass


class ReturnToMenu(Exception):
    """Raised when a method wants to exit to menu."""
    pass


class MenuLevelUp(Exception):
    """Raised in submenus, to go up to a higher level"""
    pass


class ExitProgram(Exception):
    """Raised when user decides to exit program."""
    pass


class ChangeParameters(Exception):
    """Raised when user decides to change parameters in a current routine.
    """
    pass


class ConfigFileUnavailable(Exception):
    """Raised when a config file does not exist or cannot be read."""
    pass


class WrongConfiguration(Exception):
    """Raised when a parameter is not configured correctly."""
    pass


class NotConfigured(Exception):
    """Raised when a section or parameter is missing."""


class NoMatchingData(Exception):
    """Raised when a database query yields no matches."""
    pass


class DatabaseQueryError(Exception):
    """Raised by the low-level database module as a general exception
    if a SQL query fails to execute.
    """
    pass


class MatrixNotFound(Exception):
    """Raised when the typesetting program could not find a desired
    character in the diecase layout."""
    pass


class DuplicateError(Exception):
    """DuplicateError

    Raised when trying to add a duplicate item:
    matrix (with identical coordinates), diecase (with identical ID).
    """
    pass

# Little helper functions that raise the exceptions


def return_to_menu():
    """Wrapper for raising ReturnToMenu where a function is needed"""
    raise ReturnToMenu


def menu_level_up():
    """Wrapper for raising MenuLevelUp where a function is needed"""
    raise MenuLevelUp


def exit_program():
    """Wrapper for raising ReturnToMenu where a function is needed"""
    raise ExitProgram


def change_parameters():
    """Wrapper for raising ChangeParameters where a function is needed"""
    raise ChangeParameters
