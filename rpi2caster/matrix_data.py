# -*- coding: utf-8 -*-
"""matrix_data

Module containing functions for diecase retrieval and parsing,
diecase storing, parameter searches.
"""
from rpi2caster.global_settings import USER_INTERFACE as ui
from rpi2caster import exceptions
from rpi2caster import database
# Wedge operations for several matrix-case management functions
from rpi2caster import wedge_data
DB = database.Database()


def lookup_diecase(type_series, type_size):
    """lookup_diecase

    Searches for a diecase of given type series (e.g. 327) and size (e.g. 12),
    if several matches found - allows to choose one of them, returns data.
    """
    matches = DB.diecase_by_series_and_size(type_series, type_size)
    if len(matches) == 1:
        # One result found
        return matches[0]
    else:
        # More than one match - decide which one to use:
        idents = [record[0] for record in matches]
        # Associate diecases with IDs to select one later
        assoc = dict(zip(idents, matches))
        # Display a menu with diecases from 1 to the last:
        options = [(i, k) for i, k in enumerate(matches, start=1)]
        header = 'Choose a diecase:'
        choice = ui.menu(options, header)
        # Choose one
        chosen_id = options[choice]
        # Return a list with chosen diecase's parameters:
        return assoc[chosen_id]


def list_diecases():
    """Lists all matrix cases we have."""
    data = DB.get_all_diecases()
    results = {}
    ui.display('\n' +
               'Index'.ljust(7) +
               'Diecase ID'.ljust(20) +
               'Type series'.ljust(15) +
               'Type size'.ljust(15) +
               'Wedge series'.ljust(15) +
               'Set width'.ljust(15) +
               'Typeface name' + '\n')
    for index, diecase in enumerate(data, start=1):
        # Collect diecase parameters
        index = str(index)
        row = [index.ljust(7)]
        row.append(str(diecase[0]).ljust(20))
        row.extend([str(field).ljust(15) for field in diecase[1:-2]])
        # Add number and ID to the result that will be returned
        results[index] = diecase[0]
        # Add typeface name - no justification!
        row.append(diecase[-2])
        ui.display(''.join(row))
    ui.display('\n\n')
    # Now we can return the number - diecase ID pairs
    return results


def choose_diecase():
    """with_diecase_choice:

    Decorator function for choosing the diecase to operate on.
    Lists diecases and gets the diecase ID, then gives the control to the
    internal function that does operations on this diecase.
    """
    # Do it only if we have diecases (depends on list_diecases retval)
    while True:
        ui.clear()
        ui.display('Choose a matrix case:', end='\n\n')
        available_diecases = list_diecases()
        # Enter the diecase name
        prompt = 'Number of a diecase? (leave blank to exit): '
        choice = (ui.enter_data_or_blank(prompt) or
                  exceptions.return_to_menu())
        # Safeguards against entering a wrong number or non-numeric string
        try:
            diecase_id = available_diecases[choice]
            return diecase_id
        except KeyError:
            ui.confirm('Diecase number is incorrect! [Enter] to continue...')
            continue


def show_diecase_layout():
    """show_diecase_layout:

    Wrapper function for menu: used for choosing and showing a diecase layout.
    """
    while True:
        # Choose diecase
        diecase_id = choose_diecase()
        display_diecase_layout(diecase_id)
        ui.confirm('[Enter] to continue...')


