# -*- coding: utf-8 -*-
"""
wedge_data

Contains higher-level functions for accessing wedge data.
This sits on top of the database module and is an abstraction layer
for other modules (like inventory, casting, typesetter).
Processes the data retrieved from database.
"""
from copy import deepcopy
# Default user interface
from .global_settings import USER_INTERFACE as UI
# Custom exceptions for rpi2caster suite
from . import exceptions as e
# Constants for known normal wedge unit arrangements
from . import wedge_arrangements
# Constants shared among modules
from . import constants
# Database backend
from . import database
DB = database.Database()


class DefaultWedge(object):
    """Default S5-12E wedge"""
    def __init__(self):
        # Default wedge data - for S5-12E
        self.series = '5'
        self.set_width = 12
        self.brit_pica = True
        self.unit_arrangement = constants.S5

    def show_parameters(self):
        """Shows diecase's parameters"""
        data = self.get_parameters()
        info = ['%s: %s' % (desc, value) for (value, desc) in data if value]
        for item in info:
            UI.display(item)

    def get_parameters(self):
        """Gets a list of parameters"""
        data = [('\n', '\nWedge data'),
                (self.series, 'Wedge series'),
                (self.set_width, 'Set width'),
                (self.brit_pica, 'British pica (.1667") based wedge?'),
                (' '.join([str(x) for x in self.unit_arrangement if x]),
                 'Unit arrangement for this wedge')]
        return data

    def copy(self):
        """Copies itself and returns an independent object"""
        return deepcopy(self)

    def edit(self, wedge_name=None):
        """Defines a wedge based on designation"""
        # Ask for wedge name and set width as it is written on the wedge
        prompt = ('Wedge name or leave blank to abort: ')
        # For countries that use comma as decimal delimiter, convert to point:
        wedge_name = wedge_name or UI.enter_data_or_blank(prompt)
        wedge_name = wedge_name.replace(',', '.').upper()
        if not wedge_name:
            return False
        elif 'AK' in wedge_name:
            # For the old designation of 5-series wedges
            series, set_width = '5', wedge_name.replace('AK', '').strip()
            UI.display('This is a 5-series wedge, designated as "AK"')
        elif 'BO' in wedge_name:
            # For the old designation of 5-series wedges
            series, set_width = '221', wedge_name.replace('AK', '').strip()
            UI.display('This is a 221-series wedge, designated as "BO"')
        elif 'TPWR' in wedge_name:
            UI.display('This is a typewriter wedge.')
            series, set_width = 'TPWR', wedge_name.replace('TPWR', '').strip()
        else:
            (series, set_width) = wedge_name.strip('SE').split('-')
        # Now get the set width
        # We now should have a wedge series and set width, as strings.
        # Convert the set width to float or enter it manually.
        try:
            set_width = float(set_width)
        except ValueError:
            # Will be set later
            prompt = 'Enter the set width as a decimal fraction: '
            set_width = UI.enter_data(prompt, float)
        # Check if it has a different pica as a base for unit calculations
        prompt = 'Old British pica (0.1667") based wedge?'
        brit_pica = wedge_name.endswith('E') or UI.yes_or_no(prompt)
        # We have the wedge name, so we can look the wedge up in known wedges
        # (no need to enter the unit arrangement manually)
        try:
            # Look up the unit arrangement
            unit_arrangement = [x for x in wedge_arrangements.table[series]]
        except KeyError:
            while True:
                # Enter manually:
                prompt = ('Enter the wedge unit values for rows 1...15 '
                          'or 1...16, separated by commas.\n')
                # Now we need to be sure that all whitespace is stripped,
                # and the value written to database is a list of integers
                try:
                    unit_arrangement = [int(i.strip()) for i in
                                        UI.enter_data(prompt).split(',')]
                except ValueError:
                    UI.display('Incorrect value - enter the values again.')
                    continue
                # Display warning if the number of steps is not
                # 15 or 16 (15 is most common, 16 was used for HMN and KMN).
                if 15 <= len(unit_arrangement) <= 16:
                    break
                UI.display('Wedge must have 15 or 16 steps - re-enter values.')
        # Now we need to adjust the arrangement...
        # Add 0 as the first item
        unit_arrangement = [0] + unit_arrangement
        # Keep filling the list until we reach 16 non-zero steps
        while len(unit_arrangement) < 17:
            unit_arrangement.append(unit_arrangement[-1])
        # We now should have a correct arrangement...
        if UI.yes_or_no('Apply changes?'):
            self.series = series
            self.set_width = set_width
            self.brit_pica = brit_pica
            self.unit_arrangement = unit_arrangement

    def delete_from_db(self):
        """Deletes the wedge from database"""
        ans = UI.yes_or_no('Are you sure?')
        if ans and DB.delete_wedge(self):
            UI.display('Wedge definition deleted successfully from database.')
            return True

    def save_to_db(self):
        """Stores the wedge definition in database"""
        try:
            DB.add_wedge(self)
            UI.confirm('Wedge saved successfully.')
            return True
        except e.DatabaseQueryError:
            UI.display()
            self.show_parameters()
            UI.confirm('Cannot save the wedge - check if it is already there.')
            UI.display()
            return False

    def check_db(self):
        """Checks if the wedge is in database"""
        return DB.check_wedge(self)

    def manipulation_menu(self):
        """A menu with all operations on a wedge"""
        # Menu
        try:
            while True:
                # Keep working on a chosen diecase
                UI.display('\n')
                self.show_parameters()
                UI.display('\n')
                messages = ['[E]dit wedge, [S]ave to database']
                options = {'M': e.return_to_menu,
                           'E': self.edit,
                           'S': self.save_to_db,
                           '': e.menu_level_up}
                if self.check_db():
                    options['D'] = self.delete_from_db
                    messages.append(', [D]elete from database')
                # Options constructed
                messages.append('\n[M] to return to menu; leave blank to '
                                'choose/create another wedge.')
                messages.append('\nYour choice: ')
                message = ''.join(messages)
                UI.simple_menu(message, options)()
        except e.MenuLevelUp:
            # Exit wedge manipulation menu
            return True


