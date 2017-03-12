# -*- coding: utf-8 -*-
"""Command-line interface functions for rpi2caster"""

# IMPORTS for text user interface
import io
import os
import readline
import glob
import click
from . import exceptions as e

# Whether the debug mode is on (can be changed by setting module's attribute)
DEBUG_MODE = False
# Some standard prompts
MSG_MENU = '[Enter] to go back to main menu...'
MSG_CONTINUE = '[Enter] to continue...'


class FormattedText(object):
    """Formatted text for displaying diecase layouts etc."""
    def __init__(self, text, **kwargs):
        self.text = text
        self.formatted_text = click.style(text, **kwargs)

    def __str__(self):
        return self.formatted_text

    def __repr__(self):
        return self.formatted_text

    def __len__(self):
        return len(self.text)

    def ljust(self, length):
        """Left-justify"""
        return self.formatted_text + ' ' * (length - len(self.text))

    def rjust(self, length):
        """Right-justify"""
        return ' ' * (length - len(self.text)) + self.formatted_text

    def center(self, length):
        """Center"""
        text_length = len(self.text)
        chunk = self.formatted_text
        while text_length < length:
            chunk = ' %s ' % chunk
            text_length += 2
        if text_length > length:
            return chunk[1:]
        else:
            return chunk


class Abort(Exception):
    """Exception - abort the current action"""
    pass


class Finish(Exception):
    """Exception - finish the current exit to menu etc."""
    pass


def abort(*_):
    """Raise the Abort exception"""
    raise Abort


def finish(*_):
    """Raise the Finish exception"""
    raise Finish


def menu(options, header='', footer='', no_debug=False):
    """menu(options=[(name1, long1, func1), (name2, long2, func2)...],
                    header=foo,
                    footer=bar,
                    no_debug=False):

    A menu which takes four arguments:
    options list - contains tuples for each option:
        (description, long_description, function)
    header - string to be displayed above,
    footer - string to be displayed below,
    no_debug - True if we don't want to tell the user
        that the program is in debugging mode.

    After choice is made, return the command.

    Set up vars for conditional statements,
    and lists for appending new items.

    choices - options to be entered by user
    """
    # Clear the screen, display header and add two empty lines
    clear()
    if header:
        print(header, end='\n\n')
    # Get the first option - this will be listed last
    try:
        (zero_function, zero_desc, zero_long_desc) = options[0]
        functions = [zero_function]
    except IndexError:
        raise e.MenuLevelUp
    # Display all the options
    # Tab indent, option number, option name (not processing option 0 yet!)
    for i, (function, desc, long_desc) in enumerate(options):
        if i > 0:
            functions.append(function)
            if long_desc:
                long_desc = '\n\t\t %s ' % long_desc
            print('\t %i : %s%s\n' % (i, desc, long_desc))
    # Option 0 is displayed last, add some whitespace around it
    if zero_desc:
        print('\n\t %i : %s \n\t\t %s \n' % (0, zero_desc, zero_long_desc))
    # Print footer, if defined
    if footer:
        print(footer, end='\n\n')
    if DEBUG_MODE and not no_debug:
        print('The program is now in debugging mode!', end='\n\n')
    # Add an empty line to separate prompt
    print('\n')
    # Ask for user input
    choice_number = -1
    # Get only available options and exclude non-numeric strings
    while choice_number not in range(len(options)):
        # Wait until user enters proper data
        your_choice = input('Your choice: ')
        try:
            choice_number = int(your_choice)
        except ValueError:
            # Entered anything non-digit - repeat
            your_choice = ''
    # At last, we have chosen a valid option...
    # Return a corresponding value - which is option
    return functions[choice_number]


def clear():
    """Clears the screen by click.clear() which is OS independent."""
    click.clear()


def display(*args, **kwargs):
    """Displays info for the user - print all in one line"""
    print(*args, **kwargs)


def display_header(text, symbol='-'):
    """Displays a header banner"""
    dash_line = symbol * len(text)
    print('\n' + dash_line + '\n' + text + '\n' + dash_line + '\n')


def display_parameters(data):
    """Displays the parameters by section (given as a dictionary):
    {header1: [(param1_val1, param1_desc1), (param1_val2, param1_desc2)...],
     header2: [(param2_val1, param2_desc1), (param2_val2, param2_desc2)...]...}
     a section will be displayed if there are parameters to display;
     a parameter will be displayed if its value evaluates to True."""
    # {header: [(par1, desc1), (par2, desc2)], header2: [(...)]}
    for key in data:
        parameters = '\n'.join(['%s: %s' % (desc, value)
                                for (value, desc) in data[key] if value])
        if parameters:
            display_header(key)
            print(parameters)