def display_diecase_layout(diecase_id):
    """display_diecase_layout:

    Shows a layout for a given diecase ID.
    """
    # Build a list of all characters
    # First, get diecase data
    (diecase_id, type_series, type_size, wedge_series, set_width,
     typeface_name, layout) = DB.diecase_by_id(diecase_id)
    # Process metadata
    # Get wedge unit arrangement
    arrangements = wedge_data.get_unit_arrangement(wedge_series, set_width)
    (unit_arrangement, shift_unit_arrangement) = arrangements
    all_mats = get_all_matrices(layout)
    # Mark empty matrices or unaddressable parts of multi-cell mats
    # as unused
    all_mats.extend(flag_unused_matrices(all_mats))
    # Determine which rows have matrices
    # This will skip unfilled rows (with blanks) at the end
    row_numbers = sorted({mat[0] for mat in all_mats})
    # Build rows and columns to iterate over
    column_numbers = ('NI', 'NL') + tuple([x for x in 'ABCDEFGHIJKLMNO'])
    # Arrange matrices for displaying
    diecase_arrangement = []
    for row_number in row_numbers:
        # Add only characters and styles, center chars to 5
        row = [mat[2].center(5)
               for column_number in column_numbers for mat in all_mats
               if mat[0] == row_number and mat[1] == column_number]
        diecase_arrangement.append(row)
    # We can display it now
    header = ['|' + 'Row'.center(5) + '|']
    header.extend([col.center(5) for col in column_numbers])
    header.append('|' + 'Units'.center(8) + '|')
    header.append('Shifted'.center(8) + '|')
    header = (''.join(header))
    # Print a header with column numbers
    title = typeface_name + ' : ' + type_series + ' – ' + type_size
    title = '|' + title.center(len(header) - 2) + '|'
    separator = '—' * len(header)
    empty_row = ('|' + ' ' * 5 + '|' +
                 ' ' * 5 * len(column_numbers) + '|' +
                 ' ' * 8 + '|' + ' ' * 8 + '|')
    ui.display(separator, title, separator, header, separator, empty_row,
               sep='\n')
    # Get a unit-width for each row to display it at the end
    for i, row in enumerate(diecase_arrangement, start=1):
        # Now we are going to show the matrices
        # First, display row number (and borders), then characters in row
        data = ['|' + str(i).center(5) + '|'] + row
        # At the end, unit-width and unit-width when using unit-shift
        data.append('|' + str(unit_arrangement[i]).center(8) + '|')
        data.append(str(shift_unit_arrangement[i]).center(8) + '|')
        data = ''.join(data)
        # Finally, display the row and a newline
        ui.display(data, empty_row, sep='\n')
    # Display header again
    ui.display(separator, header, separator, sep='\n', end='\n\n')
    # Explanation of symbols
    styles = '\n'.join([ui.format_display(style, style)
                        for style in ui.STYLE_MODIFIERS])
    ui.display('Explanation:', '□ - low space', '▣ - high space', styles,
               sep='\n', end='\n')


def add_diecase(diecase_id=None, type_series=None, type_size=None,
                wedge_series=None, set_width=None,
                typeface_name=None, layout=None):
    """add_diecase:

    Adds a matrix case to the database.
    Can be called with arguments from another function, or the user can enter
    the data manually.
    Displays info and asks for confirmation.
    """
    if not diecase_id:
        diecase_id = ui.enter_data('Diecase ID? (must be unique) : ')
    if not type_series:
        type_series = ui.enter_data('Fount series: ')
    if not type_size:
        type_size = ui.enter_data('Type size (end with D for Didot): ')
    if not wedge_series:
        wedge_series = ui.enter_data('Wedge/stopbar for this typeface: ')
        # If we enter S5 etc. - save it as 5
        wedge_series = wedge_series.strip('sS')
    if not set_width:
        set_width = ui.enter_data_spec_type('Set width (decimal): ', float)
    if not typeface_name:
        typeface_name = ui.enter_data('Typeface name: ')
    if layout:
        styles = ', '.join([i for i in layout.keys() if i is not 'spaces'])
    else:
        styles = None
    # Display parameters before asking to commit
    info = []
    info.append('Diecase ID: %s' % diecase_id)
    info.append('Type series: %s' % type_series)
    info.append('Type size: %s' % type_size)
    info.append('Wedge series: %s' % wedge_series)
    info.append('Set width: %s' % set_width)
    info.append('Typeface name: %s' % typeface_name)
    info.append('Styles present: %s' % styles)
    for line in info:
        ui.display(line)
    # Ask for confirmation
    if ui.simple_menu('Commit? [Y/N]: ', {'Y': True, 'N': False}):
        DB.add_diecase(diecase_id, type_series, type_size, wedge_series,
                       float(set_width), typeface_name, layout)
        ui.display('Data added successfully.')


def edit_diecase():
    """edit_diecase:

    Chooses and edits a diecase layout.

    If layout is blank, user needs to enter the column and row numbers.
    Displays characters that were previously in position,
    allows to change them.
    A matrix can be used or not (for example, multiple-cell mats
    should be addressed only at one of these cells, where the centering pin
    can descend - and not where no hole is made, because trying to
    address such a cell can damage the caster!).
    If user wants to enter a space - decide if it is low or high.
    At the end, confirm and commit."""
    while True:
        diecase_id = choose_diecase()
        layout = get_layout(diecase_id)
        # Ask for confirmation
        ans = ui.simple_menu('Are you sure? [Y/N]: ', {'Y': True, 'N': False})
        if ans and DB.update_diecase_layout(diecase_id, layout):
            ui.display('Matrix case layout updated successfully.')


