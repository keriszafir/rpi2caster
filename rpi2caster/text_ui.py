# -*- coding: utf-8 -*-
"""Command-line interface functions for rpi2caster"""

# IMPORTS for text user interface
import io
import os
import readline
import glob

from . import exceptions as e
from . import constants as c

# Whether the debug mode is on (can be changed by setting module's attribute)
DEBUG_MODE = False
# Style modifiers for displaying bold, italic, smallcaps, inferior, superior
STYLE_MODIFIERS = {'bold': '*',
                   'italic': '/',
                   'smallcaps': '#',
                   'subscript': '_',
                   'superscript': '^'}
# Some standard prompts
MSG_MENU = '[Enter] to go back to main menu...'
MSG_CONTINUE = '[Enter] to continue...'


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
        raise e.ExitProgram
    # Display all the options
    # Tab indent, option number, option name (not processing option 0 yet!)
    for i, (function, desc, long_desc) in enumerate(options):
        if i > 0:
            functions.append(function)
            print('\t %i : %s \n\t\t %s \n' % (i, desc, long_desc))
    # Option 0 is displayed last, add some whitespace around it
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
    """Clears the screen"""
    os.system('clear')


def display(*args, **kwargs):
    """Displays info for the user - print all in one line"""
    print(*args, **kwargs)


def display_header(text, symbol='-'):
    """Displays a header banner"""
    dash_line = symbol * len(text)
    print('\n\n' + dash_line + '\n' + text + '\n' + dash_line + '\n')


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


def debug_enter_data(prompt):
    """For debug-specific data"""
    if DEBUG_MODE:
        return input('DEBUG: ' + prompt)


def debug_pause(msg1='', msg2=MSG_CONTINUE):
    """For debug confirmations"""
    if DEBUG_MODE:
        input('DEBUG: ' + msg1 + ' - ' + msg2)


def pause(msg1='', msg2=MSG_CONTINUE):
    """Waits until user presses return"""
    input(msg1 + '\n' + msg2)


def enter_data(prompt, datatype=str):
    """Enter a value and convert it to the specific datatype"""
    value = ''
    while not value:
        value = input(prompt)
        try:
            value = datatype(value)
        except ValueError:
            print('Incorrect value or data type!')
            value = ''
    return value


def enter_data_or_blank(prompt, datatype=str):
    """enter_data_or_blank:

    Enter a value or leave blank, try to convert to the specified datatype
    """
    while True:
        value = input(prompt)
        if not value:
            return value
        try:
            return datatype(value)
        except ValueError:
            print('Incorrect value or data type!')


def _format_display(character, style):
    """format_display:

    Uses ANSI escape sequences to alter the appearance of the character
    displayed in the matrix case layout.

    Temporarily unused - until bugfix for 24574.
    """
    style_codes = {'roman': 0,
                   'bold': 1,
                   'italic': 33,
                   'smallcaps': 34,
                   'subscript': 35,
                   'superscript': 36}
    closing_sequence = '\033[0m'
    starting_sequence = '\033[' + str(style_codes.get(style, 0)) + 'm'
    character = starting_sequence + character + closing_sequence
    print(character)
    return character


def format_display(character, style):
    """This is a placeholder to be used until Python bug 24574 is fixed"""
    return STYLE_MODIFIERS.get(style, '') + character


def choose_one_style():
    """Chooses one style from available ones"""
    print('Choose a text style. Leave blank for roman.'
          'Available options: [r]oman, [b]old, [i]talic, [s]mall caps,\n'
          '[l]ower index (a.k.a. subscript, inferior), '
          '[u]pper index (a.k.a. superscript, superior).')
    style = enter_data_or_blank('Style?: ', str) or 'r'
    return c.STYLES.get(style, 'roman')


