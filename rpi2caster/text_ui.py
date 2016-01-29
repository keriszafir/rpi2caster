# -*- coding: utf-8 -*-
"""
user-interfaces

This module contains user interfaces to be used by rpi2caster suite.
"""

# IMPORTS for text user interface
import io
import os
import readline
import glob
from rpi2caster import exceptions
from rpi2caster import constants

# Whether the debug mode is on (can be changed by setting module's attribute)
DEBUG_MODE = False
# Style modifiers for displaying bold, italic, smallcaps, inferior, superior
STYLE_MODIFIERS = {'roman': ' ',
                   'bold': '*',
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
        (zero_desc, zero_long_desc, zero_function) = options[0]
    except IndexError:
        raise exceptions.ExitProgram
    functions = [zero_function]
    # Display all the options
    opts = [(i, desc, long_desc, function)
            for i, (desc, long_desc, function) in enumerate(options) if i]
    # Menu body
    # Tab indent, option number, option name (not processing option 0 yet!)
    for (i, desc, long_desc, function) in opts:
        functions.append(function)
        print('\t %i : %s \n\t\t %s \n' % (i, desc, long_desc))
    # Option 0 is displayed last, add some whitespace around it
    try:
        print('\n\t %i : %s \n\t\t %s \n' % (0, zero_desc, zero_long_desc))
    except KeyError:
        # Theoretically, there's always an option number zero... but if not?
        pass
    # Print footer, if defined
    if footer:
        print(footer, end='\n\n')
    if DEBUG_MODE and not no_debug:
        print('The program is now in debugging mode!', end='\n\n')
    # Add an empty line to separate prompt
    print('\n')
    # Ask for user input
    your_choice = ''
    while your_choice not in range(len(options)):
        # Wait until user enters proper data
        your_choice = input('Your choice: ')
        try:
            your_choice = int(your_choice)
        except ValueError:
            # Entered anything non-digit - repeat
            your_choice = ''
    # At last, we have chosen a valid option...
    # Return a corresponding value - which is option[2]
    return functions[your_choice]


def clear():
    """Clears the screen"""
    os.system('clear')


def display(*args, **kwargs):
    """Displays info for the user - print all in one line"""
    print(*args, **kwargs)


def debug_info(*args, **kwargs):
    """Prints debug messages to screen if in debug mode"""
    if DEBUG_MODE:
        print(*args, **kwargs)


def debug_enter_data(prompt):
    """For debug-specific data"""
    if DEBUG_MODE:
        return input(prompt)


def debug_confirm(msg1='', msg2=MSG_CONTINUE):
    """For debug confirmations"""
    if DEBUG_MODE:
        input(msg1 + '\n' + msg2)


def confirm(msg1='', msg2=MSG_CONTINUE):
    """Waits until user presses return"""
    input(msg1 + '\n' + msg2)


def enter_data_or_blank(prompt):
    """Enter data or leave blank"""
    return input(prompt)


def enter_data(prompt):
    """Let the user enter the data - blank not allowed"""
    value = ''
    while not value:
        value = input(prompt)
    return value


def enter_data_spec_type(prompt, datatype):
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


def enter_data_spec_type_or_blank(prompt, datatype):
    """enter_data_spec_type_or_blank:

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
    try:
        starting_sequence = '\033[' + str(style_codes[style]) + 'm'
    except KeyError:
        starting_sequence = closing_sequence
    character = starting_sequence + character + closing_sequence
    print(character)
    return character


def format_display(character, style):
    """This is a placeholder to be used until Python bug 24574 is fixed"""
    try:
        return STYLE_MODIFIERS[style] + character
    except KeyError:
        return character


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
        filename = (enter_data_or_blank('\nEnter the input file name '
                                        '(leave blank to return to menu): ') or
                    exceptions.return_to_menu())
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
    filename = (enter_data_or_blank('\n Enter the input file name '
                                    '(leave blank to return to menu): ') or
                exceptions.return_to_menu())
    filename = os.path.realpath(filename)
    return filename


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


def yes_or_no(question):
    """yes_or_no

    Asks a simple question with yes or no answers.
    Returns True for yes and False for no.
    """
    return simple_menu('%s [Y / N]: ' % question, {'Y': True, 'N': False})


def display_diecase_layout(diecase_layout, unit_arrangement=None):
    """display_diecase_layout:

    Shows a layout for a given diecase ID.
    Allows to specify a stopbar/wedge unit arrangement for this diecase,
    or uses the typical S5 if not specified.
    """
    # Define subroutines
    def process_matrix(mat):
        """Modifies matrix for displaying"""
        # Mat is defined as (char, (style1, style2...), column, row, units)
        (character, styles, column, row, units) = mat
        # Display different spaces as symbols
        spaces_symbols = {'_': '▣', ' ': '□', '': ' '}
        # Low space
        if character in spaces_symbols:
            character = spaces_symbols[character]
        # Otherwise we have a character - modify how it's displayed
        # based on style(s)
        else:
            try:
                for style in styles:
                    character = format_display(character, style)
            except (IndexError, KeyError):
                pass
        # Add column and row to sets
        cols_set.add(column)
        rows_set.add(row)
        # Finish
        return (character, styles, column, row, units)

    # Do we have a layout at all?
    if not diecase_layout:
        print('No layout to display!')
        return False
    # Initialize columns and rows sets
    cols_set = rows_set = set()
    # We have a layout, we can go further... get the wedge to display
    # row unit values next to the layout table
    # Safeguard against an empty unit arrangement: use S5 unit arrangement
    unit_arrangement = unit_arrangement or constants.S5
    # Build a list of all characters
    all_mats = [process_matrix(mat) for mat in diecase_layout]
    # Build rows and columns to iterate over
    cols_17 = 'NI' in cols_set or 'NL' in cols_set
    rows_16 = 16 in rows_set
    column_numbers = cols_17 and constants.COLUMNS_17 or constants.COLUMNS_15
    row_numbers = [x for x in range(1, rows_16 and 17 or 16)]
    # Arrange matrices for displaying
    # Generate a header with column numbers
    header = ['|Row|']
    header.extend([col.center(4) for col in column_numbers])
    header.append('|Units|Shift|')
    header = ''.join(header)
    # "-----" line in the table
    separator = '—' * len(header)
    # A row with only spaces and vertical lines in it
    empty_row = ('|' + ' ' * 3 + '|' +
                 ' ' * 4 * len(column_numbers) + '|' +
                 ' ' * 5 + '|' + ' ' * 5 + '|')
    # Initialize the displayed layout
    displayed_layout = [separator, header, separator, empty_row]
    # Process each row
    for row_number in row_numbers:
        # Get unit width value of the wedge for this row
        units = unit_arrangement[row_number] or ''
        shifted_units = unit_arrangement[row_number-1] or ''
        # Start with row number...
        row = ['|' + str(row_number).center(3) + '|']
        # Add only characters and styles, center chars to 4
        row.extend([mat[0].center(4)
                    for column_number in column_numbers for mat in all_mats
                    if mat[2] == column_number and mat[3] == row_number])
        row.append('|' + str(units).center(5) + '|')
        row.append(str(shifted_units).center(5) + '|')
        row = ''.join(row)
        displayed_layout.append(row)
        displayed_layout.append(empty_row)
    # Add the header at the bottom
    displayed_layout.extend([separator, header, separator])
    # We can display it now
    for row in displayed_layout:
        print(row)
    # Explanation of symbols
    print('\nExplanation:', '□ = low space, ▣ = high space',
          '*a = bold, /a = italic, #a = small caps',
          '_a = subscript (inferior), ^a = superscript (superior)',
          sep='\n', end='\n\n')


def edit_diecase_layout(layout, unit_arrangement=None):
    """edit_diecase_layout(layout, unit_arrangement):

    Edits a matrix case layout, row by row, matrix by matrix. Allows to enter
    a position to be edited.
    """
    def get_matrix(column, row):
        """Gets matrix data for given coordinates."""
        mat = [m for m in layout if column == m[2] and row == m[3]][0]
        return mat

    def display_matrix_details(mat):
        """Displays details for a given mat"""
        (char, styles, column, row, units) = mat
        print('\nDetails for matrix at %s%s:' % (column, row))
        print('Character: %s' % char)
        print('Styles: %s' % ', '.join([style for style in styles]))
        print('Unit width: %s' % units)
        print()

    def change_parameters(mat):
        """Edits a single mat in the diecase. Returns matrix description."""
        (char, styles, column, row, units) = mat
        # Edit it?
        print('Enter character: " " for low space (typical), "_" for '
              'high space (less common), leave empty to exit...')
        char = (enter_data_spec_type_or_blank('Character?: ', str) or
                exceptions.menu_level_up())
        available_styles = {'r': 'roman', 'b': 'bold',
                            'i': 'italic', 's': 'smallcaps',
                            'l': 'subscript', 'u': 'superscript'}
        print('Assign all text styles this matrix will be used for. '
              'More than one style is OK - e.g. roman and small caps.\n'
              'Available styles: [r]oman, [b]old, [i]talic, [s]mall caps,\n'
              '[l]ower index (a.k.a. subscript, inferior), '
              '[u]pper index (a.k.a. superscript, superior).\n'
              'Leave blank for roman only.')
        styles = enter_data_spec_type_or_blank('Styles?: ', str) or 'r'
        styles = [available_styles[char] for char in styles
                  if char in available_styles]
        print('How many units for this character? '
              'Leave blank for normal wedge step value')
        units = enter_data_spec_type_or_blank('Units?: ', int) or 0
        # Matrix is defined, return the data
        return [char, styles, column, row, units]

    def save_matrix(mat):
        """Updates the diecase layout with the new matrix data"""
        (_, _, column, row, _) = mat
        # Get current matrix data
        old_mat = get_matrix(column, row)
        mat_id = layout.index(old_mat)
        if yes_or_no('Save the matrix in layout?'):
            layout[mat_id] = mat

    def edit_matrix(mat):
        """Displays a matrix layout, asks for confirmation, edits the mat"""
        prompt = ('Edit this matrix: [Y]es / [N]o / '
                  '[F]inish editing? ')
        options = {'Y': True, 'N': False, 'F': 'exit'}
        # Display, ask, edit, save - or do nothing
        display_matrix_details(mat)
        decision = simple_menu(prompt, options)
        if decision == 'exit':
            exceptions.menu_level_up()
        elif decision:
            # Edit the mat
            try:
                mat = change_parameters(mat)
                save_matrix(mat)
            except exceptions.MenuLevelUp:
                pass

    def single_cell_mode():
        """Allows to specify a cell by its coordinates and edit it."""
        col_prompt = 'Column [NI, NL, A...O] or [Enter] to exit]? :'
        while True:
            try:
                column = ''
                row = 0
                while column not in constants.COLUMNS_17:
                    column = enter_data_spec_type_or_blank(col_prompt, str)
                    column = column.upper() or exceptions.menu_level_up()
                while row not in range(1, 17):
                    row = enter_data_spec_type('Row (1 - 16)?: ', int)
                mat = get_matrix(column, row)
                edit_matrix(mat)
            except exceptions.MenuLevelUp:
                break

    def all_rows_mode():
        """Row-by-row editing - all cells in row 1, then 2 etc."""
        try:
            for mat in layout:
                edit_matrix(mat)
        except exceptions.MenuLevelUp:
            pass

    def all_columns_mode():
        """Column-by-column editing - all cells in column NI, NL, A...O"""
        # Rearrange the layout so that it's read column by column
        transposed_layout = [mat
                             for col in constants.COLUMNS_17 for mat in layout
                             if mat[2] == col]
        try:
            for mat in transposed_layout:
                edit_matrix(mat)
        except exceptions.MenuLevelUp:
            pass

    def single_row_mode():
        """Edits matrices found in a single row"""
        while True:
            try:
                row = 0
                while row not in range(1, 17):
                    row = enter_data_spec_type_or_blank('Row (1 - 16)?: ', int)
                    row = row or exceptions.menu_level_up()
                workset = [mat for mat in layout if mat[3] == row]
                for mat in workset:
                    edit_matrix(mat)
            except exceptions.MenuLevelUp:
                break

    def single_column_mode():
        """Edits matrices found in a single column"""
        col_prompt = 'Column [NI, NL, A...O] or [Enter] to exit]? :'
        while True:
            try:
                column = ''
                while column not in constants.COLUMNS_17:
                    column = enter_data_spec_type_or_blank(col_prompt, str)
                    column = column.upper() or exceptions.menu_level_up()
                workset = [mat for mat in layout if mat[2] == column]
                for mat in workset:
                    edit_matrix(mat)
            except exceptions.MenuLevelUp:
                break
    # Map unit values to rows
    # Safeguard against an empty unit arrangement: use S5 unit arrangement
    unit_arrangement = unit_arrangement or constants.S5
    # If the layout is empty, we need to initialize it
    print('\nCurrent diecase layout:\n')
    display_diecase_layout(layout, unit_arrangement)
    prompt = ('\nChoose edit mode or press [Enter] to quit:\n'
              'AR - all matrices row by row,\n'
              'AC - all matrices column by column,\n'
              'M - single matrix by coordinates,\n'
              'R - all matrices in a specified row,\n'
              'C - all matrices in a specified column.'
              '\nYour choice:')
    options = {'AR': all_rows_mode,
               'AC': all_columns_mode,
               'M': single_cell_mode,
               'R': single_row_mode,
               'C': single_column_mode,
               '': exceptions.menu_level_up}
    while True:
        try:
            simple_menu(prompt, options)()
        except exceptions.MenuLevelUp:
            break
    # After editing, pass the layout to whatever called this function
    return layout


def exit_program():
    """Exit program:

    All objects call this method whenever they want to exit program.
    This is because we may do something specific in different UIs,
    so an abstraction layer may come in handy.
    """
    print('\n\nGoodbye!\n')
    exit()
