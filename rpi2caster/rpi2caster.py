# -*- coding: utf-8 -*-
"""rpi2caster - top-level script for starting the components"""
from os import system
from sys import argv
from contextlib import suppress
import argparse
from . import exceptions as e
from . import text_ui as UI
from .global_config import Config
from .database import Database
CFG = Config()
DB = Database()


def casting_job(args):
    """Casting on an actual caster or simulation"""
    from . import casting
    session = casting.Casting()
    session.ribbon_file = args.ribbon_file
    session.text_file = args.text_file
    session.input_text = args.input_text
    session.ribbon_id = args.ribbon_id
    session.diecase_id = args.diecase_id
    session.wedge_name = args.wedge_name
    session.manual_mode = args.manual_mode
    session.line_length = args.measure
    session.caster.mode.simulation = args.simulation or None
    session.caster.mode.punching = args.punching
    # Method dispatcher
    # Skip menu if casting directly, typesetting or testing
    if args.input_text:
        # TODO use object properties instead of arguments/parameters
        return session.quick_typesetting, args.input_text
    elif args.direct:
        return session.cast_composition
    elif args.testing:
        return session.diagnostics_submenu
    else:
        return session.main_menu


def typesetting_job(args):
    """Text to ribbon translation and justification"""
    from . import typesetting
    session = typesetting.Typesetting()
    session.text_file = args.text_file
    session.input_text = args.input_text
    session.ribbon_file = args.ribbon_file
    session.ribbon_id = args.ribbon_id
    session.diecase_id = args.diecase_id
    session.wedge_name = args.wedge_name
    session.manual_mode = args.manual_mode
    session.line_length = args.measure
    # Only one method here
    return session.main_menu


def update(args):
    """Updates the software"""
    # Upgrade routine
    dev_prompt = 'Testing version (newest features, but unstable)? '
    if UI.confirm('Update the software?', default=False):
        use_dev_version = (args.testing or
                           UI.confirm(dev_prompt, default=False))
        pre = '--pre' if use_dev_version else ''
        print('You may be asked for the admin password...')
        system('sudo pip3 install %s --upgrade rpi2caster' % pre)


def inventory(args):
    """Inventory management - diecase manipulation etc."""
    from . import matrix_data
    if args.list_diecases:
        # Just show what we have
        return matrix_data.list_diecases
    elif args.diecase_id:
        # Work on a specific diecase
        diecase = matrix_data.Diecase(args.diecase_id)
        return diecase.manipulation_menu
    else:
        # Choose diecase and work on it
        return matrix_data.diecase_operations


def meow(_):
    "Easter egg"
    try:
        from . import easteregg
        return easteregg.show
    except (OSError, FileNotFoundError):
        print('There are no Easter Eggs in this program.')


def main_menu(args):
    """Main menu - choose the module"""
    def toggle_punching(args):
        """Switch between punching and casting modes"""
        args.punching = not args.punching

    def toggle_simulation(args):
        """Switch between simulation and casting/punching modes"""
        args.simulation = not args.simulation

    def exit_program(*_):
        """Breaks out of menu"""
        nonlocal finished
        finished = True

    header = ('rpi2caster - computer aided type casting for Monotype '
              'composition / type & rule casters.'
              '\n\nMain menu:\n')
    finished = False
    while not finished:
        options = [(exit_program, 'Exit',
                    'Exits the rpi2caster suite'),
                   (casting_job, {True: 'Punch ribbon...',
                                  False: 'Cast type...'}[args.punching],
                    {True: 'Punch a ribbon with a keyboard\'s paper tower',
                     False: ('Cast composition, sorts or spaces; '
                             'test the machine')}[args.punching]),
                   (typesetting_job, 'Typesetting...',
                    'Compose text for casting'),
                   (inventory, 'Diecase manipulation...',
                    'Add, display, edit or remove matrix case definitions'),
                   (update, 'Update the program',
                    'Check whether new version is available and update'),
                   (toggle_punching, 'Switch to %s mode'
                    % {True: 'casting',
                       False: 'ribbon punching'}[args.punching],
                    ('The casting program has different functionality '
                     'in casting and punching modes.')),
                   (toggle_simulation, 'Switch to %s mode'
                    % {True: 'casting or ribbon punching',
                       False: 'simulation'}[args.simulation],
                    {True: 'Use a real machine',
                     False: 'Use a mockup for testing'}[args.simulation])]
        try:
            job = UI.menu(options, header=header, footer='')
            # Determine the subroutine and arguments
            # Job retval can contain additional arguments
            routine_retval = job(args)
            try:
                entry_point, *arguments = routine_retval
                entry_point(arguments)
            except TypeError:
                # A single or None value is returned
                with suppress(TypeError):
                    routine_retval()
        except (e.ReturnToMenu, e.MenuLevelUp):
            pass
        except (KeyboardInterrupt, EOFError):
            finished = True


