"""
user-interfaces

This module contains user interfaces to be used by rpi2caster suite.
"""

# IMPORTS for text user interface
import io
import os
import readline
import glob

DEBUG_MODE = False


def menu(options, header='', footer=''):
    """menu(options=[(name1, opt1), (name2, opt2)...],
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
    # Clear the screen, display header and add two empty lines
    clear()
    if header:
        print(header)  # TODO add newline
    # Display all the options; we'll take care of 0 later
    options = dict([(i, option) for i, option in enumerate(options)])
    # Menu body
    # Tab indent, option number, option name (not processing option 0 yet!)
    print('\n'.join(['\t %i : %s \n' % (k, options[k][0])
                     for k in sorted(options) if k]))
    # Option 0 is displayed last, add some whitespace around it
    try:
        print('\n\n\t %i : %s \n' % (0, options[0][0]))
    except KeyError:
        # Theoretically, there's always an option number zero... but if not?
        pass
    # Print footer, if defined
    if footer:
        print(footer)  # TODO: add newline
    # Add an empty line to separate prompt
    print('\n')
    # Ask for user input
    your_choice = ''
    while your_choice not in options:
        # Wait until user enters proper data
        your_choice = input('Your choice: ')
        try:
            your_choice = int(your_choice)
        except ValueError:
            # Entered anything non-digit - repeat
            your_choice = ''
    # At last, we have chosen a valid option...
    # Return a corresponding value - which is option[1]
    return options[your_choice][1]


def clear():
    """Clears the screen"""
    os.system('clear')


def display(*args, **kwargs):
    """Displays info for the user - print all in one line"""
    print(*args, **kwargs)  # TODO: add newline


def debug_info(*args, **kwargs):
    """Prints debug messages to screen if in debug mode"""
    if DEBUG_MODE:
        print(*args, **kwargs)  # TODO: add newline


def debug_enter_data(message):
    """For debug-specific data or confirmations"""
    if DEBUG_MODE:
        return input(message)


def enter_data(message):
    """Let user enter the data"""
    return input(message)


def tab_complete(text, state):
    """tab_complete(text, state):

    This function enables tab key auto-completion when you
    enter the filename.
    """
    return (glob.glob(text+'*')+[None])[state]


def enter_input_filename():
    """Allows to enter the input filename and checks if it is readable"""
    # Set readline parameters
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind('tab: complete')
    readline.set_completer(tab_complete)
    # Enter the input filename; check if the file is readable
    filename = input('\n Enter the input file name: ')
    filename = os.path.realpath(filename)
    try:
        with io.open(filename, 'r'):
            return filename
    except IOError:
        input('Wrong filename or file not readable!')
        return ''


def enter_output_filename():
    """Allows user to enter output filename (without checking if readable)"""
    # Set readline parameters
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind('tab: complete')
    readline.set_completer(tab_complete)
    # Enter the output filename; no check here
    filename = input('\n Enter the output file name: ')
    filename = os.path.realpath(filename)
    return filename


def hold_on_exit():
    """Waits for user to press return before going back to menu"""
    input('Press [Enter] to return to main menu...')


def simple_menu(message, options):
    """Simple menu:

    A simple menu where user is asked what to do.
    Wrong choice points back to the menu.

    Message: string displayed on screen;
    options: a list or tuple of strings - options.
    """
    ans = ''
    while ans.upper() not in options and ans.lower() not in options:
        ans = input(message)
    return ans


def exit_program():
    """Exit program:

    All objects call this method whenever they want to exit program.
    This is because we may do something specific in different UIs,
    so an abstraction layer may come in handy.
    """
    print('Goodbye!')
    exit()