def clear_diecase():
    """clear_diecase:

    Clears the diecase layout, so it can be entered from scratch.
    You usually want to use this if you seriously mess something up.
    """
    while True:
        diecase_id = choose_diecase()
        ans = ui.simple_menu('Are you sure? [Y/N]: ', {'Y': True, 'N': False})
        if ans and DB.update_diecase_layout(diecase_id):
            ui.display('Matrix case purged successfully - now empty.')


def delete_diecase():
    """Used for deleting a diecase from database.

    Lists diecases, then allows user to choose ID.
    """
    while True:
        diecase_id = choose_diecase()
        ans = ui.simple_menu('Are you sure? [Y/N]: ', {'Y': True, 'N': False})
        if ans and DB.delete_diecase(diecase_id):
            ui.display('Matrix case deleted successfully.')


def flag_unused_matrices(all_mats):
    """fill_unused_matrices:

    Flags matrices without characters and spaces as unused, preventing them
    from being addressed during typesetting and casting.
    """
    unused_mats = []
    row_numbers = sorted({mat[0] for mat in all_mats})
    column_numbers = ('NI', 'NL') + tuple([x for x in 'ABCDEFGHIJKLMNO'])
    # Get all positions without a registered matrix
    for row_number in row_numbers:
        for column_number in column_numbers:
            match = [mat for mat in all_mats
                     if mat[0] == row_number and
                     mat[1] == column_number]
            if not match:
                unused_mats.append((row_number, column_number, ' '))
    return unused_mats


def get_all_matrices(layout):
    """get_all_matrices:

    Parses a diecase layout dictionary to get all matrices into a single list.
    """
    # Process the layout
    all_mats = []
    # Iterate over type styles - roman, bold, italic etc. and spaces
    for style in layout:
        # We look for spaces and characters
        if style == 'spaces':
            for space in layout[style]:
                column = space[0]
                row = space[1]
                low_space = space[2]
                if low_space:
                    space_symbol = '□'
                else:
                    space_symbol = '▣'
                matrix = (row, column, space_symbol)
                all_mats.append(matrix)
        else:
            # Iterate over matrices in a particular style
            for item in layout[style].items():
                # Character is first
                character = item[0]
                char_properties = item[1]
                # Coordinates
                column = char_properties[0]
                row = char_properties[1]
                # Alter the style of character
                character = ui.format_display(character, style)
                # Build a matrix starting with row, then column, and char
                matrix = (row, column, character)
                # Add it to matrices list
                all_mats.append(matrix)
    # All done, time to return the mats
    return all_mats


def get_diecase_parameters(diecase_id):
    """get_diecase_parameters:

    Displays parameters for a chosen matrix case and returns them.
    """
    (diecase_id, type_series, type_size, wedge_series, set_width,
     typeface_name, layout) = DB.diecase_by_id(diecase_id)
    if layout:
        styles = ', '.join([i for i in layout.keys()
                            if i not in ('spaces', 'shared')])
    else:
        styles = None
    # Display parameters before editing
    info = []
    info.append('Diecase ID: %s' % diecase_id)
    info.append('Type series: %s' % type_series)
    info.append('Type size: %s' % type_size)
    info.append('Wedge series: %s' % wedge_series)
    info.append('Set width: %s' % set_width)
    info.append('Typeface name: %s' % typeface_name)
    info.append('Styles present: %s' % styles)
    for line in info:
        ui.display(line)
    ui.display('\n\n')
    # Return data for further processing
    return (type_series, type_size, wedge_series, set_width,
            typeface_name, layout)


def get_layout(diecase_id):
    """get_layout:

    Displays parameters for a chosen matrix case and returns them.
    """
    layout = DB.diecase_by_id(diecase_id)[-1]
    if layout:
        styles = ', '.join([i for i in layout.keys()
                            if i not in ('spaces', 'shared')])
    else:
        styles = None
    ui.display('Styles present: %s' % styles)
    return layout
