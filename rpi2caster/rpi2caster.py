# -*- coding: utf-8 -*-
"""
    rpi2caster is a CAT (computer-aided typesetting) software
    for the Monotype composition caster (a hot-metal typesetting machine).

    This project uses a control interface for 31/32 solenoid valves
    and a machine cycle sensor. It can control a casting machine
    or a pneumatic paper tape perforator from the Monotype keyboard.

    The rpi2caster package consists of three main utilities:
        * machine control,
        * typesetting,
        * inventory management.

    Machine control utility also serves as a diagnostic program
    for calibrating and testing the machine and control interface.

    For usage info, run `rpi2caster --help`

"""
import configparser as cp
from contextlib import suppress
from functools import wraps
import json
from os import system

import click
import peewee as pw
from playhouse import db_url

from . import datatypes as dt, definitions as d, drivers
from .ui import ClickUI, Abort, Finish, option

# global package-wide declarations
__version__ = '0.7.dev1'
__author__ = 'Krzysztof Słychań'


# Paths: user's local settings and data directory, user's config file...
USER_DATA_DIR = click.get_app_dir('rpi2caster', force_posix=True, roaming=True)
USER_CFG_PATH = '{}/rpi2caster.conf'.format(USER_DATA_DIR)
# database URL (sqlite, mysql, postgres etc.)
USER_DB_URL = 'sqlite:///{}/rpi2caster.db'.format(USER_DATA_DIR)


class StaticConfig(cp.ConfigParser):
    """Configuration manager based on ConfigParser"""
    # use custom names for on and off states
    BOOLEAN_STATES = {name: True for name in dt.TRUE_ALIASES}
    BOOLEAN_STATES.update({name: False for name in dt.FALSE_ALIASES})

    def __init__(self, config_path=USER_CFG_PATH):
        super().__init__()
        self.load(config_path)

    def load(self, config_path):
        """Loads a config file"""
        self.read([*d.GLOBAL_CFG_PATHS, config_path])

    def reset(self):
        """Resets the config to default values"""
        # Populate data with defaults; convert all names to lowercase
        self.read_dict(d.DEFAULTS, 'defaults')

    def save(self, file=None):
        """Save the configuration to file"""
        if not file:
            return
        self.write(file)

    def get_option(self, option_name='', default=None,
                   minimum=None, maximum=None):
        """Get an option value."""

        # get the first match for this option name or its aliases
        matching_options = self.matching_options_generator(option_name)
        value = next(matching_options)

        # take a default value argument into account, if it was specified
        default_value = default or d.DEFAULTS.get(option_name)

        # coerce the string into the default value datatype, validate limits
        return dt.convert_and_validate(value, default_value,
                                       minimum=minimum, maximum=maximum)

    def get_many(self, **kwargs):
        """Get multiple options by keyword arguments:
            (key1=option1, key2=option2...) -> {key1: option_value_1,
                                                key2: option_value_2...}
        """
        return {key: self.get_option(option) for key, option in kwargs.items()}

    def set_option(self, option_name, value, section_name=None):
        """Set an option to a given value"""
        section, cfg_option = section_name.lower(), option_name.lower()
        if section:
            self.set(section, cfg_option, value)
        else:
            self.set('default', cfg_option, value)

    def to_json(self, include_defaults=False):
        """Dump the config to json"""
        dump = {section: {option: value}
                for section, sect_options in self.items()
                for option, value in sect_options.items()}
        if include_defaults:
            dump['default'] = {option: dt.convert(value, str)
                               for option, value in d.DEFAULTS.items()}
        return json.dumps(dump, indent=4)

    def from_json(self, json_dump):
        """Load the config dump from json"""
        dump = json.loads(json_dump)
        self.read_dict(dump)

    @property
    def interface(self):
        """Return the interface configuration"""
        data = self.get_many(sensor='sensor', output='output',
                             simulation='simulation', punching='punching',
                             parallel='parallel', sensor_gpio='sensor_gpio',
                             emergency_stop_gpio='emergency_stop_gpio',
                             signals_arrangement='signals',
                             mcp0='mcp0', mcp1='mcp1', pin_base='pin_base',
                             i2c_bus='i2c_bus', bounce_time='bounce_time')
        return d.Interface(**data)

    @property
    def preferences(self):
        """Return the typesetting preferences configuration"""
        data = self.get_many(default_measure='default_measure',
                             measurement_unit='measurement_unit')
        return d.Preferences(**data)

    def matching_options_generator(self, option_name):
        """Look for an option in ConfigParser object, including aliases,
        if the option is not found in any section, get a default value."""
        for section in self.sections():
            # get all possible names for the desired option
            option_names = [option_name, *d.ALIASES.get(option_name, ())]
            for name in option_names:
                try:
                    candidate = self[section][name]
                    yield candidate
                except (cp.NoSectionError, cp.NoOptionError, KeyError):
                    continue
        # option was defined nowhere => use a default one
        # or raise NoOptionError if it fails
        yield d.DEFAULTS.get(option_name)


