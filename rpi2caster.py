#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rpi2caster - top-level script for starting the components"""
import argparse


def cast(args):
    """Casting on an actual caster or simulation"""
    from rpi2caster import casting
    if args.simulate:
        from rpi2caster import simulation as casting_backend
    else:
        from rpi2caster import monotype as casting_backend
    # Pass the debug mode flag to the UI
    casting_backend.ui.DEBUG_MODE = args.debug
    # Tie them together
    job = casting.Casting(args.ribbon)
    job.caster = casting_backend.Monotype()
    casting.main_menu(job)


def inventory(args):
    """Inventory management"""
    from rpi2caster import inventory
    # Pass the debug mode flag to the UI
    inventory.ui.DEBUG_MODE = args.debug
    inventory.main_menu()


def typesetting(args):
    """Text to ribbon translation and justification"""
    from rpi2caster import typesetter
    typesetter.ui.DEBUG_MODE = args.debug
    typesetter.main_menu()


def main():
    """Main function

    Parse input options and decide which to run"""
    # Help description and epilogue i.e. what you see at the bottom
    desc = 'rpi2caster - Raspberry Pi controls a Monotype composition caster.'
    epi = 'Typesetting is not ready yet.'
    # Initialize the main arguments parser
    main_parser = argparse.ArgumentParser(description=desc, epilog=epi)
    #
    # General options parser
    #
    gen_parser = argparse.ArgumentParser(description='General options')
    gen_parser.add_argument('-d', '--debug', help='turns the debug mode on',
                            action="store_true")
    gen_parser.add_argument('-u', '--upgrade', help='upgrades the software',
                            action="store_true")
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
    cast_parser.add_argument('-s', '--simulate',
                             help='Simulate casting instead of real casting',
                             action='store_true')
    cast_parser.add_argument('ribbon', metavar='ribbon_file', nargs='?',
                             help='Ribbon file name')
    cast_parser.set_defaults(job=cast, ribbon=None)
    #
    # Inventory management subparser
    #
    inv_parser = jobs.add_parser('inventory', aliases=['i', 'inv'],
                                 parents=[gen_parser], add_help=False,
                                 help='Wedge and matrix case management')
    inv_parser.set_defaults(job=inventory)
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
    comp_parser.set_defaults(job=typesetting)
    args = main_parser.parse_args()
    # Parsers defined
    # Upgrade routine
    if args.upgrade:
        print('Upgrading...')
    else:
        args.job(args)


if __name__ == '__main__':
    main()
