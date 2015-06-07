# -*- coding: utf-8 -*-
"""
conffile_parser

Module for reading and writing configuration from/to conffile.
"""
# Config parser for reading the interface settings
import ConfigParser
# Define some module constants
DEFAULT_CONFIG_PATH = 'rpi2caster.conf'
TRUE_ALIASES = ['true', '1', 'on', 'yes']
FALSE_ALIASES = ['false', '0', 'off', 'no']


def get_config(section_name, option_name, config_path=DEFAULT_CONFIG_PATH):
    """get_config:

    Gets a value for a given parameter from a given name.
    Returns:
      -int - if the value is numeric,
      -boolean - if the value was in one of the true or false aliases,
      -string otherwise,
      -None if there is no option or section of that name.
    """
    try:
        with open(config_path, 'r'):
            cfg = ConfigParser.SafeConfigParser()
            cfg.read(config_path)
    except IOError:
        print('Cannot open config file:', config_path)
    # Now the function proper...
    try:
        # Return an integer value whenever we can
        return int(cfg.get(section_name, option_name))
    except (ValueError, TypeError):
        # Get the value and decide what to do with it
        value = cfg.get(section_name, option_name)
        if value.lower() in TRUE_ALIASES:
            # Return boolean True if option was marked as 1, on, true, yes
            return True
        elif value.lower() in FALSE_ALIASES:
            # Return False if the option was marked as 0, off, false, no
            return False
        else:
            # Return the raw value - a list, a string etc.
            return value
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        # If section or option is not configured, return None
        return None