class RuntimeConfig:
    """runtime config for rpi2caster"""
    _simulation, punching = False, False
    interface = None

    def __init__(self, punching=False, simulation=False, measure=None,
                 diecase_id=None, wedge_name=None, ribbon=None):
        self.punching = punching
        self.diecase_id = diecase_id
        self.wedge_name = wedge_name
        self.measure = measure
        self.ribbon = ribbon
        # simulation mode from configuration
        self.simulation = simulation or CFG.interface.simulation

    def toggle_punching(self):
        """Switch between punching and casting modes"""
        self.punching = not self.punching

    def toggle_simulation(self):
        """Switch between simulation and casting/punching modes"""
        self.simulation = not self.simulation

    def hardware_setup(self):
        """Configure the hardware interface"""
        try:
            # special interfaces go here
            if CFG.interface.parallel:
                # Symbiosys parallel port driver
                self.interface = drivers.make_parallel_interface()
                self._simulation = False
                return
            else:
                # put an interface together from sensor and driver
                sensor = CFG.interface.sensor
                output = CFG.interface.output
                self.interface = drivers.make_interface(sensor, output)
                self._simulation = False
        except drivers.ConfigurationError as exc:
            # cannot initialize hardware interface: explain why,
            # offer to simulate casting instead
            UI.display(str(exc))
            UI.pause('Hardware interface unavailable. Using simulation mode.')
            self.simulation = True

    @property
    def simulation(self):
        """check whether the software runs in simulation mode"""
        return self._simulation

    @simulation.setter
    def simulation(self, status):
        """choose simulation interface if True, else hardware interface"""
        if status:
            # simulation mode ON
            self._simulation = True
            self.interface = drivers.make_simulation_interface()
        else:
            self._simulation = False
            self.hardware_setup()


class DBProxy(pw.Proxy):
    """Database object sitting on top of Peewee"""
    def __init__(self, url=USER_DB_URL):
        super().__init__()
        self.load(url)

    def __call__(self, routine):
        @wraps(routine)
        def wrapper(*args, **kwargs):
            """decorator for routines needing database connection"""
            with self:
                retval = routine(*args, **kwargs)
            return retval

        return wrapper

    def __enter__(self):
        """context manager for routines needing database connection"""
        with suppress(pw.OperationalError):
            self.connect()
        return self

    def __exit__(self, *_):
        with suppress(pw.OperationalError):
            self.close()

    def load(self, url):
        """New database session"""
        base = db_url.connect(url)
        self.initialize(base)


class UIProxy(object):
    """UI abstraction layer"""
    impl = ClickUI()
    implementations = {'text_ui': ClickUI,
                       'click': ClickUI}

    def __init__(self, impl='click', verbosity=0):
        self.load(impl, verbosity)

    def __getattr__(self, name):
        result = getattr(self.impl, name)
        if result is None:
            raise NameError('{implementation} has no function named {function}'
                            .format(implementation=self.impl.__name__,
                                    function=name))
        else:
            return result

    def get_name(self):
        """Get the underlying user interface implementation's name."""
        return self.impl.__name__

    def load(self, implementation, verbosity):
        """Load another user interface implementation"""
        impl = self.implementations.get(implementation, ClickUI)
        self.impl = impl(verbosity)


DB, CFG, UI = DBProxy(), StaticConfig(), UIProxy()
pass_runtime_config = click.make_pass_decorator(RuntimeConfig, ensure=True)


@click.group(invoke_without_command=True)
@click.option('--verbosity', '-v', count=True, default=0,
              help='verbose mode')
@click.option('--conffile', '-c', default=USER_CFG_PATH, show_default=True,
              help='config file to use')
@click.option('--database', '-d', default=USER_DB_URL, show_default=True,
              metavar='URL', help='database URL to use')
@click.option('--web', '-W', 'ui_impl', flag_value='web_ui',
              help='use web user interface (not implemented)')
@click.option('--text', '-T', 'ui_impl', flag_value='text_ui',
              default=True, help='use text user interface')
@click.option('--diecase', '-m', metavar='diecase ID',
              help='diecase ID from the database to use')
@click.option('--wedge', '-w', metavar='[S]X...-Y[E]', help='wedge to use')
@click.option('--measure', '-M', metavar='value, unit',
              help='line length to use')
@click.version_option(__version__)
@click.pass_context
def cli(ctx, conffile, database, verbosity, ui_impl, diecase, wedge, measure):
    """command-line interface for rpi2caster"""
    # update the database and configuration parameters
    CFG.load(conffile)
    DB.load(database)
    UI.load(ui_impl, verbosity)
    ctx.obj = RuntimeConfig(diecase_id=diecase, wedge_name=wedge,
                            measure=measure)

    try:
        if not ctx.invoked_subcommand:
            main_menu()
        else:
            return
    except (Abort, Finish, KeyboardInterrupt):
        UI.display('Goodbye!')


