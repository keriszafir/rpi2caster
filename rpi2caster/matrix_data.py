# -*- coding: utf-8 -*-
"""matrix_data

Module containing functions for diecase retrieval and parsing,
diecase storing, parameter searches.
"""
from rpi2caster.global_settings import USER_INTERFACE as ui
from rpi2caster import exceptions
from rpi2caster import database
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


# Placeholders for functionality not implemented yet:
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


def show_diecase_layout():
    """Used for showing a diecase layout.

    Lists diecases, then allows user to choose ID.
    """
    ui.clear()
    # Do it only if we have wedges (depends on list_wedges retval)
    while True:
        available_diecases = list_diecases()
        # Enter the diecase name
        prompt = 'Number of a diecase to show? (leave blank to exit): '
        choice = (ui.enter_data_or_blank(prompt) or
                  exceptions.return_to_menu())
        # Safeguards against entering a wrong number or non-numeric string
        try:
            diecase_id = available_diecases[choice]
        except KeyError:
            ui.display('Diecase number is incorrect!')
            continue
        # Build a list of all characters
        # First, get diecase data
        (diecase_id, type_series, type_size, wedge_series, set_width,
         typeface_name, layout) = DB.diecase_by_id(diecase_id)
        # Process metadata
        styles = None
        if layout:
            styles = ', '.join([i for i in layout.keys() if i is not 'spaces'])
        info = []
        info.append('Diecase ID: %s' % diecase_id)
        info.append('Type series: %s' % type_series)
        info.append('Type size: %s' % type_size)
        info.append('Wedge series: %s' % wedge_series)
        info.append('Set width: %s' % set_width)
        info.append('Typeface name: %s' % typeface_name)
        info.append('Styles present: %s' % styles)
        # End here if diecase is empty
        if not styles:
            ui.display('This diecase is empty!\n')
            continue
        # Get wedge unit arrangement
        try:
            wedge = DB.wedge_by_name_and_width(wedge_series, set_width)
            unit_values = wedge[4]
        except exceptions.NoMatchingData:
            ui.display('Wedge %s - %s not found in database! '
                       'Displaying the unit arrangement for wedge 5 instead.'
                       % (wedge_series, set_width))
            unit_values = (5, 6, 7, 8, 9, 9, 9, 10, 10, 11, 12, 13, 14, 15, 18)
        unit_arrangement = {}
        shift_unit_arrangement = {}
        for i, step in enumerate(unit_values, start=1):
            unit_arrangement[i] = step
            shift_unit_arrangement[i+1] = step
        # Display metadata
        for line in info:
            ui.display(line)
        ui.display(' ')
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
                        space_symbol = '⦻'
                    else:
                        space_symbol = '⨷'
                    matrix = (row, column, '', space_symbol)
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
                    # Build a matrix starting with row, then column, and char
                    matrix = (row, column, style, character)
                    # Add it to matrices list
                    all_mats.append(matrix)
        # Get the available rows
        # This will skip unfilled rows (with blanks)
        row_numbers = sorted({mat[0] for mat in all_mats})
        # Build rows and columns to iterate over
        column_numbers = ('NI', 'NL') + tuple([x for x in 'ABCDEFGHIJKLMNO'])
        # Arrange matrices
        diecase_arrangement = []
        for row_number in row_numbers:
            # Add only characters and styles, center chars to 5
            row = [(mat[3].ljust(5), mat[2])
                   for column_number in column_numbers
                   for mat in all_mats
                   if mat[0] == row_number and mat[1] == column_number]
            diecase_arrangement.append(row)
        # We can display it
        header = ['Row \ Col: '.ljust(12)]
        header += [col.ljust(5) for col in column_numbers]
        header.append('Units'.center(8))
        header.append('Shifted'.center(8))
        # Print a header with column numbers
        ui.display(''.join(header))
        for i, row in enumerate(diecase_arrangement, start=1):
            try:
                units = str(unit_arrangement[i]).center(8)
            except KeyError:
                units = ''.center(8)
            try:
                shift_units = str(shift_unit_arrangement[i]).center(8)
            except KeyError:
                shift_units = ''.center(8)
            # First, row number
            data = [str(i).ljust(12)]
            # Then, all chars
            row = [i[0] for i in row]
            data.extend(row)
            data.append(units)
            data.append(shift_units)
            data = ''.join(data)
            # Finally, display the row...
            ui.display(data)
            ui.display('')


def add_diecase(diecase_id=None, type_series=None, type_size=None,
                wedge_series=None, set_width=None,
                typeface_name=None, layout={}):
    """add_diecase:

    Wrapper function - adds a matrix case to the database.
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
    options = {'Y': True, 'N': False}
    message = ('Commit? [Y]es, [N]o: ')
    if ui.simple_menu(message, options):
        DB.add_diecase(diecase_id, type_series, type_size, wedge_series,
                       float(set_width), typeface_name, layout)
        ui.display('Data added successfully.')


def edit_diecase():
    """Not implemented yet"""
    pass


def clear_diecase():
    """Not implemented yet"""
    pass


def delete_diecase():
    """Used for deleting a diecase from database.

    Lists diecases, then allows user to choose ID.
    """
    ui.clear()
    # Do it only if we have wedges (depends on list_wedges retval)
    while True:
        # Loop over or throw an exception if there are no diecases
        available_diecases = list_diecases()
        # Enter the diecase name
        prompt = 'Number of a diecase to delete? (leave blank to exit): '
        choice = (ui.enter_data_or_blank(prompt) or
                  exceptions.return_to_menu())
        # Safeguards against entering a wrong number or non-numeric string
        try:
            diecase_id = available_diecases[choice]
        except KeyError:
            ui.display('Diecase number is incorrect!')
            continue
        # Ask for confirmation
        ans = ui.simple_menu('Are you sure? [Y / N]', {'Y': True, 'N': False})
        if ans and DB.delete_diecase(diecase_id):
            ui.display('Matrix case deleted successfully.')
