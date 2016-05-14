# -*- coding: utf-8 -*-
"""rpi2caster - top-level script for starting the components"""
from os import system
from sys import argv
import argparse
from . import exceptions as e
from .text_ui import confirm, menu
from .matrix_data import diecase_operations, list_diecases, Diecase


def cast(args):
    """Casting on an actual caster or simulation"""
    from . import casting_session
    session = casting_session.Casting(ribbon_file=args.ribbon_file,
                                      ribbon_id=args.ribbon_id,
                                      diecase_id=args.diecase_id,
                                      wedge_name=args.wedge_name)
    simulation = args.simulation or None
    session.caster.mode.simulation = simulation
    session.caster.mode.punching = args.punching
    casting_session.UI.DEBUG_MODE = args.debug
    # Skip menu if casting directly or testing
    if args.direct:
        session.cast_composition()
    elif args.testing:
        session.diagnostics_submenu()
    else:
        session.main_menu()


def composition(args):
    """Text to ribbon translation and justification"""
    from . import typesetting_session
    session = typesetting_session.Typesetting(manual_mode=args.manual_mode,
                                              text_file=args.text_file,
                                              ribbon_file=args.ribbon_file,
                                              diecase_id=args.diecase_id)
    typesetting_session.UI.DEBUG_MODE = args.debug
    session.main_menu()


def update(args):
    """Updates the software"""
    # Upgrade routine
    dev_prompt = 'Testing version (newest features, but unstable)? '
    if confirm('Update the software?', default=False):
        use_dev_version = args.testing or confirm(dev_prompt, default=False)
        pre = use_dev_version and '--pre' or ''
        print('You may be asked for the admin password...')
        system('sudo pip3 install %s --upgrade rpi2caster' % pre)


def inventory(args):
    """Inventory management - diecase manipulation etc."""
    if args.list_diecases:
        # Just show what we have
        list_diecases()
    elif args.diecase_id:
        # Work on a specific diecase
        diecase = Diecase(args.diecase_id)
        diecase.manipulation_menu()
    else:
        # Choose diecase and work on it
        diecase_operations()


def meow(_):
    "Easter egg"
    try:
        from . import easteregg
        easteregg.show()
    except (OSError, FileNotFoundError):
        print('There are no Easter Eggs in this program.')


def toggle_punching(args):
    """Switch between punching and casting modes"""
    args.punching = not args.punching


def toggle_simulation(args):
    """Switch between simulation and casting/punching modes"""
    args.simulation = not args.simulation