def debug_info(*args, **kwargs):
    """Prints debug messages to screen if in debug mode"""
    if DEBUG_MODE:
        print('DEBUG: ', *args, **kwargs)


def debug_enter_data(prompt, datatype=str):
    """For debug-specific data"""
    if DEBUG_MODE:
        return enter_data('DEBUG: ' + prompt + ' : ', datatype)


def debug_pause(msg1='', msg2=MSG_CONTINUE):
    """For debug confirmations"""
    if DEBUG_MODE:
        input('DEBUG: ' + msg1 + ' - ' + msg2)
        print('\n')


def pause(msg1='', msg2=MSG_CONTINUE):
    """Waits until user presses return"""
    input(msg1 + '\n' + msg2)
    print('\n')


def edit(text=''):
    """Use click to call a text editor for editing a text"""
    try:
        edited_text = click.edit(text, editor='nano -t', require_save=False)
    except click.ClickException:
        edited_text = click.edit(text, require_save=False)
    return edited_text


def enter_data(prompt, datatype=str):
    """Enter a value and convert it to the specific datatype"""
    value = ''
    while not value:
        value = input(prompt + ' : ')
        print()
        try:
            value = datatype(value)
        except ValueError:
            print('Incorrect value or data type!')
            value = ''
    return value


def enter_data_or_blank(prompt, datatype=str):
    """Enter a value or leave blank, try to convert to the specified datatype
    """
    while True:
        value = input(prompt + ' : ')
        print()
        if not value and datatype in (int, float, bool):
            return datatype(0)
        elif not value:
            return value
        try:
            return datatype(value)
        except ValueError:
            print('Incorrect value or data type!')


def enter_data_or_default(prompt, default=1, datatype=str, def_word='default'):
    """Enter a value and return default if not given anything,
    or try to convert to the specified datatype."""
    while True:
        value = input(prompt + ' (%s: %s) : ' % (def_word, default))
        print()
        if not value:
            return default
        try:
            return datatype(value)
        except ValueError:
            print('Incorrect value or data type!')


def enter_data_or_exception(prompt, exception=Abort, datatype=str):
    """Enter a value and raise an exception if it is blank,
    or try to convert to the specified datatype."""
    while True:
        value = input(prompt + ' : ')
        print()
        if not value:
            raise exception
        try:
            return datatype(value)
        except ValueError:
            print('Incorrect value or data type!')


def tab_complete(text, state):
    """Enables tab key auto-completion when you enter the filename."""
    return (glob.glob(text+'*')+[None])[state]


def import_file(filename=''):
    """Allows to enter the input filename and checks if it is readable.
    Repeats until proper filename or nothing is given.
    Returns a file object.
    Raises ReturnToMenu if filename not specified."""
    # Set readline parameters
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind('tab: complete')
    readline.set_completer(tab_complete)
    # Enter the input filename; check if the file is readable
    while True:
        if filename:
            prompt = 'Enter the input file name'
            filename = enter_data_or_default(prompt, filename)
        else:
            prompt = 'Enter the input file name (leave blank to abort)'
            filename = enter_data_or_exception(prompt)
        filename = os.path.realpath(filename)
        try:
            return io.open(filename, 'r')
        except (IOError, FileNotFoundError):
            print('Wrong filename or file not readable!\n')
        except (EOFError, KeyboardInterrupt):
            raise Abort


def export_file(filename=''):
    """Allows user to enter output filename (without checking if readable).
    Returns a file object.
    Raises ReturnToMenu if filename not specified."""
    # Set readline parameters
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind('tab: complete')
    readline.set_completer(tab_complete)
    # Enter the output filename; no check here
    try:
        if filename:
            prompt = 'Enter the file name to export'
            filename = enter_data_or_default(prompt, filename)
        else:
            prompt = 'Enter the file name to export (leave blank to abort)'
            filename = enter_data_or_exception(prompt)
        return io.open(os.path.realpath(filename), 'w+')
    except (EOFError, KeyboardInterrupt):
        raise Abort


def simple_menu(message, options):
    """A simple menu where user is asked what to do.
    Wrong choice points back to the menu.

    Message: prompt - string displayed on screen;
    options: a dict {ans1:opt1, ans2:opt2...}.
    """
    ans = ''
    while True:
        ans = input(message)
        print('\n')
        if ans in options:
            return options[ans]
        elif ans.lower() in options:
            return options[ans.lower()]
        elif ans.upper() in options:
            return options[ans.upper()]


def confirm(question, default=None):
    """Asks a simple question with yes or no answers.
    Returns True for yes and False for no."""
    options = {'Y': True, 'N': False}
    def_string = ''
    if default is True or default is False:
        options[''] = default
        def_string = ', default: %s' % ('Y' if default is True else 'N')
    return simple_menu('%s [Y / N%s]: ' % (question, def_string), options)