@pass_runtime_config
def main_menu(runtime_config):
    """Main menu for rpi2caster"""
    # main menu - choose the module
    header = ('rpi2caster - computer aided type casting for Monotype '
              'composition / type & rule casters.'
              '\n\nMain menu:\n')
    options = [option(key='c', value=cast, seq=20,
                      cond=lambda: not runtime_config.punching,
                      text='Casting...',
                      desc=('Cast composition, sorts, typecases or spaces;'
                            ' test the machine')),
               option(key='c', value=runtime_config.toggle_punching, seq=70,
                      cond=lambda: runtime_config.punching,
                      text='Switch to casting mode',
                      desc='Switch from punching to casting'),

               option(key='d', value=inventory, seq=30,
                      text='Diecase manipulation...',
                      desc='Manage the matrix case collection'),

               option(key='p', value=cast, seq=20,
                      cond=lambda: runtime_config.punching,
                      text='Punching...',
                      desc='Punch a ribbon with a keyboard\'s perforator'),
               option(key='p', value=runtime_config.toggle_punching, seq=70,
                      cond=lambda: not runtime_config.punching,
                      text='Switch to perforation mode',
                      desc='Switch from casting to ribbon punching'),

               option(key='s', value=runtime_config.toggle_simulation, seq=80,
                      cond=lambda: not runtime_config.simulation,
                      text='Switch to simulation mode',
                      desc='Test casting without the caster or interface'),
               option(key='s', value=runtime_config.toggle_simulation, seq=80,
                      cond=lambda: runtime_config.simulation,
                      text='Switch to machine control mode',
                      desc='Use a real Monotype caster or perforator'),

               option(key='t', value=translate, seq=10,
                      text='Typesetting...',
                      desc='Compose text for casting'),

               option(key='u', value=update,
                      text='Update the program', seq=90)]

    UI.dynamic_menu(options, header, allow_abort=True)


@cli.command()
@click.option('--testing', '-T', is_flag=True, flag_value=True,
              help='caster testing / diagnostics')
@click.option('--material', '-h', is_flag=True, flag_value=True,
              help='cast material for manual typesetting')
@click.option('--punch', '-p', is_flag=True, flag_value=True,
              help='ribbon perforation instead of casting')
@click.option('--simulate', '-s', is_flag=True, flag_value=True,
              show_default=True, help='simulation mode - no actual casting')
@click.argument('ribbon', required=False, type=click.File('r'))
@pass_runtime_config
def cast(runtime_config, punch, simulate, testing, material, ribbon):
    """Casting on an actual caster or simulation"""
    from .core import Casting
    runtime_config.punching, runtime_config.simulation = punch, simulate
    runtime_config.ribbon = ribbon
    _casting = Casting(runtime_config)
    if material:
        _casting.cast_material()
    elif ribbon:
        # cast ribbon directly - no need to go through the menu
        _casting.cast_composition()
    elif testing:
        _casting.caster.diagnostics()
    else:
        _casting.main_menu()


@cli.command()
@click.option('--src', type=click.File('r'))
@click.option('--out', type=click.File('w+', atomic=True))
@pass_runtime_config
def translate(runtime_config, src, out):
    """Text to ribbon translation and justification"""
    from .core import Typesetting
    typesetting = Typesetting()
    typesetting.diecase_id = runtime_config.diecase_id
    typesetting.wedge_name = runtime_config.wedge_name
    typesetting.text_file = src
    typesetting.ribbon_file = out
    # Only one method here
    typesetting.main_menu()


@cli.command()
@click.option('--testing', '-t', is_flag=True, flag_value=True,
              help='use a unstable/development version instead of stable')
def update(testing):
    """Updates the software"""
    # Upgrade routine
    dev_prompt = 'Testing version (newest features, but unstable)? '
    if UI.confirm('Update the software?', default=False):
        use_dev_version = testing or UI.confirm(dev_prompt, default=False)
        pre = '--pre' if use_dev_version else ''
        system('pip3 install {} --upgrade rpi2caster'.format(pre))


@cli.command()
@click.option('--list-diecases', '-l', is_flag=True, flag_value=True,
              help='list diecases stored in database and quit')
def inventory(args):
    """Inventory management - diecase manipulation etc."""
    from . import matrix_controller
    from .core import InventoryManagement
    if args.list_diecases:
        # Just show what we have
        matrix_controller.list_diecases()
    else:
        # edit diecase (or choose, if failed)
        InventoryManagement(args.diecase_id)


@cli.command()
def meow():
    "Easter egg"
    try:
        from .data import EASTER_EGG
        UI.display('\nOh, this was meowsome.\n')
        UI.display(EASTER_EGG)
    except (OSError, ImportError, FileNotFoundError):
        print('There are no Easter Eggs in this program.')


if __name__ == '__main__':
    cli()
