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

# Whether the debug mode is on (can be changed by setting module's attribute)
DEBUG_MODE = False
# Style modifiers for displaying bold, italic, smallcaps, inferior, superior
STYLE_MODIFIERS = {'roman': ' ',
                   'bold': '*',
                   'italic': '/',
                   'smallcaps': '#',
                   'subscript': '_',
                   'superscript': '^'}


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
        print(header, end='\n\n')
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
        print(footer, end='\n\n')
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
    print(*args, **kwargs)


def debug_info(*args, **kwargs):
    """Prints debug messages to screen if in debug mode"""
    if DEBUG_MODE:
        print(*args, **kwargs)


def debug_enter_data(prompt):
    """For debug-specific data or confirmations"""
    if DEBUG_MODE:
        return input(prompt)


def confirm(prompt):
    """Waits until user presses return"""
    input(prompt)


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
    value = input(prompt)
    try:
        return datatype(value)
    except ValueError:
        return value


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
    def get_styles(layout):
        """Parses the diecase layout and gets available typeface styles.
        Returns a list of them."""
        try:
            return list({style for mat in layout for style in mat[1] if style})
        except TypeError:
            return []
            
    def find_unused_matrices(layout):
        """find_unused_matrices:

        Flags matrices without characters and spaces as unused, preventing them
        from being addressed during typesetting and casting.
        """
        # mat = (character, (style1, style2...), column, row, units)
        unused_mats = []
        columns_in_diecase = list({mat[2] for mat in layout})
        row_numbers = sorted({mat[3] for mat in layout})
        # Check if it is a 15-column (older) or 17-column (newer) diecase
        column_numbers = []
        if 'NI' in columns_in_diecase or 'NL' in columns_in_diecase:
            column_numbers = ['NI', 'NL']
        column_numbers.extend([x for x in 'ABCDEFGHIJKLMNO'])
        # Get all positions without a registered matrix
        for row_number in row_numbers:
            for column_number in column_numbers:
                match = [mat for mat in layout if mat[3] == row_number and
                         mat[2] == column_number]
                if not match:
                    record = [' ', ('roman',), column_number, row_number, 0]
                    unused_mats.append(record)
        return unused_mats

    # Do we have a layout at all?
    if not diecase_layout:
        print('No layout to display!')
        return False
    # We have a layout, we can go further... get the wedge to display
    # row unit values next to the layout table
    s5_arr = ('', 5, 6, 7, 8, 9, 9, 9, 10, 10, 11, 12, 13, 14, 15, 18, 18)
    # Safeguard against an empty unit arrangement: use S5 unit arrangement
    unit_arrangement = unit_arrangement or s5_arr
    # Build a list of all characters
    # We must know all matrices/positions in the diecase, even if they're not
    # defined in the original layout
    all_mats = find_unused_matrices(diecase_layout)
    for mat in diecase_layout:
        # Mat is defined as (char, (style1, style2...), column, row, units)
        (character, styles, column, row, units) = mat
        # Display different spaces as symbols
        # Low space
        if character == '_':
            character = '▣'
        # High space
        elif character == ' ':
            character = '□'
        # Empty matrix = no character, unused
        elif not character:
            character = ' '
        # Otherwise we have a character - modify how it's displayed
        # based on style(s)
        else:
            try:
                for style in styles:
                    character = format_display(character, style)
            except (IndexError, KeyError):
                pass
        # Add a record to processed matrices
        all_mats.append((character, styles, column, row, units))
    # Determine which rows have matrices
    # This will skip unfilled rows (with blanks) at the end
    # A list of integers
    row_numbers = sorted({mat[3] for mat in all_mats})
    # Build rows and columns to iterate over
    column_numbers = ('NI', 'NL') + tuple([x for x in 'ABCDEFGHIJKLMNO'])
    # Arrange matrices for displaying
    diecase_arrangement = []
    for row_number in row_numbers:
        # Add only characters and styles, center chars to 5
        row = [mat[0].center(4)
               for column_number in column_numbers for mat in all_mats
               if mat[2] == column_number and mat[3] == row_number]
        diecase_arrangement.append(row)
    # We can display it now
    header = ['|' + 'Row' + '|']
    header.extend([col.center(4) for col in column_numbers])
    header.append('|' + 'Units' + '|')
    header.append('Shift' + '|')
    header = (''.join(header))
    separator = '—' * len(header)
    empty_row = ('|' + ' ' * 3 + '|' +
                 ' ' * 4 * len(column_numbers) + '|' +
                 ' ' * 5 + '|' + ' ' * 5 + '|')
    print(separator, header, separator, empty_row, sep='\n')
    # Get a unit-width for each row to display it at the end
    for i, row in enumerate(diecase_arrangement, start=1):
        units = str(unit_arrangement[i] or '')
        shifted_units = str(unit_arrangement[i-1] or '')
        # Now we are going to show the matrices
        # First, display row number (and borders), then characters in row
        data = ['|' + str(i).center(3) + '|'] + row
        # At the end, unit-width and unit-width when using unit-shift
        data.append('|' + units.center(5) + '|')
        data.append(shifted_units.center(5) + '|')
        data_row = ''.join(data)
        # Finally, display the row and a newline
        print(data_row, empty_row, sep='\n')
    # Display header again
    print(separator, header, separator, sep='\n', end='\n\n')
    # Names of styles found in the diecase with formatting applied to them
    displayed_styles = '\n'.join([format_display(style, style)
                                  for style in get_styles(diecase_layout)])
    # Explanation of symbols
    print('Explanation:', '□ - low space', '▣ - high space',
          displayed_styles, sep='\n', end='\n')


def edit_diecase_layout(layout, unit_arrangement=None):
    """edit_diecase_layout(layout, unit_arrangement):
    
    Edits a matrix case layout, row by row, matrix by matrix. Allows to enter
    a position to be edited.
    """
    # If the layout is empty, we need to initialize it
    if not layout:
        prompt = "Matrix case size: 1 for 15x15, 2 for 15x17, 3 for 16x17? "
        options = {'1': (15, 15), '2': (15, 17), '3': (16, 17)}
        (rows_number, columns_number) = simple_menu(prompt, options)
        # Generate column numbers
        if columns_number == 17:
            columns = ['NI', 'NL']
        else:
            columns = []
        columns.extend([letter for letter in 'ABCDEFGHIJKLMNO'])
        # Generate row numbers: 1...15 or 1...16
        rows = [num + 1 for num in range(rows_number)]
        # Map unit values to rows
        s5_arr = ('', 5, 6, 7, 8, 9, 9, 9, 10, 10, 11, 12, 13, 14, 15, 18, 18)
        # Safeguard against an empty unit arrangement: use S5 unit arrangement
        unit_arrangement = unit_arrangement or s5_arr
        # Generate an empty layout with default row unit values
        layout = [('', ('roman',), column, row, unit_arrangement[row])
                  for row in rows for column in columns]
        print(layout)
        display_diecase_layout(layout, unit_arrangement)
    # After editing, pass the layout to whatever called this function
    return layout


def exit_program():
    """Exit program:

    All objects call this method whenever they want to exit program.
    This is because we may do something specific in different UIs,
    so an abstraction layer may come in handy.
    """
    print('Goodbye!')
    exit()
