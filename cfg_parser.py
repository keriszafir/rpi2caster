# -*- coding: utf-8 -*-
"""
conffile_parser

Module for reading and writing configuration from/to conffile.
"""
# Config parser for reading the interface settings
import ConfigParser
# Custom exceptions
import newexceptions
# Define some module constants
CONFIG_PATH = 'rpi2caster.conf'
TRUE_ALIASES = ['true', 'on', 'yes']
FALSE_ALIASES = ['false', 'off', 'no']


def initialize_config():
    """Initializes config.

    Looks for the configuration file, tests if it's readable.
    Throws an exception if errors occur.
    """
    try:
        with open(CONFIG_PATH, 'r'):
            cfg = ConfigParser.SafeConfigParser()
            cfg.read(CONFIG_PATH)
            return cfg
    except IOError:
        raise newexceptions.ConfigFileUnavailable


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
        try:
            if value.lower() in TRUE_ALIASES:
                # Return boolean True if option was marked as 1, on, true, yes
                return True
            elif value.lower() in FALSE_ALIASES:
                # Return False if the option was marked as 0, off, false, no
                return False
        except AttributeError:
            pass
        # Return the raw value - a list, a string, None etc.
        return value
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        # If section or option is not configured, return None
        return None


def section_not_found(section_name):
    """section_not_found:

    Indicates whether there's no section with a given name."""
    cfg = initialize_config()
    return not cfg.has_section(section_name)
