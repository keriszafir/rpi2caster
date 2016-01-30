# -*- coding: utf-8 -*-
"""
wedge_data

Contains higher-level functions for accessing wedge data.
This sits on top of the database module and is an abstraction layer
for other modules (like inventory, casting, typesetter).
Processes the data retrieved from database.
"""
# Default user interface
from rpi2caster.global_settings import USER_INTERFACE as ui
# Custom exceptions for rpi2caster suite
from rpi2caster import exceptions
# Constants for known normal wedge unit arrangements
from rpi2caster import wedge_arrangements
# Constants shared among modules
from rpi2caster import constants
# Database backend
from rpi2caster import database
DB = database.Database()


class Wedge(object):
    """Wedge: wedge data"""
    def __init__(self, series=None, set_width=None):
        # Default wedge data - for S5-12E
        self.series = '5'
        self.set_width = 12
        self.brit_pica = True
        self.unit_arrangement = constants.S5
        # Wedges will be setup automatically
        (self.series, self.set_width, self.brit_pica,
         self.unit_arrangement) = choose_wedge(series, set_width)

    def show_parameters(self):
        """Shows diecase's parameters"""
        data = self.get_parameters()
        info = ['%s: %s' % (desc, value) for (value, desc) in data if value]
        for item in info:
            ui.display(item)

    def get_parameters(self):
        """Gets a list of parameters"""
        data = [(self.series, 'Wedge series'),
                (self.set_width, 'Set width'),
                (self.brit_pica, 'British pica (.1667") based wedge?'),
                (' '.join([str(x) for x in self.unit_arrangement if x]),
                 'Unit arrangement for this wedge')]
        return data

    def edit(self):
        """Defines a wedge based on designation"""
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
        series = wedge_name.strip('sS')
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
            unit_arrangement = wedge_arrangements.table[series]
        except KeyError:
            while True:
                # :
                prompt = ('Enter the wedge unit values for rows 1...15 '
                          'or 1...16, separated by commas.\n')
                unit_arrangement = ui.enter_data(prompt).split(',')
                # Now we need to be sure that all whitespace is stripped,
                # and the value written to database is a list of integers
                try:
                    unit_arrangement = [int(i.strip())
                                        for i in unit_arrangement]
                except ValueError:
                    ui.display('Incorrect value - enter the values again.')
                    continue
                # Display warning if the number of steps is not
                # 15 or 16 (15 is most common, 16 was used for HMN and KMN).
                # If length is correct, tell user it's OK and finish.
                warn_min = ('Warning: the wedge you entered has < 15 steps!'
                            '\nThis is almost certainly a mistake. '
                            'Enter the values again.\n')
                warn_max = ('Warning: the wedge you entered has > 16 steps!'
                            '\nThis is almost certainly a mistake. '
                            'Enter the values again.\n')
                ua_ok = ('The wedge has %i steps. That is OK.'
                         % len(unit_arrangement))
                if len(unit_arrangement) < 15:
                    ui.display(warn_min)
                elif len(unit_arrangement) > 16:
                    ui.display(warn_max)
                else:
                    ui.display(ua_ok)
                    break
        # Now we need to adjust the arrangement...
        # Add 0 as the first item, extend the list to 17 values
        unit_arrangement = [0].append(unit_arrangement)
        while len(unit_arrangement) < 17:
            unit_arrangement.append(unit_arrangement[-1])
        # We now should have a correct arrangement...
        temp_wedge = DefaultWedge()
        temp_wedge.series = series
        temp_wedge.set_width = set_width
        temp_wedge.brit_pica = brit_pica
        temp_wedge.unit_arrangement = unit_arrangement
        ui.display('Showing the entered data...')
        temp_wedge.show_parameters()
        if ui.yes_or_no('Apply changes?'):
            self.series = temp_wedge.series
            self.set_width = temp_wedge.set_width
            self.brit_pica = temp_wedge.brit_pica
            self.unit_arrangement = temp_wedge.unit_arrangement
            return True
        else:
            return False

    def save_to_db(self):
        """Stores the wedge definition in database"""
        try:
            DB.add_wedge(self)
        except exceptions.DatabaseQueryError:
            ui.confirm('Cannot save the wedge!')

    def manipulation_menu(self):
        """A menu with all operations on a wedge"""
        self.show_parameters()
        message = ('[E]dit wedge, [S]ave to database')
        # Menu
        while True:
            self.show_parameters()
            options = {'E': self.edit,
                       'S': self.save_to_db,
                       '': exceptions.menu_level_up}
            if self.check_db():
                options['D'] = self.delete_from_db
                message += ', [D]elete from database'
            # Options constructed
            message += '\nLeave blank to exit. Your choice: '
            ui.simple_menu(message, options)()


class DefaultWedge(Wedge):
    """Default S5-12E wedge"""
    def __init__(self):
        # Default wedge data - for S5-12E
        self.series = '5'
        self.set_width = 12
        self.brit_pica = True
        self.unit_arrangement = constants.S5


def wedge_operations():
    """Wedge operations menu for inventory management"""
    while True:
        wedge = choose_wedge()
        wedge.manipulation_menu()


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


def choose_wedge(wedge_series=None, set_width=None):
    """Tries to choose a wedge of given series and set width.
    If that fails, lists wedges and lets the user choose one;
    returns the wedge."""
    # Select automatically
    try:
        wedge = DB.get_wedge(wedge_series, set_width)
    except (exceptions.NoMatchingData, exceptions.DatabaseQueryError):
        pass
    # Select manually
    while True:
        ui.clear()
        ui.display('Choose a wedge:', end='\n\n')
        available_wedges = list_wedges()
        # Enter the diecase name
        prompt = 'Number of a wedge or leave blank to exit: '
        choice = ui.enter_data_or_blank(prompt)
        if not choice:
            return False
        # Safeguards against entering a wrong number or non-numeric string
        try:
            wedge = available_wedges[choice]
        except KeyError:
            ui.confirm('Wedge number is incorrect!')
            continue
    temp_wedge = DefaultWedge()
    (temp_wedge.series, temp_wedge.set_width, brit_pica,
     temp_wedge.unit_arrangement) = wedge
    temp_wedge.brit_pica = bool(brit_pica)
    return temp_wedge
