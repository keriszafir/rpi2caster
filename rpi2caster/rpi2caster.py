# -*- coding: utf-8 -*-
"""
    rpi2caster is a CAT (computer-aided typesetting) software
    for the Monotype composition caster (a hot-metal typesetting machine).

    This project uses a control interface for 31/32 solenoid valves
    and a machine cycle sensor. It can control a casting machine
    or a pneumatic paper tape perforator from the Monotype keyboard.

    The rpi2caster package consists of three main utilities:

        * casting (composition, material etc.),

        * caster/interface testing and diagnostics,

        * typesetting (not ready yet),

        * diecase and layout management.

    Machine control utility also serves as a diagnostic program
    for calibrating and testing the machine and control interface.

"""
from collections import OrderedDict
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


class CommandGroup(click.Group):
    """Click group which allows using abbreviated commands,
    and arranges them in the order they were defined."""
    def __init__(self, name=None, commands=None, **attrs):
        if commands is None:
            commands = OrderedDict()
        elif not isinstance(commands, OrderedDict):
            commands = OrderedDict(commands)
        click.Group.__init__(self, name=name, commands=commands, **attrs)

    def list_commands(self, ctx):
        """List command names as they are in commands dict."""
        return self.commands.keys()

    def get_command(self, ctx, cmd_name):
        retval = click.Group.get_command(self, ctx, cmd_name)
        if retval is not None:
            return retval
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))


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
        except drivers.HWConfigError as exc:
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
    def simulation(self, is_on):
        """choose simulation interface if True, else hardware interface"""
        if is_on:
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


