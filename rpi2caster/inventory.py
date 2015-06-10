#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Inventory:

Allows to add, list and delete wedges and diecases.
"""
from __future__ import absolute_import
from rpi2caster import text_ui as ui
from rpi2caster import database
from rpi2caster import exceptions
DB = database.Database()


# Placeholders for functionality not implemented yet:
def list_diecases():
    """Not implemented yet"""
    pass


def show_diecase_layout():
    """Not implemented yet"""
    pass


def add_diecase():
    """Not implemented yet"""
    pass


def edit_diecase():
    """Not implemented yet"""
    pass


def clear_diecase():
    """Not implemented yet"""
    pass


def delete_diecase():
    """Not implemented yet"""
    pass


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
    # Repeat the procedure all over again, if necessary
    # (can be exited by raising an exception)
    while True:
        # Enter the wedge name:
        wedge_name = ''
        set_width = ''
        brit_pica = None
        unit_arrangement = None
        ui.clear()
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
        while not wedge_name:
        # Ask for the wedge name and set width as it is written on the wedge
            prompt = ('Wedge name: ')
            wedge_name = ui.enter_data(prompt).upper()
        # For countries that use comma as decimal delimiter, convert to point:
            wedge_name = wedge_name.replace(',', '.')
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
        # (these wedges were based on the old British pica, i.e. 18 units 12 set
        # type was .1667" wide)
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
            options = {'A' : False, 'B' : True}
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
        # Enter manually f failed
        if not unit_arrangement:
        # Check if we have the values hardcoded already:
            prompt = ('Enter the wedge unit values for rows 1...15 or 1...16, '
                      'separated by commas.\n')
            while not unit_arrangement:
            # Make it a list at once
                unit_arrangement = ui.enter_data(prompt).split(',')
        # Now we need to be sure that all whitespace is stripped,
        # and the value written to database is a list of integers
            unit_arrangement = [int(step.strip()) for step in unit_arrangement]
        # Display warning if the number of steps is anything other than
        # 15 or 16 (15 is most common, 16 was used for HMN and KMN systems).
        # If length is correct, tell user it's OK.
            warn_min = ('Warning: the wedge you entered has less than 15 steps!'
                        '\nThis is almost certainly a mistake.\n')
            warn_max = ('Warning: the wedge you entered has more than 16 steps!'
                        '\nThis is almost certainly a mistake.\n')
            ua_ok = ('The wedge has %i steps. That is OK.'
                     % len(unit_arrangement))
            if len(unit_arrangement) < 15:
                ui.display(warn_min)
            elif len(unit_arrangement) > 16:
                ui.display(warn_max)
            else:
                ui.display(ua_ok)
        # Display a summary:
        summary = {'Wedge' : wedge_name,
                   'Set width' : set_width,
                   'British pica wedge?' : brit_pica}
        for parameter in summary:
            ui.display(parameter, ':', summary[parameter])
        # Loop over all values in wedge's unit arrangement, and display them:
        for i, step in enumerate(unit_arrangement):
            ui.display('Step', i+1, 'unit value:', step, '\n')
        # Subroutines:
        def commit_wedge():
            """Give feedback to user on result"""
            if DB.add_wedge(wedge_name, set_width, brit_pica, unit_arrangement):
                ui.display('Wedge added successfully.')
                return True
            else:
                ui.display('Failed to add wedge!')
                return False
        def reenter():
            """Loop over again"""
            ui.enter_data('Enter parameters again from scratch... ')
        def return_to_menu():
            """Return to menu (main menu will catch the exception)"""
            raise exceptions.ReturnToMenu
        def exit_program():
            """Exit program (main menu will catch the exception)"""
            raise exceptions.ExitProgram
        # Confirmation menu:
        message = ('\nCommit wedge to database? \n'
                   '[Y]es, [N]o (enter values again), [M]enu or [E]xit? ')
        options = {'Y' : commit_wedge,
                   'N' : reenter,
                   'M' : return_to_menu,
                   'E' : exit_program}
        ans = ui.simple_menu(message, options).upper()
        options[ans]()


def delete_wedge():
    """Used for deleting a wedge from database.

    Lists wedges
    """
    ui.clear()
    # Do it only if we have wedges (depends on list_wedges retval)
    while list_wedges():
        try:
            prompt = 'Enter the wedge ID to delete (leave blank to exit): '
            w_id = ui.enter_data(prompt)
            if not w_id:
                raise exceptions.ReturnToMenu
            w_id = int(w_id)
        except (ValueError, TypeError):
            # Not number? Skip wedge deletion, start over.
            pass
        if DB.delete_wedge(w_id):
            ui.display('Wedge deleted successfully.')
        ui.clear()


def list_wedges():
    """Lists all wedges we have."""
    results = DB.get_all_wedges()
    if not results:
        raise exceptions.NoMatchingData
    ui.display('\n' + 'wedge id'.ljust(15)
               + 'wedge No'.ljust(15)
               + 'set width'.ljust(15)
               + 'Brit. pica?'.ljust(15)
               + 'Unit arrangement'
               + '\n')
    for wedge in results:
        ui.display(''.join([str(field).ljust(15) for field in wedge]))
    return True


def main_menu():
    """Display the main menu for inventory management"""
    def exit_program():
        """Helper subroutine, throws an exception to exit the program"""
        raise exceptions.ExitProgram

    options = [('Exit program', exit_program),
               ('List matrix cases', list_diecases),
               ('Show matrix case layout', show_diecase_layout),
               ('Add a new, empty matrix case', add_diecase),
               ('Edit matrix case layout', edit_diecase),
               ('Clear matrix case layout', clear_diecase),
               ('Delete matrix case', delete_diecase),
               ('List wedges', list_wedges),
               ('Add wedge', add_wedge),
               ('Delete wedge', delete_wedge)]
    while True:
        header = 'Setup utility for rpi2caster CAT.\nMain menu:'
        try:
            ui.menu(options, header=header, footer='')()
            ui.hold_on_exit()
        except exceptions.ReturnToMenu:
            pass
        except exceptions.NoMatchingData:
            ui.display('No matching data found!')
            ui.hold_on_exit()
        except (KeyboardInterrupt, exceptions.ExitProgram):
            ui.exit_program()