def main_menu(args):
    """Main menu - choose the module"""
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
                   (cast, {True: 'Punch ribbon...',
                           False: 'Cast type...'}[args.punching],
                    {True: 'Punch a ribbon with a keyboard\'s paper tower',
                     False: ('Cast composition, sorts or spaces; '
                             'test the machine')}[args.punching]),
                   (composition, 'Typesetting...',
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
            menu(options, header=header, footer='')(args)
        except (e.ReturnToMenu, e.MenuLevelUp):
            pass
        except (KeyboardInterrupt, EOFError):
            finished = True


def main():
    """Main function

    Parse input options and decide which to run"""
    # Help description and epilogue i.e. what you see at the bottom
    desc = ('Starting rpi2caster without arguments will open the main menu, '
            'where you can choose what to do (casting, inventory management, '
            'typesetting), toggle simulation or perforation modes.')
    epi = ('Enter "%s [command] -h" for detailed help about its options. '
           'Typesetting is not ready yet.' % argv[0])
    # Initialize the main arguments parser
    main_parser = argparse.ArgumentParser(description=desc, epilog=epi)
    # Set default values for all options globally
    main_parser.set_defaults(job=main_menu, debug=False, ribbon_file='',
                             ribbon_id='', source=None, simulation=None,
                             punching=False, text_file='',
                             manual_mode=False, list_diecases=False,
                             diecase_id='', wedge_name='',
                             direct=False, testing=False)
    #
    # Define commands
    #
    # Subparsers for jobs: casting, inventory management, typesetting
    jobs = main_parser.add_subparsers(title='Commands',
                                      description='Choose what you want to do',
                                      help='description:')
    #
    # Casting subparser
    #
    cast_parser = jobs.add_parser('cast', aliases=['c'],
                                  help=('Casting with a Monotype caster '
                                        'or mockup caster for testing'))
    # Debug mode
    cast_parser.add_argument('-d', '--debug', help='debug mode',
                             action="store_true")
    # Choose specific diecase
    cast_parser.add_argument('-m', '--diecase', metavar='ID',
                             dest='diecase_id', help='diecase ID for casting')
    # Punch ribbon: uses different sensor, always adds O+15 to combinations
    cast_parser.add_argument('-p', '--punch', action='store_true',
                             dest='punching',
                             help='ribbon punching (perforation) mode')
    # Simulation mode: casting/punching without the actual caster/interface
    cast_parser.add_argument('-s', '--simulation', action='store_true',
                             help='simulate casting instead of real casting')
    test_or_cast = cast_parser.add_mutually_exclusive_group()
    # Starts in the diagnostics submenu of the casting program
    test_or_cast.add_argument('-T', '--test', action='store_true',
                              dest='testing',
                              help='caster / interface diagnostics')
    # Allows to start casting right away without entering menu
    test_or_cast.add_argument('-D', '--direct', action="store_true",
                              help='direct casting - no menu',)
    # Choose specific wedge
    cast_parser.add_argument('-w', '--wedge', metavar='W', dest='wedge_name',
                             help='wedge to use: [s]series-set_width[e]')
    # Ribbon ID for choosing from database
    cast_parser.add_argument('-R', '--ribbon_id', metavar='R',
                             help='ribbon ID to choose from database')
    # Ribbon - input file specification
    cast_parser.add_argument('ribbon_file', metavar='ribbon', nargs='?',
                             help='ribbon file name')
    cast_parser.set_defaults(job=cast)
    #
    # Software update subparser
    #
    upd_parser = jobs.add_parser('update', aliases=['u', 'upd'],
                                 help='Update the software')
    # Update to unstable version
    upd_parser.add_argument('-t', '--testing', action='store_true',
                            help='use testing rather than stable version')
    upd_parser.set_defaults(job=update)
    #
    # Composition (typesetting) program subparser
    #
    comp_parser = jobs.add_parser('translate', aliases=['t', 'set'],
                                  help='Typesetting program')
    # Manual mode option - more control for user
    comp_parser.add_argument('-M', '--manual', help='use manual mode',
                             dest='manual_mode', action='store_true')
    # Choose diecase layout
    comp_parser.add_argument('-m', '--diecase', dest='diecase_id',
                             help='diecase ID for typesetting',
                             metavar='ID')
    # Debug mode
    comp_parser.add_argument('-d', '--debug', help='debug mode',
                             action="store_true")
    # Input filename option
    comp_parser.add_argument('text_file',
                             help='source (text) file to translate',
                             metavar='text_file', nargs='?',
                             type=argparse.FileType('r', encoding='UTF-8'))
    # Output filename option
    comp_parser.add_argument('ribbon_file', help='ribbon file to generate',
                             metavar='ribbon_file', nargs='?',
                             type=argparse.FileType('w', encoding='UTF-8'))
    # Default action
    comp_parser.set_defaults(job=composition)
    #
    # Inventory subparser
    #
    inv_parser = jobs.add_parser('inventory', aliases=['i', 'inv'],
                                 help='Matrix case management')
    # List the diecases and exit
    inv_parser.add_argument('-l', '--list_diecases', action='store_true',
                            help='list all diecases and finish')
    # Manipulate diecase with given ID
    inv_parser.add_argument('-m', '--diecase', dest='diecase_id',
                            help='work on diecase with given ID',
                            metavar='ID')
    inv_parser.set_defaults(job=inventory)
    #
    # Easter egg subparser
    #
    meow_parser = jobs.add_parser('meow',
                                  aliases=['miauw', 'miau', 'miaou', 'miaow',
                                           'mew', 'mjav', 'mio', 'miao'],
                                  help='see for yourself...')
    meow_parser.set_defaults(job=meow)
    # Parsers are defined - get the args...
    args = main_parser.parse_args()
    try:
        args.job(args)
    except (e.ReturnToMenu, e.MenuLevelUp):
        pass
    except (KeyboardInterrupt, EOFError):
        print('\nInterrupted by user.')
    except AttributeError:
        if args.debug:
            raise
        else:
            main_parser.print_help()
    finally:
        print('Goodbye!')


if __name__ == '__main__':
    main()
