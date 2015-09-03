"""
wedge_data

Contains higher-level functions for accessing wedge data.
This sits on top of the database module and is an abstraction layer
for other modules (like inventory, casting, typesetter).
Processes the data retrieved from database.
"""
from rpi2caster.global_settings import USER_INTERFACE as ui
from rpi2caster import exceptions
from rpi2caster import database
DB = database.Database()

# Wedge unit arrangement definitions
# Thanks to John Cornelisse for those unit arrangements!
WEDGES = {'5': (5, 6, 7, 8, 9, 9, 9, 10, 10, 11, 12, 13, 14, 15, 18),
          '96': (5, 6, 7, 8, 9, 9, 10, 10, 11, 12, 13, 14, 15, 16, 18),
          '111': (5, 6, 7, 8, 8, 8, 9, 9, 9, 9, 10, 12, 12, 13, 15),
          '221': (5, 6, 7, 8, 9, 9, 10, 10, 11, 12, 13, 14, 15, 17, 19),
          '334': (5, 6, 7, 8, 9, 9, 10, 10, 11, 11, 13, 14, 15, 16, 18),
          '344': (5, 6, 7, 9, 9, 9, 10, 11, 11, 12, 12, 13, 14, 15, 16),
          '377': (5, 6, 7, 8, 8, 9, 9, 10, 10, 11, 12, 13, 14, 15, 18),
          '409': (5, 6, 7, 8, 8, 9, 9, 10, 10, 11, 12, 13, 14, 15, 16),
          '467': (5, 6, 7, 8, 8, 9, 9, 9, 10, 11, 12, 13, 14, 15, 18),
          '486': (5, 7, 6, 8, 9, 11, 10, 10, 13, 12, 14, 15, 15, 18, 16),
          '526': (5, 6, 7, 8, 9, 9, 10, 10, 11, 12, 13, 14, 15, 17, 18),
          '536': (5, 6, 7, 8, 9, 9, 10, 10, 11, 12, 13, 14, 15, 17, 18),
          '562': (5, 6, 7, 8, 9, 9, 9, 10, 11, 12, 13, 14, 15, 17, 18),
          '607': (5, 6, 7, 8, 9, 9, 9, 9, 10, 11, 12, 13, 14, 15, 18),
          '611': (6, 6, 7, 9, 9, 10, 11, 11, 12, 12, 13, 14, 15, 16, 18),
          '674': (5, 6, 7, 8, 8, 9, 9, 9, 10, 10, 11, 12, 13, 14, 15, 18),
          '724': (5, 6, 7, 8, 8, 9, 9, 10, 10, 11, 13, 14, 15, 16, 18),
          '990': (5, 5, 6, 7, 8, 9, 9, 9, 9, 10, 10, 11, 13, 14, 18),
          '1063': (5, 6, 8, 9, 9, 9, 9, 10, 12, 12, 13, 14, 15, 15, 18),
          '1329': (4, 5, 7, 8, 9, 9, 9, 9, 10, 10, 11, 12, 12, 13, 15),
          '1331': (4, 5, 7, 8, 8, 9, 9, 9, 9, 10, 11, 12, 12, 13, 15),
          '1406': (4, 5, 6, 7, 8, 8, 9, 9, 9, 9, 10, 10, 11, 12, 13, 15),
          '1676': (5, 6, 7, 8, 9, 9, 9, 9, 10, 11, 12, 14, 15, 18, 13),
          '1881': (5, 6, 7, 8, 9, 9, 9, 12, 13, 10, 10, 14, 15, 11, 18),
          '2006': (5, 6, 7, 8, 8, 9, 9, 10, 10, 13, 11, 16, 18, 14, 15),
          'TPWR': (9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9)}


