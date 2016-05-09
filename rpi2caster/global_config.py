# -*- coding: utf-8 -*-
"""Global settings for rpi2caster. Acts as a single point of truth (SPOT)
for every application-wide setting."""
import io
import configparser
from click import get_app_dir
from . import text_ui as UI
from .constants import TRUE_ALIASES, FALSE_ALIASES, SIGNALS


def get_config(section_name, option_name, default_value, datatype=str):
    """get_config:

    Gets a value for a given parameter from a given name.
    Returns:
      -int - if the value is numeric,
      -boolean - if the value was in one of the true or false aliases,
      -string otherwise,
      -None if there is no option or section of that name.
    """
    # Search user and global config paths
    for path in CONFIG_PATHS:
        try:
            with io.open(path, 'r'):
                cfg = configparser.ConfigParser()
                cfg.read(path)
                option_value = str(cfg.get(section_name, option_name))
                # Go further to processing
                break
        except (IOError, FileNotFoundError,
                configparser.NoSectionError, configparser.NoOptionError):
            # No option found in this config file - tr
            continue
    else:
        # Ran through all config files and found no option
        # In this case, use default...
        return default_value
    # We now have the value - let's convert it to desired datatype
    if datatype == list:
        retval = option_value.split(',')
    elif datatype == int and str(option_value).lower().startswith('0x'):
        # Value is a hexstring: 0x or 0X
        try:
            retval = int(option_value, 16)
        except (ValueError, TypeError):
            # Conversion failed
            retval = default_value
    elif option_value.lower() in ('none', 'null'):
        retval = None
    elif datatype == bool and str(option_value).lower() in TRUE_ALIASES:
        retval = True
    elif datatype == bool and str(option_value).lower() in FALSE_ALIASES:
        retval = False
    else:
        retval = datatype(option_value)
    return retval


# Conffile path
APPDIR = get_app_dir('rpi2caster', force_posix=True, roaming=True)
CONFIG_PATHS = [APPDIR + '/rpi2caster.conf',
                '/etc/rpi2caster/rpi2caster.conf', '/etc/rpi2caster.conf']
# SQLite3 database path
DATABASE_PATHS = [APPDIR + '/rpi2caster.db',
                  '/var/local/rpi2caster/rpi2caster.db',
                  '/var/rpi2caster/rpi2caster.db']
# Line length / galley width default value
DEFAULT_MEASURE = get_config('Preferences', 'default_measure', 25, int)
DEFAULT_UNIT = get_config('Preferences', 'measurement_unit', 'cc')
# Interface settings
# Inputs for the casting interface
SIGNALS_ARRANGEMENT = get_config('Interface', 'signals', SIGNALS, list)
EMERGENCY_STOP_GPIO = get_config('Interface', 'stop_gpio', 22, int)
SENSOR_GPIO = get_config('Interface', 'sensor_gpio', 17, int)
# Default hardware interface output data
MCP0 = get_config('Interface', 'MCP0', 0x20, int)
MCP1 = get_config('Interface', 'MCP1', 0x21, int)
PIN_BASE = get_config('Interface', 'pin_base', 65, int)
SENSOR = get_config('Interface', 'sensor', 'simulation')
OUTPUT = get_config('Interface', 'output', 'simulation')
BACKEND_SELECT = get_config('Preferences', 'choose_backend', False, bool)
