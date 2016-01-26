# -*- coding: utf-8 -*-
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
from rpi2caster import wedge_arrangements
DB = database.Database()


class Wedge(object):
    """Wedge: wedge data"""
    def __init__(self, series='5', set_width=12):
        self.series = series
        self.set_width = set_width
        self.brit_pica = False
        self.unit_arrangement = wedge_arrangements.table[series]

    def setup(self, series=None, set_width=None):
        """Choose a wedge from registered ones automatically or manually"""
        # Try to find a wedge with given series and set width
        try:
            wedge = get_wedge(series, set_width)
        # Cannot find wedge with this series and set width = choose it
        except (exceptions.NoMatchingData, exceptions.DatabaseQueryError):
            wedge = choose_wedge()
        (self.series, self.set_width, self.brit_pica,
         self.unit_arrangement) = wedge


def add_wedge():
    """add_wedge()

    Used for adding wedges.

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
            prompt = ('Wedge name or [Enter] to go back: ')
            wedge_name = (ui.enter_data_or_blank(prompt) or
                          exceptions.menu_level_up())
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
            try:
                (wedge_name, set_width) = wedge_name.split('-')
            except ValueError:
                # Will be set later
                set_width = None
        # We now should have a wedge series and set width, as strings.
        # If user entered S in wedge name, throw it away
        wedge_series = wedge_name.strip('sS')
        # Convert the set width to float or enter it manually.
        try:
            # Should work...
            set_width = float(set_width)
        except (TypeError, ValueError):
            # if not - enter the width manually
            prompt = 'Enter the set width as a decimal fraction: '
            set_width = ui.enter_data_spec_type(prompt, float)
        prompt = 'Old British pica (0.1667") based wedge?'
        brit_pica = brit_pica or ui.yes_or_no(prompt)
        # We have the wedge name, so we can look the wedge up in known wedges
        # (no need to enter the unit arrangement manually)
        try:
            # Look up the unit arrangement
            unit_arrangement = wedge_arrangements.table[wedge_series]
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


def delete_wedge(wedge_series, set_width):
    """Used for deleting a wedge from database."""
    if ui.yes_or_no('Are you sure?'):
        if DB.delete_wedge(wedge_series, set_width):
            ui.display('Wedge deleted successfully.')


def list_wedges():
    """Lists all wedges we have."""
    data = DB.get_all_wedges()
    results = {}
    ui.display('\n' +
               'Pos.'.ljust(5) +
               'Series'.ljust(10) +
               'Set'.ljust(10) +
               'Br. pica?'.ljust(10) +
               'Unit arrangement' +
               '\n')
    for index, wedge in enumerate(data, start=1):
        index = str(index)
        # Save the wedge associated with the index
        results[index] = wedge
        # Display only wedge parameters and not ID
        number = [index.ljust(5)]
        displayed_data = [str(field).ljust(10) for field in wedge]
        ui.display(''.join(number + displayed_data))
    return results


def choose_wedge():
    """Lists wedges and lets the user choose one; returns the wedge."""
    # Do it only if we have diecases (depends on list_diecases retval)
    while True:
        ui.clear()
        ui.display('Choose a wedge:', end='\n\n')
        available_wedges = list_wedges()
        # Enter the diecase name
        prompt = 'Number of a wedge or [Enter] to exit: '
        choice = (ui.enter_data_or_blank(prompt) or
                  exceptions.return_to_menu())
        # Safeguards against entering a wrong number or non-numeric string
        try:
            # Return [series_number, set_width, brit_pica, unit_arrangement]
            (wedge_series, set_width, brit_pica,
             unit_arrangement) = available_wedges[choice]
            return (wedge_series, set_width,
                    bool(brit_pica), tuple(unit_arrangement))
        except KeyError:
            ui.confirm('Wedge number is incorrect!')
            continue


def get_wedge(wedge_series, set_width):
    """Wrapper for database function of the same name"""
    return DB.get_wedge(wedge_series, set_width)


def get_unit_arrangement(wedge_series, set_width):
    """get_unit_arrangement(wedge_series, set_width):

    Gets a unit arrangement for a given wedge.
    Returns a 17-element tuple: (0, x, y...) so that unit values can be
    addressed with row numbers (1, 2...16).
    """
    # We need to operate on lists here
    unit_arrangement = []
    try:
        # Wedge's 4th field is unit arrangement
        unit_arrangement = get_wedge(wedge_series, set_width)[3]
    except exceptions.NoMatchingData:
        # Wedge is probably not registered in database
        # Look for a unit arrangement in known UAs
        try:
            unit_arrangement = list(wedge_arrangements.table[wedge_series])
        except KeyError:
            # Unit arrangement is not known - enter it manually
            prompt = ('Enter the wedge unit values for rows 1...15 or 1...16, '
                      'separated by commas.\n')
            unit_arrangement = ui.enter_data(prompt).split(',')
        # Now we have to prepend 0 as the first position (addressed by 0)
        # This is necessary to address unit values with row numbers
        # Some wedges may have 0 in the beginning, others may not
        if unit_arrangement[0]:
            unit_arrangement = [0] + unit_arrangement
        # Some unit arrangements are for 16-step HMN or KMN wedges
        # Most of them is for 15-step wedges though
        # Fill until we have 0 + 16 values
        while True:
            try:
                # If no exception, do nothing
                if not unit_arrangement[16]:
                    pass
                break
            except IndexError:
                unit_arrangement.append(unit_arrangement[-1])
    # All done
    return tuple(unit_arrangement)


def is_old_pica(wedge_series, set_width):
    """is_old_pica:

    Checks whether this wedge is based on old British pica (.1667") or not.
    """
    try:
        wedge = get_wedge(wedge_series, set_width)
        # British pica (1 or 0) is the fourth column
        return bool(wedge[2])
    except exceptions.NoMatchingData:
        return ui.yes_or_no('Using an old British pica (.1667") wedge?')