@click.group(invoke_without_command=True, cls=CommandGroup, help=__doc__,
             context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(__version__)
@click.option('--verbosity', '-v', count=True, default=0,
              help='verbose mode')
@click.option('--conffile', '-c', default=USER_CFG_PATH,
              help='config file to use')
@click.option('--database', '-d', default=USER_DB_URL,
              metavar='[database URL]', help='database URL to use')
@click.option('--web', '-W', 'ui_impl', flag_value='web_ui',
              help='use web user interface (not implemented)')
@click.option('--text', '-T', 'ui_impl', flag_value='text_ui',
              default=True, help='use text user interface')
@click.pass_context
def cli(ctx, conffile, database, ui_impl, verbosity):
    """decide whether to go to a subcommand or enter main menu"""
    def wrapped(function):
        """wrap a function so that the context will invoke it"""
        return lambda: ctx.invoke(function)

    runtime_config = RuntimeConfig()
    CFG.load(conffile)
    DB.load(database)
    UI.load(ui_impl, verbosity)
    ctx.obj = runtime_config

    # main menu
    header = ('rpi2caster - computer aided type casting for Monotype '
              'composition / type & rule casters.'
              '\n\nMain menu:\n')
    options = [option(key='t', value=wrapped(translate), seq=10,
                      text='Typesetting...',
                      desc='Compose text for casting'),

               option(key='c', value=wrapped(cast), seq=20,
                      text='Casting...',
                      desc=('Cast composition, sorts, typecases or spaces;'
                            ' test the machine')),

               option(key='p', value=wrapped(punch_ribbon), seq=20,
                      text='Punching...',
                      desc='Punch a ribbon with a keyboard\'s perforator'),

               option(key='d', value=wrapped(inventory), seq=30,
                      text='Diecase manipulation...',
                      desc='Manage the matrix case collection'),

               option(key='s', value=runtime_config.toggle_simulation, seq=80,
                      cond=lambda: not runtime_config.simulation,
                      text='Switch to simulation mode',
                      desc='Test casting without the caster or interface'),
               option(key='s', value=runtime_config.toggle_simulation, seq=80,
                      cond=lambda: runtime_config.simulation,
                      text='Switch to machine control mode',
                      desc='Use a real Monotype caster or perforator'),

               option(key='u', value=wrapped(update),
                      text='Update the program', seq=90)]

    if not ctx.invoked_subcommand:
        UI.dynamic_menu(options, header, allow_abort=True,
                        catch_exceptions=(Abort, Finish, click.Abort))


@cli.group(invoke_without_command=True, cls=CommandGroup)
@click.option('--simulate', '-s', is_flag=True, flag_value=True,
              default=CFG.interface.simulation, show_default=True,
              help='simulate machine control')
@click.option('--diecase', '-m', metavar='[diecase ID]',
              help='diecase ID from the database to use')
@click.option('--wedge', '-w', metavar='e.g. S5-12E',
              help='series, set width, E for European wedges')
@click.option('--measure', '-l', metavar='[value+unit]',
              help='line length to use')
@click.pass_context
def cast(ctx, simulate, diecase, wedge, measure):
    """Cast type with a Monotype caster.

    Casts composition, material for handsetting, QR codes.
    Can also cast a diecase proof.

    Can also be run in simulation mode without the actual caster."""
    from .core import Casting
    # context object stores parameters passed in top-level command...
    runtime_config = ctx.obj
    # allow override if we call this from menu
    runtime_config.simulation = runtime_config.simulation or simulate
    casting = Casting(runtime_config)
    casting.measure = measure
    casting.diecase_id = diecase
    casting.wedge_name = wedge
    # replace the context object for the subcommands to see
    ctx.obj = casting
    if not ctx.invoked_subcommand:
        casting.main_menu()


@cast.command('ribbon')
@click.argument('ribbon', metavar='[FILENAME / RIBBON_ID]')
@click.pass_obj
def cast_ribbon(casting, ribbon):
    """Cast composition from file or database."""
    casting.ribbon_by_name(ribbon)
    casting.cast_composition()


@cast.command('material')
@click.pass_obj
def cast_handsetting_material(casting):
    """Cast founts, sorts and spaces/quads."""
    casting.cast_material()


@cast.command('qrcode')
@click.pass_obj
def cast_qr_code(casting):
    """Generate and cast QR codes."""
    casting.cast_qr_code()


@cast.command('proof')
@click.pass_obj
def cast_diecase_proof(casting):
    """Cast a matrix case proof."""
    casting.diecase_proof()


@cli.group(invoke_without_command=True, cls=CommandGroup, name='punch')
@click.option('--simulate', '-s', is_flag=True, flag_value=True,
              default=CFG.interface.simulation, show_default=True,
              help='simulate machine control')
@click.option('--diecase', '-m', metavar='[diecase ID]',
              help='diecase ID from the database to use')
@click.option('--wedge', '-w', metavar='e.g. S5-12E',
              help='series, set width, E for European wedges')
@click.option('--measure', '-l', metavar='[value+unit]',
              help='line length to use')
@click.pass_context
def punch_ribbon(ctx, simulate, diecase, wedge, measure):
    """Punch the paper ribbon with a perforator.

    Punches composition, material for handsetting or QR codes.

    Can also be run in simulation mode without the actual interface."""
    from .core import Casting
    # context object stores parameters passed in top-level command...
    runtime_config = ctx.obj
    runtime_config.punching = True
    # allow override if we call this from menu
    runtime_config.simulation = runtime_config.simulation or simulate
    casting = Casting(runtime_config)
    casting.measure = measure
    casting.diecase_id = diecase
    casting.wedge_name = wedge
    # replace the context object for the subcommands to see
    ctx.obj = casting
    if not ctx.invoked_subcommand:
        casting.main_menu()


punch_ribbon.add_command(cast_ribbon, 'ribbon')
punch_ribbon.add_command(cast_qr_code, 'qrcode')
punch_ribbon.add_command(cast_handsetting_material, 'material')


@cli.command('test')
@click.option('--punch', '-p', is_flag=True, flag_value=True,
              help='test the interface in punching mode')
@click.option('--simulate', '-s', is_flag=True, flag_value=True,
              default=CFG.interface.simulation, show_default=True,
              help='simulate machine control')
@click.pass_obj
def test_machine(runtime_config, simulate, punch):
    """Monotype caster testing and diagnostics."""
    from .monotype import MonotypeCaster
    runtime_config.punching = punch
    runtime_config.simulation = simulate
    machine = MonotypeCaster(runtime_config)
    machine.diagnostics()


@cli.command()
@click.option('--src', type=click.File('r'))
@click.option('--out', type=click.File('w+', atomic=True))
@click.option('--diecase', '-m', metavar='[diecase ID]',
              help='diecase ID from the database to use')
@click.option('--wedge', '-w', metavar='e.g. S5-12E',
              help='series, set width, E for European wedges')
@click.option('--measure', '-l', metavar='[value+unit]',
              help='line length to use')
@click.option('--align', '-a', metavar='[ALIGNMENT]', default='left',
              help='default text alignment')
@click.option('--manual', '-M', is_flag=True, flag_value=True,
              help='leave end-of-line decisions to the operator')
def translate(src, out, align, manual, **kwargs):
    """Translate text to a sequence of Monotype codes.

    Set and justify a text with control codes.

    The output is a sequence of codes which can control the
    Monotype composition caster.

    These codes are specific to a diecase and wedge used."""
    from .core import Typesetting
    typesetting = Typesetting()
    typesetting.measure = kwargs.get('measure')
    typesetting.diecase_id = kwargs.get('diecase')
    typesetting.wedge_name = kwargs.get('wedge')
    typesetting.manual_mode = manual
    typesetting.default_alignment = align
    typesetting.text_file = src
    typesetting.ribbon.file = out
    # Only one method here
    typesetting.main_menu()


@cli.group(invoke_without_command=True, cls=CommandGroup)
@click.pass_context
def inventory(ctx):
    """Diecase definition and layout management."""
    if not ctx.invoked_subcommand:
        ctx.invoke(edit_diecase)


@inventory.command('edit')
@click.argument('diecase', required=False, default=None)
def edit_diecase(diecase):
    """Load and edit a matrix case."""
    from . import matrix_controller as mc
    editor = mc.DiecaseMixin()
    editor.diecase_id = diecase
    editor.diecase_manipulation()


@inventory.command('list')
def list_diecases():
    """List all available diecases and exit."""
    from . import matrix_controller as mc
    mc.list_diecases()


@cli.command()
@click.option('--testing', '-t', is_flag=True, flag_value=True,
              help='use a unstable/development version instead of stable')
def update(testing):
    """Update the software."""
    # Upgrade routine
    dev_prompt = 'Testing version (newest features, but unstable)? '
    if UI.confirm('Update the software?', default=False):
        use_dev_version = testing or UI.confirm(dev_prompt, default=False)
        pre = '--pre' if use_dev_version else ''
        system('pip3 install {} --upgrade rpi2caster'.format(pre))


@cli.command()
def meow():
    "Easter egg."
    try:
        from .data import EASTER_EGG
        UI.display('\nOh, this was meowsome.\n')
        UI.display(EASTER_EGG)
    except (OSError, ImportError, FileNotFoundError):
        print('There are no Easter Eggs in this program.')
