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
from configparser import ConfigParser
from contextlib import suppress
from functools import wraps
import os

import click
import peewee as pw
from playhouse import db_url

from .ui import ClickUI, Abort, Finish, option

# global package-wide declarations
__version__ = '0.7.dev1'
__author__ = 'Krzysztof Słychań'

# Find the data directory path
USER_DATA_DIR = click.get_app_dir('rpi2caster', force_posix=True, roaming=True)

# Default values for options
CONFIG = {'System': {'database': ('sqlite:///{}/rpi2caster.db'
                                  .format(USER_DATA_DIR)),
                     'interfaces': ('http://monotype:23017/interfaces/0, '
                                    'http://localhost:23017/interfaces/0')},
          'Typesetting': dict(default_measure='25cc', measurement_unit='cc')}


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


class DBProxy(pw.Proxy):
    """Database object sitting on top of Peewee"""
    def __init__(self, url=''):
        super().__init__()
        if url:
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
        try:
            base = db_url.connect(url)
            self.initialize(base)
        except RuntimeError:
            click.echo('Failed loading database at {}'.format(url))


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


# initialize the user interface, configuration and database
# these will be reconfigured as needed
UI = UIProxy()
CFG = ConfigParser()
CFG.read_dict(CONFIG)
DB = DBProxy(CFG['System'].get('database'))


@click.group(invoke_without_command=True, cls=CommandGroup, help=__doc__,
             context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(__version__)
@click.option('--verbosity', '-v', count=True, default=0,
              help='verbose mode')
@click.option('--conffile', '-c', help='config file to use',
              default=os.path.join(USER_DATA_DIR, 'rpi2caster.conf'))
@click.option('--database', '-d', metavar='[database URL]', default='',
              help='database URL to use')
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

    CFG.read(conffile)
    database_url = database or CFG['System'].get('database')
    CFG.add_section('Runtime')
    runtime_config = CFG['Runtime']
    runtime_config['conffile'] = conffile
    runtime_config['database'] = database_url
    runtime_config['ui_implementation'] = ui_impl
    DB.load(database_url)
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
                      text='Casting or punching...',
                      desc=('Cast composition, sorts, typecases or spaces;'
                            ' test the machine')),

               option(key='d', value=wrapped(inventory), seq=30,
                      text='Diecase manipulation...',
                      desc='Manage the matrix case collection'),

               option(key='u', value=wrapped(update),
                      text='Update the program', seq=90)]

    exceptions = (Abort, Finish, click.Abort)
    if not ctx.invoked_subcommand:
        UI.dynamic_menu(options, header, allow_abort=True,
                        catch_exceptions=exceptions)


@cli.group(invoke_without_command=True, cls=CommandGroup,
           options_metavar='[-hlmsw]', subcommand_metavar='[what] [-h]')
@click.option('--interface', '-i', default=1, metavar='[number]',
              help='choose interface:\n0=simulation, 1,2...=hardware')
@click.option('--punch', '-p', is_flag=True, flag_value=True,
              help='punch ribbon instead of casting type')
@click.option('--diecase', '-m', metavar='[diecase ID]',
              help='diecase ID from the database to use')
@click.option('--wedge', '-w', metavar='e.g. S5-12E',
              help='series, set width, E for European wedges')
@click.option('--measure', '-l', metavar='[value+unit]',
              help='line length to use')
@click.pass_context
def cast(ctx, interface, punch, diecase, wedge, measure):
    """Cast type with a Monotype caster.

    Casts composition, material for handsetting, QR codes.
    Can also cast a diecase proof.

    Can also be run in simulation mode without the actual caster."""
    from .core import Casting
    runtime_config = CFG['Runtime']
    runtime_config['operation_mode'] = 'punching' if punch else 'casting'
    # allow override if we call this from menu
    casting = Casting(interface)
    casting.measure = measure
    casting.diecase_id = diecase
    casting.wedge_name = wedge
    # replace the context object for the subcommands to see
    ctx.obj = casting
    if not ctx.invoked_subcommand:
        casting.main_menu()


@cast.command('ribbon', options_metavar='[-h]')
@click.argument('ribbon', metavar='[filename|ribbon_id]')
@click.pass_obj
def cast_ribbon(casting, ribbon):
    """Cast composition from file or database."""
    casting.ribbon_by_name(ribbon)
    casting.cast_composition()


