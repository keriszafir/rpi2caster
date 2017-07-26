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
from functools import partial
import os
import click
import librpi2caster

from . import data, global_state
from .ui import Abort, Finish, option

# get singleton instances for user interface, database and configuration
USER_DATA_DIR = global_state.USER_DATA_DIR
UI = global_state.UI
DB = global_state.DB
CFG = global_state.CFG


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
        """Try to get a command with given partial name;
        in case of multiple match, abort."""
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


def find_casters(operation_mode=None):
    """Finds casters and returns dictionary of number-caster values"""
    from .monotype import MonotypeCaster, SimulationCaster

    def make_caster(url):
        """caster factory method: make a real or simulation caster;
        if something bad happens, just return None"""
        try:
            return MonotypeCaster(url, operation_mode)
        except (librpi2caster.CommunicationError,
                librpi2caster.UnsupportedMode):
            return None

    # get the interface URLs
    # the first interface is a simulation interface numbered 0
    config_urls = CFG['System']['interfaces']
    caster_urls = [*(x.strip() for x in config_urls.split(','))]
    # make a dictionary of casters starting with 0 for a simulation caster
    casters = {0: (SimulationCaster(), 'No URL')}
    for number, url in enumerate(caster_urls, start=1):
        caster = make_caster(url)
        casters[number] = (caster, url)
    return casters


@click.group(invoke_without_command=True, cls=CommandGroup, help=__doc__,
             context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(None, '--version', '-v')
@click.option('verbosity', '-V', count=True, default=0,
              help='verbose mode (count, default=0)')
@click.option('--conffile', '-c', help='config file to use', metavar='[PATH]',
              default=os.path.join(USER_DATA_DIR, 'rpi2caster.conf'))
@click.option('--database', '-d', metavar='[URL]', help='database URL to use')
@click.option('--web', '-W', 'ui_impl', flag_value='web_ui',
              help='use web user interface (not implemented)')
@click.option('--text', '-T', 'ui_impl', flag_value='text_ui',
              default=True, help='use text user interface')
@click.pass_context
def cli(ctx, conffile, database, ui_impl, verbosity):
    """decide whether to go to a subcommand or enter main menu"""
    def options():
        """Dynamically generate options"""
        ret = [option(key='t', value=partial(ctx.invoke, translate), seq=10,
                      text='Typesetting...',
                      desc='Compose text for casting'),

               option(key='c', value=partial(ctx.invoke, cast), seq=20,
                      text='Casting or punching...',
                      desc=('Cast composition, sorts, typecases or spaces;'
                            ' test the machine')),

               option(key='d', value=partial(ctx.invoke, inventory), seq=30,
                      text='Diecase manipulation...',
                      desc='Manage the matrix case collection'),

               option(key='u', value=partial(ctx.invoke, update),
                      text='Update the program', seq=90)]
        return ret

    CFG.read(conffile)
    # get the URL from the argv or updated config
    database_url = database or CFG['System']['database']
    DB.load(database_url)
    UI.load(ui_impl, verbosity)
    # main menu
    header = ('rpi2caster - computer aided typesetting software '
              'for Monotype composition casters.'
              '\n\nMain menu:\n')
    exceptions = (Abort, Finish, click.Abort)
    if not ctx.invoked_subcommand:
        UI.dynamic_menu(options, header, allow_abort=True,
                        catch_exceptions=exceptions)


@cli.command('machines', options_metavar='[-h]')
@click.option('--punching', '-p', 'operation_mode', flag_value='punching',
              help='punch ribbon with a perforator (if supported)')
@click.option('--casting', '-c', 'operation_mode', flag_value='casting',
              help='cast type on a composition caster (if supported)')
def list_casters(operation_mode):
    """List all configured casters and show the available ones."""
    data = find_casters(operation_mode)
    unavailable = click.style('currently unavailable', fg='red')
    UI.display('\nList of configured interfaces:\n')
    for number, (caster, url) in data.items():
        name = caster if caster else unavailable
        caster_url = '[{}]'.format(url)
        UI.display('{:^4}{:<50}: {}'.format(number, caster_url, name))


@cli.group(invoke_without_command=True, cls=CommandGroup,
           options_metavar='[-hlmsw]', subcommand_metavar='[what] [-h]')
@click.option('--interface', '-i', default=None, type=int, metavar='[number]',
              help='choose interface:\n0=simulation, 1,2...=hardware')
@click.option('--punching', '-p', 'operation_mode', flag_value='punching',
              help='punch ribbon with a perforator (if supported)')
@click.option('--casting', '-c', 'operation_mode', flag_value='casting',
              help='cast type on a composition caster (if supported)')
@click.option('--diecase', '-m', metavar='[diecase ID]',
              help='diecase ID from the database to use')
@click.option('--wedge', '-w', metavar='e.g. S5-12E',
              help='series, set width, E for European wedges')
@click.option('--measure', '-l', metavar='[value+unit]',
              help='line length to use')
@click.pass_context
def cast(ctx, interface, operation_mode, diecase, wedge, measure):
    """Cast type with a Monotype caster.

    Casts composition, material for handsetting, QR codes.
    Can also cast a diecase proof.

    Can also be run in simulation mode without the actual caster."""
    from .core import Casting
    # allow override if we call this from menu
    casting = Casting(interface, operation_mode)
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
    try:
        casting.ribbon_by_name(ribbon)
        casting.cast_composition()
    except FileNotFoundError:
        UI.display('File {} not found.'.format(ribbon))


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


@cast.command('test', options_metavar='[-hps]')
@click.pass_obj
def test_machine(casting):
    """Monotype caster testing and diagnostics."""
    casting.machine.diagnostics_menu()


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


@inventory.command('diecases', options_metavar='[-h]')
def list_diecases():
    """List all available diecases and exit."""
    from . import views, matrix_controller as mc
    views.list_diecases(mc.get_all_diecases())


@inventory.command('wedges', options_metavar='[-h]')
def list_wedges():
    """List all known wedge definitions, and exit."""
    from . import views
    views.list_wedges()


@inventory.command('typefaces', options_metavar='[-h]')
def list_typefaces():
    """List all known typefaces and exit."""
    from . import views
    views.list_typefaces()


@inventory.command('uas', options_metavar='[-h]')
def list_uas():
    """List all known unit arrangements and exit."""
    from . import views
    views.list_unit_arrangements()


@inventory.command('layout', options_metavar='[-h]')
@click.argument('diecase', required=False, default=None,
                metavar='[diecase_id]')
def display_layout(diecase):
    """Display a diecase layout.

    If diecase_id is not specified, choose a diecase from the database."""
    from . import views, matrix_controller as mc
    case = mc.get_diecase(diecase)
    views.display_layout(case.layout)


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
        UI.display('\nOh, this was meowsome.\n')
        UI.display(data.EASTER_EGG)
    except (OSError, ImportError, FileNotFoundError):
        print('There are no Easter Eggs in this program.')
