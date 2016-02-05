# -*- coding: utf-8 -*-
"""rpi2caster - top-level script for starting the components"""
from os import system
import argparse
from rpi2caster import exceptions
from rpi2caster.text_ui import yes_or_no


def cast(args):
    """Casting on an actual caster or simulation"""
    from rpi2caster import casting
    job = casting.Casting(args.ribbon_file)
    if args.simulate:
        # Simulation mockup caster
        from rpi2caster import common_caster as caster_module
    else:
        # Real caster
        from rpi2caster import monotype as caster_module
    caster_module.UI.DEBUG_MODE = args.debug
    job.caster = caster_module.Caster()
    # Perforation mode if desired or not depending on command line arguments
    job.caster.is_perforator = args.is_perforator
    job.main_menu()


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


def main():
    """Main function

    Parse input options and decide which to run"""
    # Help description and epilogue i.e. what you see at the bottom
    desc = 'rpi2caster - Raspberry Pi controls a Monotype composition caster.'
    epi = 'Typesetting is not ready yet.'
    # Initialize the main arguments parser
    # Create the update optoin for easy update
    main_parser = argparse.ArgumentParser(description=desc, epilog=epi)
    main_parser.add_argument('-u', '--update', help='Update the software',
                             action="store_true")
    #
    # General options parser - for all sub-programs
    #
    gen_parser = argparse.ArgumentParser(description='General options')
    gen_parser.add_argument('-d', '--debug', help='Debug mode',
                            action="store_true")
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
                                  parents=[gen_parser], add_help=False,
                                  help=('Casting with a Monotype caster '
                                        'or mockup caster for testing'))
    cast_parser.add_argument('-s', '--simulate', action='store_true',
                             help='Simulate casting instead of real casting')
    cast_parser.add_argument('-p', '--perforate', action='store_true',
                             dest='is_perforator',
                             help='Ribbon perforation mode')
    cast_parser.add_argument('ribbon_file', metavar='ribbon', nargs='?',
                             help='Ribbon file name')
    cast_parser.set_defaults(job=cast, ribbon_file=None)
    #
    # Inventory management subparser
    #
    inv_parser = jobs.add_parser('inventory', aliases=['i', 'inv'],
                                 parents=[gen_parser], add_help=False,
                                 help='Wedge and matrix case management')
    inv_parser.set_defaults(job=inv)
    #
    # Composition (typesetting) program subparser
    #
    comp_parser = jobs.add_parser('translate', aliases=['t', 'set'],
                                  parents=[gen_parser], add_help=False,
                                  help='Typesetting program')
    # Input filename option
    comp_parser.add_argument('source', help='source (text) file to translate',
                             metavar='text_file', nargs='?',
                             type=argparse.FileType('r', encoding='UTF-8'))
    # Output filename option
    comp_parser.add_argument('ribbon', help='ribbon file to generate',
                             metavar='ribbon_file', nargs='?',
                             type=argparse.FileType('w', encoding='UTF-8'))
    # Manual mode option - more control for user
    comp_parser.add_argument('-m', '--manual', help='use manual mode',
                             action='store_true')
    # Choose diecase layout
    comp_parser.add_argument('-D', '--diecase', dest='diecase_id',
                             help='diecase ID for typesetting',
                             metavar='ID')
    # Default action
    comp_parser.set_defaults(job=translate)
    args = main_parser.parse_args()
    # Parsers defined
    try:
        # Upgrade routine
        if args.update:
            if yes_or_no('Update the software?'):
                print('Entering your password may be necessary.')
                system('sudo pip3 install --install-option="--install-data=/dev/null" --upgrade rpi2caster')
        elif args.job:
            args.job(args)
    except exceptions.ExitProgram:
        print('Goodbye!')
    except (KeyboardInterrupt, EOFError):
        print('\nInterrupted by user.')
    except AttributeError:
        main_parser.print_help()


if __name__ == '__main__':
    main()
