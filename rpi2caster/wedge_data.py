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
        # Ask for wedge name and set width as it is written on the wedge
        prompt = ('Wedge name or leave blank to abort: ')
        # For countries that use comma as decimal delimiter, convert to point:
        wedge_name = ui.enter_data_or_blank(prompt).replace(',', '.').upper()
        if not wedge_name:
            return False
        elif 'AK' in wedge_name:
            # For the old designation of 5-series wedges
            set_width = wedge_name.replace('AK', '').strip()
            ui.display('This is a 5-series wedge, designated as "AK"')
            series = '5'
        elif 'BO' in wedge_name:
            # For the old designation of 5-series wedges
            set_width = wedge_name.replace('AK', '').strip()
            ui.display('This is a 221-series wedge, designated as "BO"')
            series = '221'
        elif 'TPWR' in wedge_name:
            ui.display('This is a typewriter wedge.')
            set_width = wedge_name.replace('TPWR', '').strip()
            series = 'TPWR'
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
            set_width = ui.enter_data(prompt, float)
        # Check if it has a different pica as a base for unit calculations
        if wedge_name.endswith('E'):
            # For wedges made for European countries that use the Didot system
            # (these wedges were based on the old British pica,
            # i.e. 18units 12set type was .1667" wide)
            ui.display('The letter E at the end means that this wedge was '
                       'made for European market, and based on pica =.1667".')
            brit_pica = True
        else:
            prompt = 'Old British pica (0.1667") based wedge?'
            brit_pica = ui.yes_or_no(prompt)
        # We have the wedge name, so we can look the wedge up in known wedges
        # (no need to enter the unit arrangement manually)
        try:
            # Look up the unit arrangement
            unit_arrangement = list(wedge_arrangements.table[series])
        except KeyError:
            while True:
                # Enter manually:
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
        # Add 0 as the first item
        unit_arrangement = [0] + unit_arrangement
        # Keep filling the list until we reach 16 non-zero steps
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

    def delete_from_db(self):
        """Deletes the wedge from database"""
        ans = ui.yes_or_no('Are you sure?')
        if ans and DB.delete_wedge(self):
            ui.display('Wedge definition deleted successfully from database.')

    def save_to_db(self):
        """Stores the wedge definition in database"""
        try:
            DB.add_wedge(self)
        except exceptions.DatabaseQueryError:
            ui.confirm('Cannot save the wedge!')

    def check_db(self):
        """Checks if the wedge is in database"""
        return DB.check_wedge(self)

    def manipulation_menu(self):
        """A menu with all operations on a wedge"""
        # Menu
        try:
            while True:
                # Keep working on a chosen diecase
                ui.display('\n')
                self.show_parameters()
                ui.display('\n')
                messages = ['[E]dit wedge, [S]ave to database']
                options = {'M': exceptions.return_to_menu,
                           'E': self.edit,
                           'S': self.save_to_db,
                           '': exceptions.menu_level_up}
                if self.check_db():
                    options['D'] = self.delete_from_db
                    messages.append(', [D]elete from database')
                # Options constructed
                messages.append('\n[M] to return to menu; leave blank to '
                                'choose/create another wedge.')
                messages.append('\nYour choice: ')
                message = ''.join(messages)
                ui.simple_menu(message, options)()
        except exceptions.MenuLevelUp:
            # Exit wedge manipulation menu
            pass


class Wedge(DefaultWedge):
    """Wedge: wedge data"""
    def __init__(self, series='', set_width=0):
        DefaultWedge.__init__(self)
        # Wedges will be setup automatically
        temp_wedge = choose_wedge(series, set_width)
        self.series = temp_wedge.series
        self.set_width = temp_wedge.set_width
        self.brit_pica = temp_wedge.brit_pica
        self.unit_arrangement = temp_wedge.unit_arrangement


def wedge_operations():
    """Wedge operations menu for inventory management"""
    try:
        ui.display('Wedge manipulation: choose a wedge or define a new one')
        while True:
            # Choose a wedge or initialize a new one
            wedge = choose_wedge()
            wedge.manipulation_menu()
    except exceptions.ReturnToMenu:
        # Exit wedge operations
        pass


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
    ui.confirm()


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
        # Save the wedge associated with the index
        results[index] = wedge
        # Modify the wedge data for display
        unit_arrangement = wedge[-1]
        # Display only wedge parameters and not unit arrangement
        data_string = ''.join([str(field).ljust(10) for field in wedge[:-1]])
        values_string = ' '.join([str(x) for x in unit_arrangement if x])
        ui.display(str(index).ljust(5) + data_string + values_string)
    return results


def choose_wedge(wedge_series='', set_width=0):
    """Tries to choose a wedge of given series and set width.
    If that fails, lists wedges and lets the user choose one;
    returns the wedge."""
    # Select automatically
    try:
        wedge = DB.get_wedge(wedge_series, set_width)
    except (exceptions.NoMatchingData, exceptions.DatabaseQueryError):
        while True:
            ui.display('\nChoose a wedge:', end='\n')
            try:
                available_wedges = list_wedges()
            except (exceptions.NoMatchingData, exceptions.DatabaseQueryError):
                ui.display('No wedges found in database. '
                           'Using default S5-12E...')
                return DefaultWedge()
            # Enter the diecase name
            prompt = 'Enter number (leave blank to work with default S5-12E): '
            choice = ui.enter_data_or_blank(prompt, int)
            if not choice:
                return DefaultWedge()
            # Safeguards against entering a wrong number or non-numeric string
            try:
                wedge = available_wedges[choice]
                break
            except KeyError:
                ui.confirm('Wedge number is incorrect!')
                continue
    temp_wedge = DefaultWedge()
    (temp_wedge.series, temp_wedge.set_width, brit_pica,
     temp_wedge.unit_arrangement) = wedge
    temp_wedge.brit_pica = bool(brit_pica)
    return temp_wedge
