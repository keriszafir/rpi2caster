# -*- coding: utf-8 -*-
"""Command-line interface functions for rpi2caster"""

# IMPORTS for text user interface
import io
import os
import readline
import glob
import click

from . import exceptions as e
from . import constants as c

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
    return click.edit(text, require_save=False) or text


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


def enter_data_or_default(prompt, default=1, datatype=str):
    """Enter a value and return default if not given anything,
    or try to convert to the specified datatype."""
    while True:
        value = input(prompt + ' (default: %s) : ' % default)
        print()
        if not value:
            return default
        try:
            return datatype(value)
        except ValueError:
            print('Incorrect value or data type!')


def enter_data_or_exception(prompt, exception=ValueError, datatype=str):
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


def enter_input_filename():
    """Allows to enter the input filename and checks if it is readable.
    Repeats until proper filename or nothing is given.
    Raises ReturnToMenu if filename not specified."""
    # Set readline parameters
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind('tab: complete')
    readline.set_completer(tab_complete)
    # Enter the input filename; check if the file is readable
    while True:
        prompt = 'Enter the input file name (leave blank to abort)'
        filename = enter_data_or_exception(prompt, e.ReturnToMenu)
        filename = os.path.realpath(filename)
        try:
            with io.open(filename, 'r'):
                return filename
        except (IOError, FileNotFoundError):
            print('Wrong filename or file not readable!\n')


def enter_output_filename():
    """Allows user to enter output filename (without checking if readable).
    Raises ReturnToMenu if filename not specified."""
    # Set readline parameters
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind('tab: complete')
    readline.set_completer(tab_complete)
    # Enter the output filename; no check here
    prompt = 'Enter the input file name (leave blank to abort)'
    filename = enter_data_or_exception(prompt, e.ReturnToMenu)
    return os.path.realpath(filename)


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
        else:
            pass


def confirm(question, default=None):
    """Asks a simple question with yes or no answers.
    Returns True for yes and False for no."""
    options = {'Y': True, 'N': False}
    def_string = ''
    if default is True or default is False:
        options[''] = default
        def_string = ', default: %s' % ('Y' if default is True else 'N')
    return simple_menu('%s [Y / N%s]: ' % (question, def_string), options)


def display_diecase_layout(diecase):
    """Shows a layout for a given diecase ID, unit values for its
    assigned wedge, or the typical S5 if not specified."""
    def _get_char(matrix):
        """Modifies matrix char for displaying"""
        # Style modifiers for displaying roman, bold, italic,
        # smallcaps, inferior, superior
        style_modifiers = {'r': '', 'b': '*', 'i': '/',
                           's': '·', 'u': '_', 'l': '^'}
        spaces_symbols = {'_': '▣', ' ': '□', '': ' '}
        fmt = ''.join([style_modifiers.get(s, '') for s in matrix.styles])
        if len(fmt) > 2:
            fmt = '#'
        return spaces_symbols.get(matrix.char) or fmt + matrix.char

    def get_char(matrix):
        """New style formatting for diecase layouts"""
        style_modifiers = {'r': dict(fg=None),
                           'b': dict(bold=True),
                           'i': dict(fg='cyan'),
                           's': dict(underline=True),
                           'u': dict(fg='blue'),
                           'l': dict(fg='magenta')}
        spaces_symbols = {'_': FormattedText('▣', fg='red'),
                          ' ': FormattedText('□', fg='red'),
                          '': FormattedText(' ')}
        style_options = {'fg': None}
        for style in matrix.styles:
            style_options.update(style_modifiers.get(style))
        return (spaces_symbols.get(matrix.char) or
                FormattedText(matrix.char, **style_options))

    def get_width(column):
        """Get the column width"""
        return column_widths.get(column, 4)

    def get_mat_unit_value(mat):
        """Get the unit value string for a character, if the width
        overrides the wedge default"""
        show_units = (mat.units != wedge_row_units and
                      mat.char and not mat.is_space)
        if show_units:
            return str(mat.units)
        else:
            return ''

    col_numbers = c.COLUMNS_15
    row_numbers = [x for x in range(1, 16)]
    # Set the initial column width value to 4
    column_widths = {}
    # Now loop over the matrices and adjust the displayed table
    for mat in diecase:
        if '16' in mat.code:
            col_numbers = c.COLUMNS_17
            row_numbers = [x for x in range(1, 17)]
            break
        elif mat.column in ('NI', 'NL'):
            col_numbers = c.COLUMNS_17
        # Update column width if displayed character turns out too long
        if len(get_char(mat)) + 2 > column_widths.get(mat.column, 4):
            column_widths[mat.column] = len(get_char(mat)) + 2
    # Generate a header with column numbers
    # Widths are variable and depend on text field width
    fields = [col.center(get_width(col)) for col in col_numbers]
    header = ' Row %s Units ' % ''.join(fields)
    # "-----" line in the table
    separator = '—' * len(header)
    # Initialize the displayed layout
    table = [header, separator]
    # Process each row
    for row in row_numbers:
        items = []
        units_row = []
        wedge_row_units = diecase.wedge[row]
        for col in col_numbers:
            width = get_width(col)
            for mat in diecase:
                if mat.code == '%s%s' % (col, row):
                    items.append(get_char(mat).center(width))
                    units_row.append(get_mat_unit_value(mat).center(width))
                    # No need to iterate further
                    break
        items = ['|', str(row).center(3), '|', ''.join(items),
                 '|%s|' % str(wedge_row_units).center(5)]
        units_row = ['|', ' ' * 3, '|', ''.join(units_row), '|', ' ' * 5, '|']
        table.append(''.join(items))
        table.append(''.join(units_row))
        # table.append(empty_row)
    # Add the header at the bottom
    table.extend([separator, header])
    # We can display it now
    print('\nDiecase ID: %s  -   assigned stopbar/wedge: %s\n'
          % (diecase, diecase.wedge))
    for row in table:
        print(row)
    # Explanation of symbols
    print('\nExplanation:', '□ = low space, ▣ = high space',
          '*a = bold, /a = italic, ·a = small caps',
          '_a = subscript (inferior), ^a = superscript (superior)',
          '# - matrix assigned to more than two styles', sep='\n')


