# -*- coding: utf-8 -*-
"""matrix_data

Module containing functions for diecase retrieval and parsing,
diecase storing, parameter searches.
"""
import io
# We need user interface
from rpi2caster.global_settings import USER_INTERFACE as ui
from rpi2caster.global_settings import COMMENT_SYMBOLS
# Some functions raise custom exceptions
from rpi2caster import exceptions
# We need to operate on a database
from rpi2caster import database
# Wedge operations for several matrix-case management functions
from rpi2caster import wedge_data
# Create an instance of Database class with default parameters
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


def show_diecase():
    """show_diecase:

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
    # Names of styles found in the diecase with formatting applied to them
    displayed_styles = '\n'.join([ui.format_display(style, style)
                                 for style in get_styles(layout)])
    # Explanation of symbols
    ui.display('Explanation:', '□ - low space', '▣ - high space',
               displayed_styles, sep='\n', end='\n')


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
    # Display parameters before asking to commit
    info = []
    info.append('Diecase ID: %s' % diecase_id)
    info.append('Type series: %s' % type_series)
    info.append('Type size: %s' % type_size)
    info.append('Wedge series: %s' % wedge_series)
    info.append('Set width: %s' % set_width)
    info.append('Typeface name: %s' % typeface_name)
    info.append('Styles present: %s' % ', '.join(get_styles(layout)))
    for line in info:
        ui.display(line)
    # Load the layout from file? Ask only if no layout at input
    layout = layout or submit_layout_file() or None
    # Ask for confirmation
    if ui.yes_or_no('Commit?'):
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
        # Load the layout from file? Ask only if no layout at input
        layout = submit_layout_file() or layout
        # Ask for confirmation
        ans = ui.yes_or_no('Are you sure?')
        if ans and DB.update_diecase_layout(diecase_id, layout):
            ui.display('Matrix case layout updated successfully.')


def clear_diecase():
    """clear_diecase:

    Clears the diecase layout, so it can be entered from scratch.
    You usually want to use this if you seriously mess something up.
    """
    while True:
        diecase_id = choose_diecase()
        ans = ui.yes_or_no('Are you sure?')
        if ans and DB.update_diecase_layout(diecase_id):
            ui.display('Matrix case purged successfully - now empty.')


def delete_diecase():
    """Used for deleting a diecase from database.

    Lists diecases, then allows user to choose ID.
    """
    while True:
        diecase_id = choose_diecase()
        ans = ui.yes_or_no('Are you sure?')
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
    # Begin with an empty matrix list - mats will be added one by one
    all_mats = []
    # Iterate over all the matrices in layout dictionary
    for matrix in layout:
        # Each matrix is described as an association of tuples
        # (character, (style1, style2...)) : (column, row, unit_width)
        # We can have multiple 'A', 'B' etc. - provided the style is different
        #
        # A single character can belong to multiple styles
        # (for example, punctuation marks used by bold and small caps)
        # The first style will be dominant and used for formatting display.
        #
        # Low spaces and high spaces are indicated as styles too.
        # Their 'character' is a number.
        # This will make the matrices easier to address when typesetting.
        #
        # Translated matrix data stands as follows:
        # (row, column, character)
        style = matrix[1][0]
        column = layout[matrix][0]
        row = layout[matrix][1]
        # If we have a space - we don't want to see a number
        # Use a predefined space symbol instead
        if style == ('low_space',):
            character = '□'
        elif style == ('high_space',):
            character = '▣'
        else:
            # Format the character accordingly for display
            character = ui.format_display(matrix[0], style)
        # Add it to the list of matrices
        all_mats.append((row, column, character))
    # After we're done, return the list of mats
    return all_mats


def get_diecase_parameters(diecase_id):
    """get_diecase_parameters:

    Displays parameters for a chosen matrix case and returns them.
    """
    (diecase_id, type_series, type_size, wedge_series, set_width,
     typeface_name, layout) = DB.diecase_by_id(diecase_id)
    # Display parameters before editing
    info = []
    info.append('Diecase ID: %s' % diecase_id)
    info.append('Type series: %s' % type_series)
    info.append('Type size: %s' % type_size)
    info.append('Wedge series: %s' % wedge_series)
    info.append('Set width: %s' % set_width)
    info.append('Typeface name: %s' % typeface_name)
    info.append('Styles present: %s' % ', '.join(get_styles(layout)))
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
    ui.display('Styles present: %s' % ', '.join(get_styles(layout)))
    return layout


def get_styles(layout):
    """Parses the diecase layout and gets available typeface styles.
    Returns a list of them."""
    return list({style for mat in layout for style in mat[1]
                if style not in ('high_space', 'low_space')}) or []


def submit_layout_file():
    """submit_layout_file:

    Reads a matrix case arrangement from a text or csv file.
    The format should be:
    "character";"style1,style2...";"column";"row";"unit_width"
    """
    # Ask, and stop here if answered no
    if not ui.yes_or_no('Add layout from file?'):
        return False
    filename = ui.enter_input_filename()
    if not filename:
        return False
    with io.open(filename, 'r') as layout_file:
        layout = []
        low_space_count = 0
        high_space_count = 0
        for line in layout_file:
            # A record is a list with all diecase data:
            # [character, (style1, style2...), column, row, units]
            # Empty line is discarded, # denotes comment - don't parse
            if not line.strip() or line.startswith('# '):
                continue
            # Parse it and strip the components of whitespace
            record = line.split('";"')
            for item in record:
                item.strip()
            # Get character (and strip the left quote)
            if record[0] == '""':
                character = '"'
            elif record[0] == '\;':
                character = ';'
            else:
                character = record[0].lstrip('"')
            # Strip the right quote from the last item in the record
            record[-1] = record[-1].strip('"\n')
            # Split the styles
            styles = tuple(record[1].split(','))
            # No character? Then it is a space...
            if not character and 'low_space' in styles:
                character = low_space_count
                low_space_count += 1
            elif not character and 'high_space' in styles:
                character = high_space_count
                high_space_count += 1
            # We want to use uppercase column numbers
            column = record[2]
            # Add the remaining data
            row = int(record[3])
            try:
                unit_width = int(record[4])
            except (IndexError, ValueError):
                unit_width = None
            layout.append([(character, styles), (column, row, unit_width)])
    # We now have completed uploading a layout
    return layout