class Wedge(DefaultWedge):
    """Wedge: wedge data"""
    def __init__(self, wedge_series=None, set_width=None):
        super().__init__()
        try:
            wedge_data = (wedge_series and set_width and
                          DB.get_wedge(wedge_series, set_width) or
                          choose_wedge() or None)
            (self.series, self.set_width, self.brit_pica,
             self.unit_arrangement) = wedge_data
        except (TypeError, ValueError, e.NoMatchingData, e.DatabaseQueryError):
            UI.display('Wedge choice failed. Using S5-12 instead.')


def wedge_operations():
    """Wedge operations menu for inventory management"""
    try:
        UI.display('Wedge manipulation: choose a wedge or define a new one')
        while True:
            # Choose a wedge or initialize a new one
            Wedge().manipulation_menu()
    except e.ReturnToMenu:
        # Exit wedge operations
        return True


def generate_wedge_collection(series='5', brit_pica=True):
    """Generates a collection of wedges for all set widths from 5.0 to 14.75
    for a given series (S5 by default)"""
    widths = [x + y for x in range(5, 15) for y in (0, 0.25, 0.5, 0.75)]
    for set_width in widths:
        wedge = DefaultWedge()
        wedge.series = series
        wedge.set_width = set_width
        wedge.brit_pica = brit_pica
        unit_arrangement = [0] + [x for x in wedge_arrangements.table[series]]
        while len(unit_arrangement) < 17:
            unit_arrangement.append(unit_arrangement[-1])
        wedge.unit_arrangement = unit_arrangement
        wedge.save_to_db()
    list_wedges()
    UI.confirm()


def list_wedges():
    """Lists all wedges we have."""
    data = DB.get_all_wedges()
    results = {}
    UI.display('\n' +
               'Pos.'.ljust(5) +
               'Series'.ljust(10) +
               'Set'.ljust(10) +
               'Br. pica?'.ljust(10) +
               'Unit arrangement' +
               '\n')
    for index, wedge in enumerate(data, start=1):
        # Save the wedge associated with the index
        results[index] = wedge
        # Modify the wedge data for display
        unit_arrangement = wedge[-1]
        # Display only wedge parameters and not unit arrangement
        data_string = ''.join([str(field).ljust(10) for field in wedge[:-1]])
        values_string = ' '.join([str(x) for x in unit_arrangement if x])
        UI.display(str(index).ljust(5) + data_string + values_string)
    return results


def choose_wedge():
    """Tries to choose a wedge of given series and set width.
    If that fails, lists wedges and lets the user choose one;
    returns the wedge."""
    prompt = 'Enter number (leave blank to work with default S5-12E): '
    while True:
        try:
            UI.display('\nChoose a wedge:', end='\n')
            available_wedges = list_wedges()
            choice = UI.enter_data_or_blank(prompt, int)
            return choice and available_wedges[choice] or None
        except KeyError:
            UI.confirm('Wedge number is incorrect!')
        except (e.NoMatchingData, e.DatabaseQueryError):
            UI.display('No wedges found in database.')
            return None
