# -*- coding: utf-8 -*-
"""rpi2caster - top-level script for starting the components"""
from os import system
from sys import argv
import argparse
from .ui import UI, Abort, Finish, option
from .misc import MQ


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
    session.caster.simulation = args.simulation or None
    session.caster.punching = args.punching
    # Method dispatcher
    # Skip menu if casting directly, typesetting or testing
    if args.input_text:
        # TODO use object properties instead of arguments/parameters
        session.quick_typesetting(args.input_text)
    elif args.direct:
        session.cast_composition()
    elif args.testing:
        session.caster.diagnostics()
    else:
        session.main_menu()


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
    session.main_menu()


def update(args):
    """Updates the software"""
    # Upgrade routine
    dev_prompt = 'Testing version (newest features, but unstable)? '
    if UI.confirm('Update the software?', default=False):
        use_dev_version = (args.testing or
                           UI.confirm(dev_prompt, default=False))
        pre = '--pre' if use_dev_version else ''
        print('You may be asked for the admin password...')
        system('sudo pip3 install {} --upgrade rpi2caster'.format(pre))


def inventory(args):
    """Inventory management - diecase manipulation etc."""
    from . import matrix_controller
    if args.list_diecases:
        # Just show what we have
        matrix_controller.list_diecases()
    else:
        # edit diecase (or choose, if failed)
        matrix_controller.MatrixEditor(args.diecase_id)


def meow(_):
    "Easter egg"
    try:
        from .resources import easteregg
        easteregg.show()
    except (OSError, ImportError, FileNotFoundError):
        print('There are no Easter Eggs in this program.')


def show_version(_):
    "Show the rpi2caster version"
    from . import __version__
    print('rpi2caster v{}'.format(__version__))


def main_menu(args):
    """Main menu - choose the module"""
    def toggle_punching(args):
        """Switch between punching and casting modes"""
        args.punching = not args.punching

    def toggle_simulation(args):
        """Switch between simulation and casting/punching modes"""
        args.simulation = not args.simulation

    header = ('rpi2caster - computer aided type casting for Monotype '
              'composition / type & rule casters.'
              '\n\nMain menu:\n')
    options = [option(key='c', value=casting_job, seq=20,
                      cond=lambda: not args.punching,
                      text='Casting...',
                      desc=('Cast composition, sorts, typecases or spaces; '
                            'test the machine')),
               option(key='c', value=toggle_punching, seq=70,
                      cond=lambda: args.punching,
                      text='Switch to casting mode',
                      desc='Switch from punching to casting'),

               option(key='d', value=inventory, seq=30,
                      text='Diecase manipulation...',
                      desc='Manage the matrix case collection'),

               option(key='p', value=casting_job, seq=20,
                      cond=lambda: args.punching,
                      text='Punching...',
                      desc='Punch a ribbon with a keyboard\'s perforator'),
               option(key='p', value=toggle_punching, seq=70,
                      cond=lambda: not args.punching,
                      text='Switch to perforation mode',
                      desc='Switch from casting to ribbon punching'),

               option(key='s', value=toggle_simulation, seq=80,
                      cond=lambda: not args.simulation,
                      text='Switch to simulation mode',
                      desc='Test casting without the caster or interface'),
               option(key='s', value=toggle_simulation, seq=80,
                      cond=lambda: args.simulation,
                      text='Switch to machine control mode',
                      desc='Use a real Monotype caster or perforator'),

               option(key='t', value=typesetting_job, seq=10,
                      text='Typesetting...',
                      desc='Compose text for casting'),

               option(key='u', value=update,
                      text='Update the program', seq=90)]

    UI.dynamic_menu(options, header, allow_abort=True, func_args=(args,))


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
        # Version parser
        version_parser = cmds.add_parser('version', aliases=['v', 'ver'],
                                         help='Show the software version')
        version_parser.set_defaults(job=show_version)

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
        epi = ('Enter "{} [command] -h" for detailed help about its options. '
               'Typesetting is not ready yet.'.format(argv[0]))
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
    UI.verbosity = 3 if args.debug else 0
    # Update configuration and database
    MQ.update('config', {'config_path': args.config})
    MQ.update('database', {'url': args.database, 'debug': args.debug})
    # Parse the arguments, get the entry point
    try:
        job = args.job
    except AttributeError:
        # User provided wrong command line arguments. Display help and quit.
        main_parser.print_help()
        return
    # Run the routine
    try:
        job(args)
    except (Abort, Finish):
        print('Goodbye!')


if __name__ == '__main__':
    main()
