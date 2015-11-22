# -*- coding: utf-8 -*-
"""
conffile_parser

Module for reading and writing configuration from/to conffile.
"""
import io
# Config parser for reading the interface settings
import configparser
# Global settings for rpi2caster
from rpi2caster import global_settings
# Custom exceptions
from rpi2caster import exceptions

# Define some module constants
config_paths = [global_settings.CONFIG_PATH,
                '/etc/rpi2caster.conf',
                '../data/rpi2caster.conf']
TRUE_ALIASES = ['true', 'on', 'yes']
FALSE_ALIASES = ['false', 'off', 'no']


def initialize_config():
    """Initializes config.

    Looks for the configuration file, tests if it's readable.
    Throws an exception if errors occur.
    """
    for path in config_paths:
        try:
            with io.open(path, 'r'):
                cfg = configparser.SafeConfigParser()
                cfg.read(path)
                return cfg
        except (IOError, FileNotFoundError):
            continue
    # No config file specified can be accessed
    raise exceptions.ConfigFileUnavailable


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
        elif value in TRUE_ALIASES:
            # Return boolean True if option was marked as 1, on, true, yes
            return True
        elif value in FALSE_ALIASES:
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


def get_caster_settings(caster_name):
    """get_caster_settings():

    Reads the settings for a caster with caster_name
    from the config file (where it is represented by a section, whose
    name is the same as the caster's).

    Returns perforator flag and interface ID.
    """
    is_perforator = get_config(caster_name, 'is_perforator')
    interface_id = get_config(caster_name, 'interface_id')
    # Caster correctly configured
    return (is_perforator, interface_id)


def get_output_settings(interface_id):
    """get_interface_output_settings:

    Reads a configuration file and gets interface output parameters.
    Used for perforators as well as casters.
    """
    interface_name = 'Interface' + str(interface_id)
    # Set up MCP23017 interface parameters
    mcp0_address = get_config(interface_name, 'mcp0_address')
    mcp1_address = get_config(interface_name, 'mcp1_address')
    pin_base = get_config(interface_name, 'pin_base')
    # Check which signals arrangement the interface uses...
    signals_arr = get_config(interface_name, 'signals_arrangement')
    # ...and get the signals order for it:
    signals_arrangement = get_config('SignalsArrangements', signals_arr)
    signals_arrangement = str(signals_arrangement).upper()
    # Interface configured successfully - return a tuple with parameters
    return (int(mcp0_address), int(mcp1_address),
            pin_base, signals_arrangement)


def get_input_settings(interface_id):
    """get_input_settings:

    Reads settings for inputs (emergency stop and machine cycle sensor)
    from the conffile. Used for casters only.
    """
    interface_name = 'Interface' + str(interface_id)
    # Emergency stop and sensor are valid only for casters,
    # perforators do not have them
    emergency_stop_gpio = get_config(interface_name, 'emergency_stop_gpio')
    sensor_gpio = get_config(interface_name, 'sensor_gpio')
    return (emergency_stop_gpio, sensor_gpio)


def section_not_found(section_name):
    """section_not_found:

    Indicates whether there's no section with a given name."""
    cfg = initialize_config()
    return not cfg.has_section(section_name)
