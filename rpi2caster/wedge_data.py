"""
wedge_data

Contains higher-level functions for accessing wedge data.
This sits on top of the database module and is an abstraction layer
for other modules (like inventory, casting, typesetter).
Processes the data retrieved from database.
"""
from rpi2caster import text_ui as ui
from rpi2caster import exceptions
from rpi2caster import database
DB = database.Database()


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
    # Thanks to John Cornelisse for those unit arrangements!
    wedges = {5: [5, 6, 7, 8, 9, 9, 9, 10, 10, 11, 12, 13, 14, 15, 18, 18],
              96: [5, 6, 7, 8, 9, 9, 10, 10, 11, 12, 13, 14, 15, 16, 18, 18],
              111: [5, 6, 7, 8, 8, 8, 9, 9, 9, 9, 10, 12, 12, 13, 15, 15],
              334: [5, 6, 7, 8, 9, 9, 10, 10, 11, 11, 13, 14, 15, 16, 18, 18],
              344: [5, 6, 7, 9, 9, 9, 10, 11, 11, 12, 12, 13, 14, 15, 16, 16],
              377: [5, 6, 7, 8, 8, 9, 9, 10, 10, 11, 12, 13, 14, 15, 18, 18],
              409: [5, 6, 7, 8, 8, 9, 9, 10, 10, 11, 12, 13, 14, 15, 16, 16],
              467: [5, 6, 7, 8, 8, 9, 9, 9, 10, 11, 12, 13, 14, 15, 18, 18],
              486: [5, 7, 6, 8, 9, 11, 10, 10, 13, 12, 14, 15, 15, 18, 16, 16],
              526: [5, 6, 7, 8, 9, 9, 10, 10, 11, 12, 13, 14, 15, 17, 18, 18],
              536: [5, 6, 7, 8, 9, 9, 10, 10, 11, 12, 13, 14, 15, 17, 18, 18],
              562: [5, 6, 7, 8, 9, 9, 9, 10, 11, 12, 13, 14, 15, 17, 18, 18],
              607: [5, 6, 7, 8, 9, 9, 9, 9, 10, 11, 12, 13, 14, 15, 18, 18],
              611: [6, 6, 7, 9, 9, 10, 11, 11, 12, 12, 13, 14, 15, 16, 18, 18],
              674: [5, 6, 7, 8, 8, 9, 9, 9, 10, 10, 11, 12, 13, 14, 15, 18],
              724: [5, 6, 7, 8, 8, 9, 9, 10, 10, 11, 13, 14, 15, 16, 18, 18],
              990: [5, 5, 6, 7, 8, 9, 9, 9, 9, 10, 10, 11, 13, 14, 18, 18],
              1063: [5, 6, 8, 9, 9, 9, 9, 10, 12, 12, 13, 14, 15, 15, 18, 18],
              1329: [4, 5, 7, 8, 9, 9, 9, 9, 10, 10, 11, 12, 12, 13, 15, 15],
              1331: [4, 5, 7, 8, 8, 9, 9, 9, 9, 10, 11, 12, 12, 13, 15, 15],
              1406: [4, 5, 6, 7, 8, 8, 9, 9, 9, 9, 10, 10, 11, 12, 13, 15],
              'TPWR': [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9]}
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
            wedge_name = ui.enter_data(prompt) or exceptions.return_to_menu()
        # For countries that use comma as decimal delimiter, convert to point:
            wedge_name = wedge_name.replace(',', '.').upper()
        if 'AK' in wedge_name:
            # For the old designation of 5-series wedges
            set_width = float(wedge_name.replace('AK', '').strip())
            ui.display('This is a 5-series wedge, designated as "AK"')
            wedge_name = '5'
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
        # We operate on integers or floats though.
        # Convert the wedge name to integer:
        if wedge_name not in ['TPWR']:
            try:
                wedge_name = int(wedge_name)
            except ValueError:
                # Start the procedure all over again (pause)
                ui.enter_data('Incorrect wedge name! Enter it again. '
                              'Press [Enter] to continue...')
                continue
        # We now have determined the wedge name.
        # Convert the set width to float or enter it manually.
        try:
            # Should work...
            set_width = float(set_width)
        except ValueError:
            # if not - enter the width manually
            set_width = ''
            while not set_width:
                try:
                    # Enter width manually
                    prompt = 'Enter the set width as a decimal fraction: '
                    set_width = float(ui.enter_data(prompt))
                except ValueError:
                    # In case of incorrect value...
                    set_width = ''
                    # Start over
        # We should determine if it's a British or American wedge
        # (18 units 12 set = 1pica = .1667" - British, or .1660" - US )
        if brit_pica is None:
            # Do it only if undefined
            # Let user choose if it's American or British pica-based wedge:
            options = {'A': False, 'B': True}
            message = '[A]merican (0.1660"), or [B]ritish (0.1667") pica? '
            choice = ui.simple_menu(message, options).upper()
            brit_pica = options[choice]
        # We have the wedge name, so we can look the wedge up in known wedges
        # (no need to enter the unit arrangement manually)
        try:
            # Look up the unit arrangement
            unit_arrangement = wedges[wedge_name]
        except KeyError:
            # Unknown wedge
            unit_arrangement = None
            # Check if we have the values hardcoded already:
            prompt = ('Enter the wedge unit values for rows 1...15 or 1...16, '
                      'separated by commas.\n')
            while not unit_arrangement:
                # Make it a list at once
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
        user_info.append('Wedge: ' + str(wedge_name))
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
        ans = ui.simple_menu('Commit? [Y / N]', {'Y': 'Y', 'N': 'N'})
        if ans in ['y', 'Y']:
            if DB.add_wedge(wedge_name, set_width,
                            brit_pica, unit_arrangement):
                ui.display('Wedge added successfully.')


def delete_wedge():
    """Used for deleting a wedge from database.

    Lists wedges, then allows user to choose ID.
    """
    ui.clear()
    # Do it only if we have wedges (depends on list_wedges retval)
    while list_wedges():
        try:
            prompt = 'Enter the wedge ID to delete (leave blank to exit): '
            w_id = ui.enter_data(prompt) or exceptions.return_to_menu()
            w_id = int(w_id)
        except (ValueError, TypeError):
            # Not number? Skip wedge deletion, start over.
            continue
        # Ask for confirmation
        ans = ui.simple_menu('Are you sure? [Y / N]', {'Y': 'Y', 'N': 'N'})
        if ans in ['y', 'Y'] and DB.delete_wedge(w_id):
            ui.display('Wedge deleted successfully.')


def list_wedges():
    """Lists all wedges we have."""
    results = DB.get_all_wedges()
    ui.display('\n' + 'wedge id'.ljust(15) +
               'wedge No'.ljust(15) +
               'set width'.ljust(15) +
               'Brit. pica?'.ljust(15) +
               'Unit arrangement' +
               '\n')
    for wedge in results:
        ui.display(''.join([str(field).ljust(15) for field in wedge]))
    return True


def wedge_by_name_and_width(wedge_name, set_width):
    """Wrapper for database function of the same name"""
    return DB.wedge_by_name_and_width(wedge_name, set_width)