def edit_diecase_layout(diecase):
    """Edits a matrix case layout, row by row, matrix by matrix.
    Allows to enter a position to be edited. """
    def swap(command):
        """Swap two matrices based on command"""
        # Process the command string (uppercase)
        command = command.replace('SWAP', '').strip()
        code1, code2 = command.split(',', 1)
        code1, code2 = code1.strip(), code2.strip()
        # Look for matrices
        matches1 = [mat for mat in diecase.matrices if mat.code == code1]
        matches2 = [mat for mat in diecase.matrices if mat.code == code2]
        if matches1 and matches2:
            mat1, mat2 = matches1[0], matches2[0]
            mat1.code, mat2.code = mat2.code, mat1.code

    def edit(mat):
        """Edit a matrix"""
        clear()
        display_diecase_layout(diecase)
        mat.edit()

    def all_rows_mode():
        """Row-by-row editing - all cells in row 1, then 2 etc."""
        for mat in diecase:
            edit(mat)

    def all_columns_mode():
        """Column-by-column editing - all cells in column NI, NL, A...O"""
        # Rearrange the layout so that it's read column by column
        iter_mats = (mat for col in c.COLUMNS_17
                     for mat in diecase if mat.column == col)
        for mat in iter_mats:
            edit(mat)

    def single_row_mode(row):
        """Edits matrices found in a single row"""
        iter_mats = (mat for mat in diecase if mat.row == row)
        for mat in iter_mats:
            edit(mat)

    def single_column_mode(column):
        """Edits matrices found in a single column"""
        iter_mats = (mat for mat in diecase if mat.column == column)
        for mat in iter_mats:
            edit(mat)

    # Map unit values to rows
    # If the layout is empty, we need to initialize it
    can_save = diecase.typeface and diecase.diecase_id
    prompt = ('Enter row number to edit all mats in a row,\n'
              'column number to edit all mats in a column,\n'
              'matrix coordinates to edit a single matrix,\n'
              'or choose edit mode: AR - all matrices row by row, '
              'AC - all matrices column by column.'
              '\nYou can swap two mats by entering: "swap coords1, coords2".'
              '%s'
              '\nYour choice (or leave blank to exit) : '
              % (can_save and '\nS to save diecase to database.' or ''))
    while True:
        print('\nCurrent diecase layout:\n')
        display_diecase_layout(diecase)
        print()
        try:
            ans = input(prompt).upper()
            if ans == 'S' and can_save:
                diecase.save_to_db()
            elif ans == 'AR':
                all_rows_mode()
            elif ans == 'AC':
                all_columns_mode()
            elif ans in c.COLUMNS_17:
                single_column_mode(ans)
            elif ans in [str(x) for x in range(1, 17)]:
                single_row_mode(int(ans))
            elif ans.startswith('SWAP'):
                swap(ans)
            elif ans:
                try:
                    mats = [mat for mat in diecase if mat.code == ans.upper()]
                    edit(mats[0])
                except (IndexError, TypeError, AttributeError):
                    # Loop over again
                    pass
            else:
                return diecase.matrices
        except (IndexError, KeyboardInterrupt, TypeError, AttributeError):
            pass