def add_wedge():
    """add_wedge()

    Used for adding wedges.

    Can be called with or without arguments.

    wedge_name - string - series name for a wedge (e.g. S5, S111)
    set_width  - float - set width of a particular wedge (e.g. 9.75)
    brit_pica - boolean - whether the wedge is based on British pica
    (0.1667") or not (American pica - 0.1660")
    True if the wedge is for European market ("E" after set width number)
    steps - string with unit values for steps - e.g. '5,6,7,8,9,9,9...,16'

    Start with defining the unit arrangements for some known wedges.
    This data will be useful when adding a wedge. The setup program
    will look up a wedge by its name, then get unit values.

    The TPWR wedge is a special wedge, where all steps have
    the same unit value of 9. It is used for casting constant-width
    (monospace) type, like the typewriters have. You could even cast
    from regular matrices, provided that you use 0005 and 0075 wedges
    to add so many units that you can cast wide characters
    like "M", "W" etc. without overhang. You'll get lots of spacing
    between narrower characters, because they'll be cast on a body
    wider than necessary.

    In this program, all wedges have the "S" (for stopbar) letter
    at the beginning of their designation. However, the user can enter
    a designation with or without "S", so check if it's there, and
    append if needed (only for numeric designations - not the "monospace"
    or other text values!)

    If no name is given, assume that the user means the S5 wedge, which is
    very common and most casting workshops have a few of them.
    """
    # Start with a clear screen
    ui.clear()
    # Display an explanation once
    ui.display('Adding a wedge:\n\n'
               'To use a wedge/stopbar definition in rpi2caster, you must '
               'add the wedge to the database. \n'
               'Enter the wedge name  you can see on the wedge, and the '
               'program will try to determine \n'
               'its width and unit arrangement.\n'
               'The set width will usually be a fractional number - you '
               'must enter it \n'
               'as a decimal fraction (e.g. 9 1/4 = 9.25), '
               'with point or comma as delimiter.\n\n'
               'Some special wedges are:\n'
               '"setwidth AK" - it is a 5-series wedge,\n'
               'typewriter wedges (monospace, uniform width) - enter '
               '"tpwr setwidth" for those.')
    while True:
        # Repeat the procedure all over again, if necessary
        # (can be exited by raising an exception)
        # Enter the wedge name first:
        wedge_name = ''
        set_width = ''
        brit_pica = None
        unit_arrangement = None
        while not wedge_name:
            # Ask for wedge name and set width as it is written on the wedge
            prompt = ('Wedge name (leave blank to return to menu): ')
            wedge_name = (ui.enter_data_or_blank(prompt) or
                          exceptions.return_to_menu())
        # For countries that use comma as decimal delimiter, convert to point:
            wedge_name = wedge_name.replace(',', '.').upper()
        if 'AK' in wedge_name:
            # For the old designation of 5-series wedges
            set_width = float(wedge_name.replace('AK', '').strip())
            ui.display('This is a 5-series wedge, designated as "AK"')
            wedge_name = '5'
        elif 'BO' in wedge_name:
            # For the old designation of 5-series wedges
            set_width = float(wedge_name.replace('AK', '').strip())
            ui.display('This is a 221-series wedge, designated as "BO"')
            wedge_name = '221'
        elif 'TPWR' in wedge_name:
            ui.display('This is a typewriter wedge.')
            set_width = float(wedge_name.replace('TPWR', '').strip())
            wedge_name = 'TPWR'
        elif wedge_name.endswith('E'):
            # For wedges made for European countries that use the Didot system
            # (these wedges were based on the old British pica,
            # i.e. 18unit 12set type was .1667" wide)
            ui.display('The letter E at the end means that this wedge was '
                       'made for European market, and based on pica =.1667".')
            brit_pica = True
            # Parse the input data to get the name and set width
            (wedge_name, set_width) = wedge_name.strip('E').split('-')
        else:
            # For wedges marked as "5-6.5" etc.
            (wedge_name, set_width) = wedge_name.split('-')
        # We now should have a wedge series and set width, as strings.
        # Convert the set width to float or enter it manually.
        wedge_series = wedge_name.strip('sS')
        try:
            # Should work...
            set_width = float(set_width)
        except ValueError:
            # if not - enter the width manually
            prompt = 'Enter the set width as a decimal fraction: '
            set_width = ui.enter_data_spec_type(prompt, float)
        prompt = 'Old British pica (0.1667") based wedge?'
        brit_pica = brit_pica or ui.yes_or_no(prompt)
        # We have the wedge name, so we can look the wedge up in known wedges
        # (no need to enter the unit arrangement manually)
        try:
            # Look up the unit arrangement
            unit_arrangement = WEDGES[wedge_series]
        except KeyError:
            # Unknown wedge
            unit_arrangement = None
            # Check if we have the values hardcoded already:
            prompt = ('Enter the wedge unit values for rows 1...15 or 1...16, '
                      'separated by commas.\n')
            unit_arrangement = ui.enter_data(prompt).split(',')
        # Now we need to be sure that all whitespace is stripped,
        # and the value written to database is a list of integers
            unit_arrangement = [int(i.strip()) for i in unit_arrangement]
        # Display warning if the number of steps is anything other than
        # 15 or 16 (15 is most common, 16 was used for HMN and KMN systems).
        # If length is correct, tell user it's OK.
            warn_min = ('Warning: the wedge you entered has < 15 steps!'
                        '\nThis is almost certainly a mistake.\n')
            warn_max = ('Warning: the wedge you entered has > 16 steps!'
                        '\nThis is almost certainly a mistake.\n')
            ua_ok = ('The wedge has %i steps. That is OK.'
                     % len(unit_arrangement))
            if len(unit_arrangement) < 15:
                ui.display(warn_min)
            elif len(unit_arrangement) > 16:
                ui.display(warn_max)
            else:
                ui.display(ua_ok)
        # Display a summary with wedge's values:
        user_info = []
        user_info.append('Wedge: ' + str(wedge_series))
        user_info.append('Set width: ' + str(set_width))
        user_info.append('British pica wedge?: ' + str(brit_pica))
        user_info.append('Unit arrangement for that wedge:')
        rows_line = ''.join([str(i).ljust(5) for i in range(1, 16)])
        unit_values_line = ''.join([str(u).ljust(5) for u in unit_arrangement])
        data = ('Row:'.ljust(8) + rows_line + '\n' +
                'Units:'.ljust(8) + unit_values_line + '\n')
        user_info.append(data)
        # Display the info
        ui.display('\n'.join(user_info))
        # Ask for confirmation
        if ui.yes_or_no('Commit?') and DB.add_wedge(wedge_series, set_width,
                                                    brit_pica,
                                                    unit_arrangement):
            ui.display('Wedge added successfully.')


