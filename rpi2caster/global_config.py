# -*- coding: utf-8 -*-
"""Global settings for rpi2caster. Acts as a single point of truth (SPOT)
for every application-wide setting."""
import io
import configparser
from . import defaults
from .misc import singleton
from .constants import TRUE_ALIASES, FALSE_ALIASES


@singleton
class Config(object):
    """Configuration manager class"""
    def __init__(self, config_path=''):
        self.data = {}
        self.reset()
        self.load(config_path)

    def reset(self):
        """Resets the config to default values"""
        # Populate data with defaults first... convert all names to lowercase
        self.data = {}
        for section in defaults.OPTIONS:
            section_name = section.lower()
            self.data[section_name] = {}
            for option, value in defaults.OPTIONS[section].items():
                option_name = option.lower()
                self.data[section_name][option_name] = value

    def load(self, path=None):
        """Loads the configuration data from all files."""
        use_path = path or defaults.USER_CFG_PATH
        conffile_paths = defaults.GLOBAL_CFG_PATHS + [use_path]
        # Read configuration files
        file_cfg = configparser.ConfigParser()
        file_cfg.read(conffile_paths)
        # Update the default value with what was found in the conffiles
        # Make sure all options are lowercase
        for section in file_cfg.sections():
            section_name = section.lower()
            # Sageguard against sections present in files but missing
            # in default options
            if self.data.get(section_name) is None:
                self.data[section_name] = {}
            for option_name, option_value in file_cfg[section].items():
                # First look up the option name in aliases
                # Use proper name if alias encountered
                for alias_group in defaults.ALIASES:
                    if option_name in alias_group:
                        option_name = alias_group[0]
                # Determine the default value datatype...
                def_v = defaults.OPTIONS.get(section_name, {}).get(option_name)
                if def_v is None:
                    def_v = ''
                # ...then coerce a parsed value, and store it
                new_value = change_type(option_value, type(def_v))
                self.data[section_name][option_name.lower()] = new_value

    def save(self, path=None):
        """Saves all the stored configuration to specified file"""
        use_path = path or defaults.USER_CFG_PATH
        parser = configparser.ConfigParser()
        data = self.data
        # Output tuples and lists to comma-separated strings
        for section in data:
            for option, value in self.data[section].items():
                if isinstance(value, list) or isinstance(value, tuple):
                    data[section][option] = ','.join(value)
        # Save the file
        parser.read_dict(data)
        with io.open(use_path, 'w+') as conffile:
            parser.write(conffile)

    def set_option(self, name, value, section_name=None):
        """Set the option value in temporarily stored config"""
        option_name = name.lower()
        if section_name:
            self.data[section_name.lower()][option_name] = value
        else:
            for section, options_dict in self.data.items():
                if option_name in options_dict:
                    self.data[section][option_name] = value

    def get_option(self, name, section_name=None):
        """Look for a parameter name in ANY section, return the first match"""
        option_name = name.lower()
        if section_name:
            return self.data.get(section_name.lower()).get(option_name)
        else:
            for section, options_dict in self.data.items():
                if option_name in options_dict:
                    return self.data[section][option_name]
            # Tried everything to no result?
            return None

    def display(self):
        """Display all configured settings"""
        from .rpi2caster import UI
        for section in sorted(self.data):
            UI.display('---%s---' % section.upper())
            for option in sorted(self.data[section]):
                value = self.data[section][option]
                # Separate list/tuple items by commas
                if isinstance(value, list) or isinstance(value, tuple):
                    UI.display('%s: %s' % (option, ','.join(value)))
                else:
                    UI.display('%s: %s' % (option, str(value)))
            # Empty line
            UI.display()


def change_type(option_value, datatype):
    """Changes the value's type:
    -to list: comma-separated strings
    -to int, str, float: use int(), str(), float()
    -can convert hexstrings to int
    -can convert any true / false alias to boolean
    -otherwise leave string."""
    def check_if_none(value):
        """check if option is set to none or null"""
        if value.lower() in ('none', 'null'):
            return True

    def to_list(value):
        """convert comma-separated strings to lists"""
        return value.split(',')

    def to_tuple(value):
        """convert comma-separated strings to tuples"""
        return tuple(value.split(','))

    def to_int(value):
        """convert integer strings or hex strings to integers"""
        try:
            return int(value)
        except ValueError:
            return int(option_value, 16)

    def to_bool(value):
        """convert to boolean"""
        if str(value).lower() in TRUE_ALIASES:
            return True
        elif str(value).lower() in FALSE_ALIASES:
            return False
        else:
            return bool(value)

    # Associate the type with routines
    conv = {list: to_list, int: to_int, bool: to_bool, tuple: to_tuple}
    # First check if this option is set to None
    if check_if_none(option_value):
        return None
    else:
        try:
            # Convert value (will raise TypeError or ValueError if failed)
            return conv[datatype](option_value)
        except KeyError:
            # Try coercing into a desired datatype
            return datatype(option_value)

CFG = Config()