def choose_styles():
    """Chooses one or more styles and returns a list of them"""
    print('Choose one or more text styles, e.g. roman and small caps.\n'
          'Available options: [r]oman, [b]old, [i]talic, [s]mall caps,\n'
          '[l]ower index (a.k.a. subscript, inferior), '
          '[u]pper index (a.k.a. superscript, superior).\n'
          'Leave blank for roman only.')
    styles_string = enter_data_or_blank('Styles?: ', str) or 'r'
    return list({c.STYLES[char] for char in styles_string if char in c.STYLES})


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
    while True:
        prompt = '\nEnter the input file name (leave blank to abort): '
        filename = enter_data_or_blank(prompt)
        if not filename:
            return False
        filename = os.path.realpath(filename)
        try:
            with io.open(filename, 'r'):
                return filename
        except (IOError, FileNotFoundError):
            print('Wrong filename or file not readable!\n')


def enter_output_filename():
    """Allows user to enter output filename (without checking if readable)"""
    # Set readline parameters
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind('tab: complete')
    readline.set_completer(tab_complete)
    # Enter the output filename; no check here
    prompt = '\nEnter the input file name (leave blank to abort): '
    filename = enter_data_or_blank(prompt)
    if filename:
        return os.path.realpath(filename)
    else:
        return False


def simple_menu(message, options):
    """Simple menu:

    A simple menu where user is asked what to do.
    Wrong choice points back to the menu.

    Message: prompt - string displayed on screen;
    options: a dict {ans1:opt1, ans2:opt2...}.
    """
    ans = ''
    while True:
        ans = input(message)
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
        def_string = ', default: %s' % (default and 'Y' or 'N')
    return simple_menu('%s [Y / N%s]: ' % (question, def_string), options)


def display_diecase_layout(diecase):
    """Shows a layout for a given diecase ID, unit values for its
    assigned wedge, or the typical S5 if not specified."""
    def displayed_char(matrix):
        """Modifies matrix char for displaying"""
        spaces_symbols = {'_': '▣', ' ': '□', '': ' '}
        formatted_char = matrix.char
        for style in matrix.styles:
            formatted_char = format_display(formatted_char, style)
        return spaces_symbols.get(matrix.char, formatted_char)

    def row_units(row):
        """Gets wedge unit value for the row"""
        return str(diecase.wedge.units[row])

    matrices = [mat for mat in diecase]
    cols_set = {matrix.column for matrix in matrices}
    rows_set = {matrix.row for matrix in matrices}
    col_numbers = ((16 in rows_set or 'NI' in cols_set or 'NL' in cols_set) and
                   c.COLUMNS_17 or c.COLUMNS_15)
    # If row 16 found - generate 16 rows; else 15
    row_numbers = [x for x in range(1, 16 in rows_set and 17 or 16)]
    # Generate a header with column numbers
    header = ('|Row|' + ''.join([col.center(4) for col in col_numbers]) +
              '|' + 'Units'.center(7) + '|')
    # "-----" line in the table
    separator = '—' * len(header)
    # A row with only spaces and vertical lines in it
    empty_row = ('|' + ' ' * 3 + '|' + ' ' * 4 * len(col_numbers) + '|' +
                 ' ' * 7 + '|')
    # Initialize the displayed layout
    table = [separator, header, separator, empty_row]
    # Process each row
    for row_num in row_numbers:
        # Start with row number...
        row = ['|' + str(row_num).center(3) + '|']
        # Add only characters and styles, center chars to 4
        row.extend([displayed_char(mat).center(4)
                    for column_num in col_numbers for mat in matrices
                    if mat.column == column_num and mat.row == row_num])
        table.append(''.join(row) + '|' + row_units(row_num).center(7) + '|')
        table.append(empty_row)
    # Add the header at the bottom
    table.extend([separator, header, separator])
    # We can display it now
    print('\nDiecase ID: %s' % diecase)
    print('Stopbar / wedge: %s\n' % diecase.wedge)
    for row in table:
        print(row)
    # Explanation of symbols
    print('\nExplanation:', '□ = low space, ▣ = high space',
          '*a = bold, /a = italic, #a = small caps',
          '_a = subscript (inferior), ^a = superscript (superior)',
          sep='\n', end='\n\n')


