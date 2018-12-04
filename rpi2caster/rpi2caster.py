# -*- coding: utf-8 -*-
"""
    rpi2caster is a CAT (computer-aided typesetting) software
    for the Monotype composition caster (a hot-metal typesetting machine).

    This project uses a control interface for 31/32 solenoid valves
    and a machine cycle sensor. It can control a casting machine
    or a pneumatic paper tape perforator from the Monotype keyboard.

    The rpi2caster package consists of three main utilities:

        * casting (composition, material etc.),

        * caster/interface testing and diagnostics

    Machine control utility also serves as a diagnostic program
    for calibrating and testing the machine and control interface.

"""
from collections import OrderedDict
from contextlib import suppress
import os

import click

from . import ui

# initialize the configuration for rpi2caster
USER_DATA_DIR = click.get_app_dir('rpi2caster', force_posix=True, roaming=True)
with suppress(FileExistsError):
    os.mkdir(USER_DATA_DIR, mode=0o775)

# pica = .1667, US pica = .166, Didot = .1776, Fournier = .1628
# make it configurable in the future
ui.PICA = 0.1776


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
        return None


@click.group(invoke_without_command=True, cls=CommandGroup, help=__doc__,
             context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(None, '--version', '-V')
@click.option('verbosity', '-v', count=True, default=0,
              help='verbose mode (count, default=0)')
@click.option('--address', '-a', help='address (default: 127.0.0.1)',
              default='127.0.0.1')
@click.option('--port', '-p', help='port (default: 23017)', type=int,
              default=23017)
@click.pass_context
def cli(ctx, verbosity, address, port):
    """decide whether to go to a subcommand or enter main menu"""
    ctx.obj = dict(address=address, port=port)
    ui.verbosity = verbosity
    if not ctx.invoked_subcommand:
        ctx.invoke(cast)


@cli.group(invoke_without_command=True, cls=CommandGroup,
           options_metavar='[-aph]', subcommand_metavar='[what]')
@click.pass_context
def cast(ctx):
    """Cast type with a Monotype caster.

    Casts composition, material for handsetting, QR codes.
    Can also cast a diecase proof.

    Can also be run in simulation mode without the actual caster."""
    address, port = ctx.obj.get('address'), ctx.obj.get('port')
    from .casting import Casting
    # replace the context object for the subcommands to see
    ctx.obj = Casting(address, port)
    if not ctx.invoked_subcommand:
        ctx.obj.main_menu()


@cast.command('ribbon', options_metavar='[-h]')
@click.argument('ribbon', metavar='[filename]', type=click.File())
@click.pass_obj
def cast_ribbon(casting, ribbon):
    """Cast composition from file or database."""
    casting.cast_file(ribbon)


@cast.command('xls', options_metavar='[-h]')
@click.argument('files', metavar='[filenames]',
                type=click.File(mode='rb'), nargs=-1)
@click.pass_obj
def cast_excel_file(casting, files):
    """Cast composition from file or database."""
    casting.cast_xls(files)


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


@cast.command('test', options_metavar='[-h]')
@click.pass_obj
def test_machine(casting):
    """Monotype caster testing and diagnostics."""
    casting.diagnostics()


@cast.command('align', options_metavar='[-h]')
@click.pass_obj
def align_machine(casting):
    """Monotype caster testing and diagnostics."""
    casting.calibrate_machine()


@cli.command(options_metavar='[-ht]')
@click.option('--testing', '-t', is_flag=True, flag_value=True,
              help='use a unstable/development version instead of stable')
def update(testing):
    """Update the software."""
    # Upgrade routine
    dev_prompt = 'Testing version (newest features, but unstable)? '
    if ui.confirm('Update the software?', default=False):
        use_dev_version = testing or ui.confirm(dev_prompt, default=False)
        pre = '--pre' if use_dev_version else ''
        os.system('pip3 install {} --upgrade rpi2caster'.format(pre))


@cli.command()
def meow():
    "Easter egg."
    text = r"""
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                   _                              _    ║
    ║    /\___/\       __   __     __   |    __  _ __       __   __    |    ║
    ║   |       |     /  \ /  \   /  \ -+-  |  \ |/  \     /  \ /  \  -+-   ║
    ║  _  *   *  _   |      __ |  \__   |   +--/ |        |      __ |  |    ║
    ║  -   /_\   -   |     /  \|     \  |   |    |        |     /  \|  |    ║
    ║      ---        \__/_\__/\__\__/___\_/ \__/|_        \__/_\__/\___\_  ║
    ║                                                                       ║
    ║ Hello Kitty!              gives your MONOTYPE nine lives              ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """
    try:
        ui.display('\nOh, this was meowsome.\n')
        ui.display(text)
    except (OSError, ImportError, FileNotFoundError):
        print('There are no Easter Eggs in this program.')
