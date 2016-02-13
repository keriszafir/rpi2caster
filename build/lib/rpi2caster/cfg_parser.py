# -*- coding: utf-8 -*-
"""
conffile_parser

Module for reading and writing configuration from/to conffile.
"""
import io
# Config parser for reading the interface settings
import configparser
# Global settings for rpi2caster
from . import global_settings
# Custom exceptions
from . import exceptions
# Package constants
from . import constants


def initialize_config():
    """Initializes config.

    Looks for the configuration file, tests if it's readable.
    Throws an exception if errors occur.
    """
    config_paths = ([global_settings.CONFIG_PATH] +
                    constants.DEFAULT_CONFIG_PATHS)
    for path in config_paths:
        try:
            with io.open(path, 'r'):
                cfg = configparser.SafeConfigParser()
                cfg.read(path)
                return cfg
        except (IOError, FileNotFoundError):
            # Try next
            continue
    # No config file specified can be accessed
    raise exceptions.ConfigFileUnavailable('Cannot access config file!')


def get_config(section_name, option_name):
    """get_config:

    Gets a value for a given parameter from a given name.
    Returns:
      -int - if the value is numeric,
      -boolean - if the value was in one of the true or false aliases,
      -string otherwise,
      -None if there is no option or section of that name.
    """
    cfg = initialize_config()
    try:
        # Return an integer value whenever we can
        return int(cfg.get(section_name, option_name))
    except (ValueError, TypeError):
        # Get the value and decide what to do with it
        value = cfg.get(section_name, option_name)
        return determine(value)
    except (configparser.NoSectionError, configparser.NoOptionError):
        # If section or option is not configured, raise an exception
        raise exceptions.NotConfigured


def determine(value):
    """Checks if the string means a hexdigit, None, True or False"""
    # Convert to lowercase:
    value = value.lower()
    try:
        if value.startswith('0x'):
            # Value is a hexstring: 0x or 0X
            return int(value, 16)
        elif value in ['none', 'null']:
            # Value was specified to be None or null
            return None
        elif value in constants.TRUE_ALIASES:
            # Return boolean True if option was marked as 1, on, true, yes
            return True
        elif value in constants.FALSE_ALIASES:
            # Return False if the option was marked as 0, off, false, no
            return False
        else:
            # Return an integer
            return int(value)
    except (ValueError, TypeError, AttributeError):
        # Do nothing if the value has no method we tried
        pass
    # Return the raw value - a list, a string, None etc.
    return value


def section_not_found(section_name):
    """section_not_found:

    Indicates whether there's no section with a given name."""
    cfg = initialize_config()
    return not cfg.has_section(section_name)