def delete_wedge():
    """Used for deleting a wedge from database.

    Lists wedges, then allows user to choose ID.
    """
    ui.clear()
    # Do it only if we have wedges (depends on list_wedges retval)
    while True:
        # Loop over or throw an exception if there are no diecases
        available_wedges = list_wedges()
        # Enter the diecase name
        prompt = 'Number of a wedge to delete? (leave blank to exit): '
        choice = (ui.enter_data_or_blank(prompt) or
                  exceptions.return_to_menu())
        # Safeguards against entering a wrong number or non-numeric string
        try:
            wedge_id = available_wedges[choice][0]
        except KeyError:
            ui.display('Wedge number is incorrect!')
            continue
        # Ask for confirmation
        if ui.yes_or_no('Are you sure?') and DB.delete_wedge(wedge_id):
            ui.display('Wedge deleted successfully.')


def list_wedges():
    """Lists all wedges we have."""
    data = DB.get_all_wedges()
    results = {}
    ui.display('\n' +
               'Number'.ljust(10) +
               'wedge series'.ljust(15) +
               'set width'.ljust(15) +
               'Brit. pica?'.ljust(15) +
               'unit arrangement' +
               '\n')
    for index, wedge in enumerate(data, start=1):
        index = str(index)
        # Save the wedge associated with the index
        results[index] = wedge
        # Display only wedge parameters and not ID
        number = [index.ljust(10)]
        displayed_data = [str(field).ljust(15) for field in wedge[1:]]
        ui.display(''.join(number + displayed_data))
    return results


def choose_wedge():
    """choose_wedge:

    Lists wedges and lets the user choose one; returns the wedge ID.
    """
    # Do it only if we have diecases (depends on list_diecases retval)
    while True:
        ui.clear()
        ui.display('Choose a wedge:', end='\n\n')
        available_wedges = list_wedges()
        # Enter the diecase name
        prompt = 'Number of a wedge? (leave blank to exit): '
        choice = (ui.enter_data_or_blank(prompt) or
                  exceptions.return_to_menu())
        # Safeguards against entering a wrong number or non-numeric string
        try:
            # Return [series_number, set_width, brit_pica, unit_arrangement]
            wedge = list(available_wedges[choice])
            wedge[3] = bool(wedge[3])
            return tuple(wedge)
        except KeyError:
            ui.confirm('Wedge number is incorrect! [Enter] to continue...')
            continue


def wedge_by_name_and_width(wedge_name, set_width):
    """Wrapper for database function of the same name"""
    return DB.wedge_by_name_and_width(wedge_name, set_width)


def get_unit_arrangement(wedge_series, set_width):
    """Returns an unit arrangement for a given wedge."""
    try:
        wedge = DB.wedge_by_name_and_width(wedge_series, set_width)
        unit_arrangement = [int(i) for i in wedge[4]]
    except exceptions.NoMatchingData:
        try:
            unit_arrangement = WEDGES[wedge_series]
        except KeyError:
            prompt = ('Enter the wedge unit values for rows 1...15 or 1...16, '
                      'separated by commas.\n')
            unit_arrangement = ui.enter_data(prompt).split(',')
    return unit_arrangement


def is_old_pica(wedge_series, set_width):
    """is_old_pica:

    Checks whether this wedge is based on old British pica (.1667") or not.
    """
    try:
        wedge = DB.wedge_by_name_and_width(wedge_series, set_width)
        # British pica (1 or 0) is the fourth column
        return bool(wedge[3])
    except exceptions.NoMatchingData:
        return ui.yes_or_no('Using an old British pica (.1667") wedge?')
