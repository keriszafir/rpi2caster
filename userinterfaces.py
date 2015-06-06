# -*- coding: utf-8 -*-
"""
user-interfaces

This module contains user interfaces to be used by rpi2caster suite.
"""

# IMPORTS for text user interface
import sys
import os
import readline
import glob


class TextUI(object):
    """TextUI:

    Use this class for creating a text-based console user interface.
    A caster object must be created before instantiating this class.
    Suitable for controlling a caster from the local terminal or via SSH,
    supports UTF-8 too.
    """

    def __init__(self, debug_mode=False):
    # Get the debug-mode from input parameters
        self.debug_mode = debug_mode

    def __enter__(self):
        """Try to call main menu for a job.

        Display a message when user presses ctrl-C.
        """
    # Print some debug info
        self.debug_info('Entering text UI context...')
        try:
            pass
        except KeyboardInterrupt:
            print '\nUser pressed ctrl-C. Exiting.'
        finally:
            print '\nGoodbye!\n'

    def menu(self, options, header='', footer=''):
        """menu(options={'foo':'bar','baz':'qux'}
                        header=foo,
                        footer=bar):

        A menu which takes three arguments:
        header - string to be displayed above,
        footer - string to be displayed below,

        After choice is made, return the command.

        Set up vars for conditional statements,
        and lists for appending new items.

        choices - options to be entered by user
        """
        your_choice = ''
        choices = []
        # Clear the screen, display header and add two empty lines
        self.clear()
        if header:
            print header
            print
        # Display all the options; we'll take care of 0 later
        for choice in options:
            if choice != 0:
            # Print the option choice and displayed text
                print '\t', choice, ' : ', options[choice], '\n'
            # Add this option to possible choices.
            # We need to convert it to string first.
                choices.append(str(choice))
        try:
        # If an option "0." is available, print it at the end
            option_zero = options[0]
            print '\n\t', 0, ' : ', option_zero
            choices.append('0')
        except KeyError:
            pass
        # Print footer, if defined
        if footer:
            print '\n' + footer
        # Add an empty line to separate prompt
        print '\n'
        # Ask for user input
        while your_choice not in choices:
            your_choice = raw_input('Your choice: ')
        else:
        # Valid option is chosen, return integer if options were numbers,
        # else return string
            try:
                return int(your_choice)
            except ValueError:
                return your_choice

    def clear(self):
        # Clear screen
        os.system('clear')

    def display(self, *args):
        # Display info for the user - print all in one line
        for arg in args:
            print arg,
        print '\n'

    def debug_info(self, *args):
        # Print debug message to screen if in debug mode
        if self.debug_mode:
            for arg in args:
                print arg,
            print '\n'

    def debug_enter_data(self, message):
        # For debug-specific data or confirmations
        if self.debug_mode:
            return raw_input(message)


    def exception_handler(self):
        # Raise caught exceptions in debug mode
        if self.debug_mode:
            print sys.exc_info()

    def enter_data(self, message):
        # Let user enter the data
        return raw_input(message)

    def enter_input_filename(self):
        def tab_complete(text, state):
            """tab_complete(text, state):
    
            This function enables tab key auto-completion when you
            enter the filename.
            """
            return (glob.glob(text+'*')+[None])[state]
        # Set readline parameters
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind('tab: complete')
        readline.set_completer(tab_complete)
        # Enter the input filename; check if the file is readable
        filename = raw_input('\n Enter the input file name: ')
        filename = os.path.realpath(filename)
        try:
            with open(filename, 'r'):
                return filename
        except IOError:
            raw_input('Wrong filename or file not readable!')
            return ''

    def enter_output_filename(self):
        def tab_complete(text, state):
            """tab_complete(text, state):
    
            This function enables tab key auto-completion when you
            enter the filename.
            """
            return (glob.glob(text+'*')+[None])[state]
        # Set readline parameters
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind('tab: complete')
        readline.set_completer(tab_complete)
        # Enter the output filename; no check here
        filename = raw_input('\n Enter the output file name: ')
        filename = os.path.realpath(filename)
        return filename

    def hold_on_exit(self):
        raw_input('Press [Enter] to return to main menu...')

    def simple_menu(self, message, options):
        """Simple menu:

        A simple menu where user is asked what to do.
        Wrong choice points back to the menu.

        Message: string displayed on screen;
        options: a list or tuple of strings - options.
        """
        ans = ''
        while ans.upper() not in options and ans.lower() not in options:
            ans = raw_input(message)
        return ans

    def exit_program(self):
        """Exit program:

        All objects call this method whenever they want to exit program.
        This is because we may do something specific in different UIs,
        so an abstraction layer may come in handy.
        """
        exit()
        return False

    def __exit__(self, *args):
        self.debug_info('Exiting text UI context.')

class WebInterface(object):
    """WebInterface:

    TODO: not implemented yet!
    Use this class for instantiating text-based console user interface
    """

    def __init__(self):
        pass

    def __enter__(self):
        return self

    def web_UI(self):
        """This is a placeholder for web interface method. Nothing yet..."""
        pass

    def __exit__(self, *args):
        pass
