# -*- coding: utf-8 -*-
"""User interface for rpi2caster. Text UI is implemented here, additional UIs
can be added later or imported from separate modules"""
import io
import os
import readline
import glob
from contextlib import suppress
import click
from . import exceptions as e
from .misc import weakref_singleton, PubSub


def abort(*_):
    """Raise the Abort exception"""
    raise Abort


def finish(*_):
    """Raise the Finish exception"""
    raise Finish


class Abort(Exception):
    """Exception - abort the current action"""
    pass


class Finish(Exception):
    """Exception - finish the current exit to menu etc."""
    pass


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


class ClickUI(object):
    """Click-based text user interface"""
    __name__ = 'Text UI based on Click'

    def __init__(self):
        self.verbosity = 0

    def menu(self, options, header='', footer='', no_debug=False):
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
        self.clear()
        if header:
            click.echo(header + '\n\n')
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
                click.echo('\t %i : %s%s\n' % (i, desc, long_desc))
        # Option 0 is displayed last, add some whitespace around it
        if zero_desc:
            click.echo('\n\t %i : %s \n\t\t %s \n'
                       % (0, zero_desc, zero_long_desc))
        # Print footer, if defined
        if footer:
            click.echo(footer + '\n\n')
        if self.verbosity > 0 and not no_debug:
            click.echo('The program is now in debugging mode!\n\n')
        # Add an empty line to separate prompt
        click.echo('\n')
        # Ask for user input
        choice_number = -1
        # Get only available options and exclude non-numeric strings
        while choice_number not in range(len(options)):
            # Wait until user enters proper data
            choice_number = self.enter('Your choice: ', datatype=int)
        # At last, we have chosen a valid option...
        # Return a corresponding value - which is option
        return functions[choice_number]

    @staticmethod
    def clear():
        """Clears the screen by click.clear() which is OS independent."""
        click.clear()

    def display(self, *args, sep=' ', end='\n', file=None, min_verbosity=0):
        """Displays info for the user:
        args - iterable of arguments to display,
        sep : separation string (default: space),
        end : termination string (default: newline)"""
        if self.verbosity >= min_verbosity:
            display_string = sep.join(str(arg) for arg in args) + end
            click.echo(message=display_string, nl=False, file=file)

    def display_header(self, text, symbol='-'):
        """Displays a header banner"""
        dash_line = symbol * len(text)
        self.display(dash_line, text, dash_line, sep='\n', end='\n\n')

    def display_parameters(self, data):
        """Displays the parameters by section (given as a dictionary):
        {header1: [(par1_val1, par1_desc1), (par1_val2, par1_desc2)...],
         header2: [(par2_val1, par2_desc1), (par2_val2, par2_desc2)...]...}
         a section will be displayed if there are parameters to display;
         a parameter will be displayed if its value evaluates to True."""
        # {header: [(par1, desc1), (par2, desc2)], header2: [(...)]}
        for key, collection in data.items():
            parameters = '\n'.join(['%s: %s' % (desc, value)
                                    for (value, desc) in collection if value])
            if parameters:
                self.display_header(key)
                self.display(parameters)

    def pause(self, msg1='', msg2='Press any key to continue...',
              min_verbosity=0):
        """Waits until user presses a key"""
        if self.verbosity >= min_verbosity:
            click.pause(msg1 + '\n' + msg2 + '\n')

    @staticmethod
    def edit(text=''):
        """Use click to call a text editor for editing a text"""
        try:
            edited_text = click.edit(text, editor='nano -t',
                                     require_save=False)
        except click.ClickException:
            edited_text = click.edit(text, require_save=False)
        return edited_text

    @staticmethod
    def enter(prompt,
              blank_ok=False, default=None, exception=None, datatype=str):
        """Enter data based on function arguments.
        prompt :    set the custom prompt to show to the user,
        blank_ok :  if True, allows not choosing anything
                    (return '', 0 or False coerced to datatype),
        default :   default value, not choosing anything will lead to
                    returning this value, coerced to datatype,
        exception : an exception to be raised if nothing is chosen
                    (useful to escape the control flow)
        datatype :  type to coerce the input string into.

        If blank_ok is False, and no default value or exception is specified,
        the function will loop over until the user enters a value which can be
        coerced into the datatype specified.
        """

        def throw(exception):
            """raise an exception"""
            raise exception

        suffix = ' [%s] : ' % default if default is not None else ' : '
        while True:
            value = input(prompt + suffix)
            click.echo()
            if not value:
                if default is not None:
                    return datatype(default)
                elif exception:
                    throw(exception)
                elif blank_ok:
                    for cand in ('', 0, False):
                        with suppress(TypeError, ValueError):
                            return datatype(cand)
            # we now should have a value
            # accept 0 as a valid option here
            try:
                value = datatype(value)
                if value or value == 0:
                    return value
            except ValueError:
                # stay in the loop
                click.echo('Incorrect value or data type!')
                value = ''

    def import_file(self, filename=''):
        """Allows to enter the input filename and checks if it is readable.
        Repeats until proper filename or nothing is given.
        Returns a file object.
        Raises ReturnToMenu if filename not specified."""
        # Set readline parameters
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind('tab: complete')
        readline.set_completer(lambda text, state:
                               (glob.glob(text+'*')+[None])[state])
        # Enter the input filename; check if the file is readable
        while True:
            if filename:
                prompt = 'Enter the input file name'
                filename = self.enter(prompt, default=filename)
            else:
                prompt = 'Enter the input file name (leave blank to abort)'
                filename = self.enter(prompt, exception=Abort)
            filename = os.path.realpath(filename)
            try:
                return io.open(filename, 'r')
            except (IOError, FileNotFoundError):
                click.echo('Wrong filename or file not readable!\n')
            except (EOFError, KeyboardInterrupt):
                raise Abort

    def export_file(self, filename=''):
        """Allows user to enter output filename (without checking if readable).
        Returns a file object.
        Raises ReturnToMenu if filename not specified."""
        # Set readline parameters
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind('tab: complete')
        readline.set_completer(lambda text, state:
                               (glob.glob(text+'*')+[None])[state])
        # Enter the output filename; no check here
        try:
            if filename:
                prompt = 'Enter the file name to export'
                filename = self.enter(prompt, default=filename)
            else:
                prompt = 'Enter the file name to export (leave blank to abort)'
                filename = self.enter(prompt, exception=Abort)
            return io.open(os.path.realpath(filename), 'w+')
        except (EOFError, KeyboardInterrupt):
            raise Abort

    @staticmethod
    def simple_menu(message, options):
        """A simple menu where user is asked what to do.
        Wrong choice points back to the menu.

        Message: prompt - string displayed on screen;
        options: a dict {ans1:opt1, ans2:opt2...}.
        """
        while True:
            ans = click.prompt(message, default='')
            click.echo('\n')
            for key in (ans, ans.lower(), ans.upper()):
                # default to some nonsensical string for wrong dict hits
                # make it possible to have None as options
                # (https://en.wikipedia.org/wiki/Etaoin_shrdlu)
                match = options.get(key, 'etaoin shrdlu cmfwyp')
                if match is not 'etaoin shrdlu cmfwyp':
                    return match

    def confirm(self, question, default=None):
        """Asks a simple question with yes or no answers.
        Returns True for yes and False for no."""
        return click.confirm(question, default)


@weakref_singleton
class UIFactory(object):
    """UI abstraction layer"""
    implementations = {'text_ui': ClickUI,
                       'click': ClickUI}

    def __init__(self):
        PubSub().subscribe(self, 'UI')
        self.impl = ClickUI()

    def __getattr__(self, name):
        result = getattr(self.impl, name)
        if result is None:
            raise NameError('%s has no function named %s'
                            % (self.impl.__name__, name))
        else:
            return result

    def update(self, source):
        """Update the UI implementation"""
        name = source.get('impl') or source.get('implementation')
        impl = self.implementations.get(name)
        if impl:
            self.impl = impl()
