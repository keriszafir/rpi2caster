# -*- coding: utf-8 -*-
"""rpi2caster - top-level script for starting the components"""
from os import system
from sys import argv
import argparse
from . import exceptions
from .text_ui import yes_or_no, menu, exit_program


def cast(args):
    """Casting on an actual caster or simulation"""
    from . import casting_session
    session = casting_session.Casting(args.ribbon_file)
    session.mode.simulation = args.simulation
    session.mode.punching = args.punching
    session.caster.UI = casting_session.UI
    casting_session.UI.DEBUG_MODE = args.debug
    # Skip menu if casting directly
    if args.direct and args.ribbon_file:
        session.cast()
    if args.testing:
        session.diagnostics_submenu()
    else:
        session.main_menu()


def inv(args):
    """Inventory management"""
    from rpi2caster import inventory
    # Pass the debug mode flag to the UI
    inventory.UI.DEBUG_MODE = args.debug
    inventory.main_menu()


def translate(args):
    """Text to ribbon translation and justification"""
    from rpi2caster import typesetting
    typesetting.UI.DEBUG_MODE = args.debug
    typesetting.main_menu()


def update(args):
    """Updates the software"""
    # Upgrade routine
    if yes_or_no('Update the software?'):
        pre = args.unstable and '--pre' or ''
        print('You may be asked for the admin password...')
        system('sudo pip3 install %s --upgrade rpi2caster' % pre)


def change_punching(args):
    """Switch between punching and casting modes"""
    args.punching = not args.punching


def change_simulation(args):
    """Switch between simulation and casting/punching modes"""
    args.simulation = not args.simulation


def main_menu(args):
    """Main menu - choose the module"""
    header = ('rpi2caster - computer aided type casting for Monotype '
              'composition / type & rule casters.'
              '\n\nMain menu:\n')
    while True:
        options = [(exit_program, 'Exit',
                    'Exits the rpi2caster suite'),
                   (cast, {True: 'Punch ribbon...',
                           False: 'Cast type...'}[args.punching],
                    {True: 'Punch a ribbon with a keyboard\'s paper tower',
                     False: ('Cast composition, sorts or spaces; '
                             'test the machine')}[args.punching]),
                   (inv, 'Inventory management...',
                    'List, add and remove diecase or wedge definitions'),
                   (translate, 'Typesetting...',
                    'Compose text for casting'),
                   (update, 'Update the program',
                    'Check whether new version is available and update'),
                   (change_punching, 'Switch to %s mode'
                    % {True: 'casting',
                       False: 'ribbon punching'}[args.punching],
                    ('The casting program has different functionality '
                     'in casting and punching modes.')),
                   (change_simulation, 'Switch to %s mode'
                    % {True: 'casting or ribbon punching',
                       False: 'simulation'}[args.simulation],
                    {True: 'Use a real machine',
                     False: 'Use a mockup for testing'}[args.simulation])]
        try:
            menu(options, header=header, footer='')(args)
        except (exceptions.ReturnToMenu, exceptions.MenuLevelUp,
                exceptions.ExitProgram):
            pass
        except (KeyboardInterrupt, EOFError):
            exit_program()


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
    main_parser.set_defaults(job=main_menu, debug=False, ribbon_file=None,
                             source=None, simulation=False, punching=False,
                             unstable=False, manual=False, diecase=False,
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
    cast_parser.add_argument('-d', '--debug', help='debug mode',
                             action="store_true")
    cast_parser.add_argument('-s', '--simulation', action='store_true',
                             help='simulate casting instead of real casting')
    cast_parser.add_argument('-p', '--punch', action='store_true',
                             dest='punching',
                             help='ribbon punching (perforation) mode')
    test_or_cast = cast_parser.add_mutually_exclusive_group()
    test_or_cast.add_argument('-t', '--test', action='store_true',
                              dest='testing',
                              help='caster / interface diagnostics')
    test_or_cast.add_argument('-D', '--direct', action="store_true",
                              help='direct casting - no menu',)
    cast_parser.add_argument('ribbon_file', metavar='ribbon', nargs='?',
                             help='ribbon file name')
    cast_parser.set_defaults(job=cast, ribbon_file=None)
    #
    # Inventory management subparser
    #
    inv_parser = jobs.add_parser('inventory', aliases=['i', 'inv'],
                                 help='Wedge and matrix case management')
    inv_parser.add_argument('-d', '--debug', help='debug mode',
                            action="store_true")
    inv_parser.set_defaults(job=inv)
    #
    # Software update subparser
    #
    upd_parser = jobs.add_parser('update', aliases=['u', 'upd'],
                                 help='Update the software')
    upd_parser.add_argument('-u', '--unstable', action='store_true',
                            help='update to unstable (development) version')
    upd_parser.set_defaults(job=update)
    #
    # Composition (typesetting) program subparser
    #
    comp_parser = jobs.add_parser('translate', aliases=['t', 'set'],
                                  help='Typesetting program')
    # Manual mode option - more control for user
    comp_parser.add_argument('-m', '--manual', help='use manual mode',
                             action='store_true')
    # Choose diecase layout
    comp_parser.add_argument('-D', '--diecase', dest='diecase_id',
                             help='diecase ID for typesetting',
                             metavar='ID')
    comp_parser.add_argument('-d', '--debug', help='Debug mode',
                             action="store_true")
    # Input filename option
    comp_parser.add_argument('source', help='source (text) file to translate',
                             metavar='text_file', nargs='?',
                             type=argparse.FileType('r', encoding='UTF-8'))
    # Output filename option
    comp_parser.add_argument('ribbon', help='ribbon file to generate',
                             metavar='ribbon_file', nargs='?',
                             type=argparse.FileType('w', encoding='UTF-8'))
    # Default action
    comp_parser.set_defaults(job=translate)
    args = main_parser.parse_args()
    # Parsers defined
    try:
        args.job(args)
    except (exceptions.ExitProgram, exceptions.ReturnToMenu,
            exceptions.MenuLevelUp):
        print('Goodbye!')
    except (KeyboardInterrupt, EOFError):
        print('\nInterrupted by user.')
    except AttributeError:
        if args.debug:
            raise
        else:
            main_parser.print_help()


if __name__ == '__main__':
    main()
