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
    results = DB.get_all_diecases()
    ui.display('\n' + 'Diecase ID'.ljust(15) +
               'Type series'.ljust(15) +
               'Type size'.ljust(15) +
               'Wedge series'.ljust(15) +
               'Set width'.ljust(15) +
               'Typeface name' + '\n')
    for diecase in results:
        # Collect diecase parameters
        row = [str(field).ljust(15) for field in diecase[:-2]]
        # Add typeface name - no justification!
        row.append(diecase[-2])
        ui.display(''.join(row))
    return True


def show_diecase_layout():
    """Used for showing a diecase layout.

    Lists diecases, then allows user to choose ID.
    """
    ui.clear()
    # Do it only if we have wedges (depends on list_wedges retval)
    while list_diecases():
        # Enter the diecase name
        prompt = 'Enter the diecase ID to show (leave blank to exit): '
        diecase_id = ui.enter_data(prompt) or exceptions.return_to_menu()
        # Build a list of all characters
        # First, get diecase data
        (diecase_id, type_series, type_size, set_width, wedge_series,
         typeface_name, layout) = DB.diecase_by_id(diecase_id)
        # Process metadata
        styles = ', '.join([i for i in layout.keys() if i is not 'spaces'])
        info = []
        info.append('Diecase ID: %s' % diecase_id)
        info.append('Type series: %s' % type_series)
        info.append('Type size: %s' % type_size)
        info.append('Wedge series: %s' % wedge_series)
        info.append('Set width: %s' % set_width)
        info.append('Typeface name: %s' % typeface_name)
        info.append('Styles present: %s' % styles)
        # Get wedge unit arrangement
        wedge = DB.wedge_by_name_and_width(wedge_series, set_width)
        unit_values = wedge[4]
        unit_arrangement = {}
        shift_unit_arrangement = {}
        for i, step in enumerate(unit_values, 1):
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
        # Build rows and columns to iterate over
        column_numbers = ('NI', 'NL') + tuple([x for x in 'ABCDEFGHIJKLMNO'])
        row_numbers = range(1, 16)
        # Arrange matrices
        diecase_arrangement = []
        for row_number in row_numbers:
            # Add only characters and styles, center chars to 5
            row = [(mat[4].center(5), mat[3]) for mat in all_mats
                   for column_number in column_numbers
                   if matrix[0] == row_number and matrix[1] == column_number]
            diecase_arrangement.append(row)
        # We can display it
        header = ['Row: '.ljust(6)]
        header += [col.center(5) for col in column_numbers]
        header.append('Units'.center(8))
        header.append('Shifted'.center(8))
        # Print a header with column numbers
        ui.display(''.join(header))
        for i, row in enumerate(diecase_arrangement, 1):
            try:
                units = str(unit_arrangement[i]).center(8)
            except KeyError:
                units = ''.center(8)
            try:
                shift_units = str(shift_unit_arrangement[i]).center(8)
            except KeyError:
                shift_units = ''.center(8)
            # First, row number
            data = [int(i).ljust(6)]
            # Then, all chars
            row = [i[0] for i in row]
            data.extend(row)
            data.append(units)
            data.append(shift_units)
            data = ''.join(data)
            # Finally, display the row...
            ui.display(data)


def add_diecase(diecase_id, type_series, type_size, set_width,
                typeface_name, wedge_series, layout):
    """add_diecase:

    Wrapper function - adds a matrix case to the database.
    Displays info and asks for confirmation.
    """
    styles = ', '.join([i for i in layout.keys() if i is not 'spaces'])
    info = []
    info.append('Diecase ID: %s' % diecase_id)
    info.append('Type series: %s' % type_series)
    info.append('Type size: %s' % type_size)
    info.append('Wedge series: %s' % wedge_series)
    info.append('Set width: %s' % set_width)
    info.append('Typeface name: %s' % typeface_name)
    info.append('Styles present: %s' % styles)
    # Display metadata
    for line in info:
        ui.display(line)
    # Ask for confirmation
    options = {'Y': True, 'N': False}
    message = ('Commit? [Y]es, [N]o: ')
    if ui.simple_menu(message, options):
        DB.add_diecase(diecase_id, type_series, type_size, float(set_width),
                       typeface_name, wedge_series, layout)
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
    while list_diecases():
        try:
            prompt = 'Enter the diecase ID to delete (leave blank to exit): '
            diecase_id = ui.enter_data(prompt) or exceptions.return_to_menu()
        except (ValueError, TypeError):
            # Not number? Skip diecase deletion, start over.
            continue
        # Ask for confirmation
        ans = ui.simple_menu('Are you sure? [Y / N]', {'Y': True, 'N': False})
        if ans and DB.delete_diecase(diecase_id):
            ui.display('Matrix case deleted successfully.')
