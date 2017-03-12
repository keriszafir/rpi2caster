# -*- coding: utf-8 -*-
"""default settings for rpi2caster"""
from click import get_app_dir
from .constants import SIGNALS

# Paths
USER_DATA_DIR = get_app_dir('rpi2caster', force_posix=True, roaming=True)
USER_CFG_PATH = '%s/rpi2caster.conf' % USER_DATA_DIR
GLOBAL_CFG_PATHS = ['/etc/rpi2caster/rpi2caster.conf', '/etc/rpi2caster.conf']
USER_DB_PATH = '%s/rpi2caster.db' % USER_DATA_DIR
# Options and their default values
OPTIONS = {}
OPTIONS['preferences'] = {'default_measure': '25',
                          'measurement_unit': 'cc',
                          'choose_backend': False}
OPTIONS['interface'] = {'signals_arrangement': SIGNALS,
                        'emergency_stop_gpio': 22,
                        'sensor_gpio': 17,
                        'input_bounce_time': 25,
                        'MCP0': 0x20,
                        'MCP1': 0x21,
                        'pin_base': 65,
                        'sensor': 'simulation',
                        'output': 'simulation'}
OPTIONS['database'] = {'url': 'sqlite:///%s' % USER_DB_PATH}
# Option aliases - alternate names for options in files
ALIASES = [['signals_arrangement', 'signals', 'arrangement'],
           ['choose_backend', 'backend_select'],
           ['default_measure', 'line_length', 'default_line_length'],
           ['measurement_unit', 'typesetting_unit', 'unit', 'pica'],
           ['sensor_gpio', 'photocell_gpio', 'light_switch_gpio'],
           ['emergency_stop_gpio', 'stop_gpio', 'stop_button_gpio'],
           ['path', 'db_path', 'database_path']]