@cast.command('material', options_metavar='[-h]')
@click.pass_obj
def cast_handsetting_material(casting):
    """Cast founts, sorts and spaces/quads."""
    casting.cast_material()


@cast.command('qrcode', options_metavar='[-h]')
@click.pass_obj
def cast_qr_code(casting):
    """Generate and cast QR codes."""
    casting.cast_qr_code()


@cast.command('proof')
@click.pass_obj
def cast_diecase_proof(casting):
    """Cast a matrix case proof."""
    casting.diecase_proof()


@cli.command('test', options_metavar='[-hps]')
@click.option('--punch', '-p', is_flag=True, flag_value=True,
              help='test the interface in punching mode')
@click.option('--interface', '-i', default=None, show_default=True,
              help='choose interface: 0 = simulation, 1... - real interfaces')
@click.pass_obj
def test_machine(runtime_config, interface, punch):
    """Monotype caster testing and diagnostics."""
    from .monotype import choose_machine
    operation_mode = 'punching' if punch else 'casting'
    machine = choose_machine(interface, operation_mode)
    machine.diagnostics()


@cli.command(options_metavar='[-ahlmMw] [--src textfile] [--out ribbonfile]')
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


@cli.group(invoke_without_command=True, cls=CommandGroup,
           options_metavar='[-h]', subcommand_metavar='[d|e|l] [-h]')
@click.pass_context
def inventory(ctx):
    """Diecase definition and layout management."""
    if not ctx.invoked_subcommand:
        ctx.invoke(edit_diecase)


@inventory.command('edit', options_metavar='[-h]')
@click.argument('diecase', required=False, default=None,
                metavar='[diecase_id]')
def edit_diecase(diecase):
    """Load and edit a matrix case."""
    from . import matrix_controller as mc
    editor = mc.DiecaseMixin()
    editor.diecase_id = diecase
    editor.diecase_manipulation()


@inventory.command('list', options_metavar='[-h]')
def list_diecases():
    """List all available diecases and exit."""
    from . import matrix_controller as mc
    mc.list_diecases()


@inventory.command('display', options_metavar='[-h]')
@click.argument('diecase', required=False, default=None,
                metavar='[diecase_id]')
def display_layout(diecase):
    """Display a diecase layout.

    If diecase_id is not specified, choose a diecase from the database."""
    from . import matrix_controller as mc
    case = mc.get_diecase(diecase)
    mc.display_layout(case.layout)


@cli.group(invoke_without_command=True, cls=CommandGroup,
           options_metavar='[-h]', subcommand_metavar='[d|r] [-h]')
@click.pass_context
def settings(ctx):
    """Display the local and global configuration for rpi2caster."""
    if not ctx.invoked_subcommand:
        ctx.invoke(settings_dump)


@settings.command('dump', options_metavar='[-h]')
@click.argument('output', required=False, type=click.File('w+'),
                default=click.open_file('-', 'w'), metavar='[path]')
def settings_dump(output):
    """Write all settings to a file or stdout.

    Dumps all current configuration settings, both user-specific and global.

    Path can be any file on the local filesystem."""
    CFG.write(output)


@settings.command('read', options_metavar='[-h]')
@click.argument('cfg_option')
def settings_read(cfg_option):
    """Read a specified option from configuration.

    If option is not found, display error message."""
    for section_name in CFG.sections():
        section = CFG[section_name]
        for option_name, option_value in section.items():
            if option_name.lower() == cfg_option.lower():
                click.echo('{}: {}'.format(section_name, option_value))


@cli.command(options_metavar='[-ht]')
@click.option('--testing', '-t', is_flag=True, flag_value=True,
              help='use a unstable/development version instead of stable')
def update(testing):
    """Update the software."""
    # Upgrade routine
    dev_prompt = 'Testing version (newest features, but unstable)? '
    if UI.confirm('Update the software?', default=False):
        use_dev_version = testing or UI.confirm(dev_prompt, default=False)
        pre = '--pre' if use_dev_version else ''
        os.system('pip3 install {} --upgrade rpi2caster'.format(pre))


@cli.command()
def meow():
    "Easter egg."
    try:
        from .data import EASTER_EGG
        UI.display('\nOh, this was meowsome.\n')
        UI.display(EASTER_EGG)
    except (OSError, ImportError, FileNotFoundError):
        print('There are no Easter Eggs in this program.')