def main():
    """Main function

    Parse input options and decide which to run"""
    def build_casting_parser():
        """Define options for the casting parser"""
        # Casting subparser
        parser = cmds.add_parser('cast', aliases=['c'],
                                 help=('Casting with a Monotype caster '
                                       'or mockup caster for testing'))
        # Choose specific diecase
        parser.add_argument('-m', '--diecase', metavar='ID',
                            dest='diecase_id',
                            help='diecase ID for casting')
        # Punch ribbon: uses different sensor, always adds O+15 to combinations
        parser.add_argument('-p', '--punch', action='store_true',
                            dest='punching',
                            help='ribbon punching (perforation) mode')
        # Simulation mode: casting/punching without the actual caster/interface
        parser.add_argument('-s', '--simulation', action='store_true',
                            help='simulation run instead of real casting')
        # Entry point decides where the user starts the program
        start = parser.add_mutually_exclusive_group()
        # Starts in the diagnostics submenu of the casting program
        start.add_argument('-T', '--test', action='store_true', dest='testing',
                           help='caster / interface diagnostics')
        # Allows to start casting right away without entering menu
        start.add_argument('-D', '--direct', action="store_true",
                           help='direct casting - no menu',)
        # Quick typesetting feature
        start.add_argument('-t', '--text', dest='input_text',
                           metavar='"input text"',
                           help=('compose and cast the '
                                 'single- or double-quoted input text'))
        # Choose specific wedge
        parser.add_argument('-w', '--wedge', metavar='W', dest='wedge_name',
                            help='wedge to use: [s]series-set_width[e]')
        # Ribbon ID for choosing from database
        parser.add_argument('-R', '--ribbon_id', metavar='R',
                            help='ribbon ID to choose from database')
        # Ribbon - input file specification
        parser.add_argument('ribbon_file', metavar='ribbon', nargs='?',
                            type=argparse.FileType('r', encoding='UTF-8'),
                            help='ribbon file name')
        parser.set_defaults(job=casting_job)

    def build_typesetting_parser():
        """Typesetting a.k.a. text translation options"""
        parser = cmds.add_parser('translate', aliases=['t', 'set'],
                                 help='Typesetting program')
        # Choose diecase layout
        parser.add_argument('-m', '--diecase', dest='diecase_id', metavar='ID',
                            help='diecase ID for typesetting')
        # Input filename option
        parser.add_argument('text_file', metavar='text_file', nargs='?',
                            help='source (text) file to translate',
                            type=argparse.FileType('r', encoding='UTF-8'))
        # Quick typesetting feature
        parser.add_argument('-t', '--text', dest='input_text',
                            metavar='"input text"',
                            help=('compose and cast the '
                                  'single- or double-quoted input text'))
        # Output filename option
        parser.add_argument('ribbon_file', metavar='ribbon_file', nargs='?',
                            help='ribbon file to generate',
                            type=argparse.FileType('w+', encoding='UTF-8'))
        # Measure (line length)
        parser.add_argument('-M', '--measure',
                            metavar='measure', dest='measure',
                            help='line length with units e.g. 16cc')
        # Wedge name to use instead of diecase's assigned wedge
        parser.add_argument('-w', '--wedge', metavar='W', dest='wedge_name',
                            help='wedge to use: [s]series-set_width[e]')
        # Automatic typesetting
        parser.add_argument('--manual', dest='manual_mode',
                            action='store_true',
                            help='use manual typesetting engine')
        # Default action
        parser.set_defaults(job=typesetting_job)

    def build_misc_parsers():
        """Miscellaneous parsers"""
        # Update subparser
        upd_parser = cmds.add_parser('update', aliases=['u', 'upd'],
                                     help='Update the software')
        upd_parser.add_argument('-t', '--testing', action='store_true',
                                help='use testing rather than stable version')
        upd_parser.set_defaults(job=update)
        # Easter egg subparser
        meow_parser = cmds.add_parser('meow', help='here, kitty, kitty!',
                                      aliases=['miauw', 'miau', 'miaou', 'mio',
                                               'miaow', 'mew', 'mjav', 'miao'])
        meow_parser.set_defaults(job=meow)

    def build_inv_parser():
        """Inventory management parser"""
        parser = cmds.add_parser('inventory', aliases=['i', 'inv'],
                                 help='Matrix case management')
        # List the diecases and exit
        parser.add_argument('-l', '--list_diecases', action='store_true',
                            help='list all diecases and finish')
        # Manipulate diecase with given ID
        parser.add_argument('-m', '--diecase', dest='diecase_id', metavar='ID',
                            help='work on diecase with given ID')
        parser.set_defaults(job=inventory)

    def build_main_parser():
        """Main parser"""
        # Help description and epilogue i.e. what you see at the bottom
        desc = ('Starting rpi2caster without arguments will open the main '
                'menu, where you can choose what to do (casting, inventory '
                'management, typesetting), toggle simulation or '
                'perforation modes.')
        epi = ('Enter "%s [command] -h" for detailed help about its options. '
               'Typesetting is not ready yet.' % argv[0])
        # Initialize the main arguments parser
        parser = argparse.ArgumentParser(description=desc, epilog=epi)
        # Debug mode
        parser.add_argument('-d', '--debug', help='debug mode',
                            action="store_true")
        parser.add_argument('--database', metavar='FILE',
                            help='path to alternative sqlite3 database file')
        parser.add_argument('--config', metavar='FILE',
                            help='path to alternative configuration file')
        # Set default values for all options globally
        parser.set_defaults(job=main_menu, debug=False, ribbon_file=None,
                            ribbon_id=None, simulation=False,
                            punching=False, text_file=None,
                            list_diecases=False,
                            diecase_id=None, wedge_name=None, input_text=None,
                            direct=False, testing=False, database=None,
                            config=None, measure=None, manual_mode=False)
        return parser

    # Build the parsers and get the arguments
    main_parser = build_main_parser()
    cmds = main_parser.add_subparsers(title='Commands', help='description:',
                                      description='Choose what you want to do')
    build_typesetting_parser()
    build_casting_parser()
    build_inv_parser()
    build_misc_parsers()
    main_parser.parse_args()
    args = main_parser.parse_args()
    UI.DEBUG_MODE = args.debug
    global DB, CFG
    # Update configuration and database
    CFG = Config(args.config)
    DB = Database(args.database)
    # Parse the arguments, get the entry point
    try:
        routine_retval = args.job(args)
    except AttributeError:
        # User provided wrong command line arguments. Display help and quit.
        main_parser.print_help()
    # Figure out if additional arguments are provided
    try:
        entry_point, *arguments = routine_retval
        entry_point(*arguments)
    except TypeError:
        # Use case: no additional arguments provided
        # A single or None value is returned
        with suppress(TypeError):
            routine_retval()
    except (KeyboardInterrupt, EOFError):
        print('\nInterrupted by user.')
    except (e.ReturnToMenu, e.MenuLevelUp):
        pass
    finally:
        print('Goodbye!')


if __name__ == '__main__':
    main()