def edit_matrix(matrix):
    """Edits the matrix data"""
    display_parameters({'Matrix details': matrix.parameters})
    prompt = ('Character (" "=low space, "_"=high space, '
              'blank to leave unchanged, ctrl-C to exit) ? : ')
    matrix.char = enter_data_or_blank(prompt) or matrix.char
    if not matrix.char:
        return matrix
    matrix.styles = choose_styles()
    units = matrix.units or matrix.row_units()
    prompt = 'Unit width? (current: %s) : ' % units
    matrix.units = enter_data_or_blank(prompt, int) or units
    return matrix


def edit_diecase_layout(diecase):
    """Edits a matrix case layout, row by row, matrix by matrix.
    Allows to enter a position to be edited. """
    def all_rows_mode():
        """Row-by-row editing - all cells in row 1, then 2 etc."""
        for mat in diecase:
            edit_matrix(mat)

    def all_columns_mode():
        """Column-by-column editing - all cells in column NI, NL, A...O"""
        # Rearrange the layout so that it's read column by column
        iter_mats = (mat for col in c.COLUMNS_17
                     for mat in diecase if mat.column == col)
        for mat in iter_mats:
            edit_matrix(mat)

    def single_row_mode(row):
        """Edits matrices found in a single row"""
        iter_mats = (mat for mat in diecase if mat.row == row)
        for mat in iter_mats:
            edit_matrix(mat)

    def single_column_mode(column):
        """Edits matrices found in a single column"""
        iter_mats = (mat for mat in diecase if mat.column == column)
        for mat in iter_mats:
            edit_matrix(mat)

    # Map unit values to rows
    # If the layout is empty, we need to initialize it
    prompt = ('Enter row number to edit all mats in a row,\n'
              'column number to edit all mats in a column,\n'
              'matrix coordinates to edit a single matrix,\n'
              'or choose edit mode: AR - all matrices row by row, '
              'AC - all matrices column by column.'
              '\nYour choice (or leave blank to exit) : ')
    while True:
        print('\nCurrent diecase layout:\n')
        display_diecase_layout(diecase)
        try:
            ans = input(prompt).upper()
            if ans == 'AR':
                all_rows_mode()
            elif ans == 'AC':
                all_columns_mode()
            elif ans in c.COLUMNS_17:
                single_column_mode(ans)
            elif ans in [str(x) for x in range(1, 17)]:
                single_row_mode(int(ans))
            elif ans:
                mat = diecase.decode_matrix(ans)
                edit_matrix(mat)
            else:
                return diecase.matrices
        except (IndexError, KeyboardInterrupt, TypeError, AttributeError):
            pass


def enter_line_length():
    """Enter the line length, choose measurement units
    (for e.g. British or European measurement system). Return length in
    12-set units e.g. the standard Monotype measure."""
    prompt = ('Enter the desired line length and measurement unit:\nb'
              'c - cicero (.1776"), p - pica (.166"), dtp - DTP pica (.1667"),'
              '\n", in - inch, mm - millimeter, cm - centimeter?\n'
              '(default: c) : ')
    factor = 1.0
    # We need an ordered sequence here
    symbols = ['dtp', 'p', 'cm', 'c', 'mm', 'in', '"', '']
    units = {'dtp': 0.1667, 'p': 0.166, 'cm': 0.3937, 'mm': 0.03937,
             'c': 0.1776, '"': 1, 'in': 1, '': 0.1776}
    while True:
        raw_string = input(prompt).lower()
        try:
            for symbol in symbols:
                # Get the units
                if raw_string.endswith(symbol):
                    factor = units[symbol]
                    input_string = raw_string.replace(symbol, '')
                    input_string = input_string.strip()
                    break
            # Calculate length in inches and go on
            inches_length = float(input_string) * factor
            break
        except (TypeError, ValueError):
            print('Incorrect value - enter again...')
    # Return line length in 12-set units based on .1667" pica
    # Will be normalized in the typesetting routines
    return round(18 * 6 * inches_length)


def exit_program(*_):
    """Exit program:

    All objects call this method whenever they want to exit program.
    This is because we may do something specific in different UIs,
    so an abstraction layer may come in handy.
    """
    print('\n\nGoodbye!\n')
    exit()
