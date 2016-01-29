# -*- coding: utf-8 -*-
"""Inventory:

Allows to add, list and delete wedges and diecases.
"""
from rpi2caster import exceptions
from rpi2caster import matrix_data
wedge_data = matrix_data.wedge_data
ui = matrix_data.ui


def main_menu():
    """Display the main menu for inventory management"""
    header = ('Matrix case  and wedge management utility for rpi2caster.'
              '\n\nMain menu:\n')
    options = [('Exit program', exceptions.exit_program),
               ('Matrix manipulation...', matrix_menu),
               ('Wedge manupulation...', wedge_menu)]
    while True:
        try:
            ui.menu(options, header=header, footer='')()
            ui.confirm('Finished!', ui.MSG_MENU)
        except exceptions.ReturnToMenu:
            pass
        except exceptions.NoMatchingData:
            ui.confirm('No matching data found!', ui.MSG_MENU)
        except exceptions.DatabaseQueryError:
            ui.confirm('Database query error!', ui.MSG_MENU)
        except (KeyboardInterrupt, EOFError, exceptions.ExitProgram):
            ui.exit_program()


def matrix_menu():
    """Matrix manipulation functions - creating, viewing, editing, deleting"""

    def menu(*args):
        """Exits to main menu"""
        exceptions.return_to_menu()

    def work_on_diecase():
        """Options for working on a chosen diecase"""
        header = ('Choose: \n[E]dit layout, [C]lear layout, '
                  '[L]oad new layout from file, [S]ave layout to file, \n'
                  '[D]elete the matrix case from database,\n'
                  '[Enter] to go back to matrix manipulation menu. : ')
        options = {'L': matrix_data.load_layout,
                   'S': matrix_data.export_layout,
                   'E': matrix_data.edit_diecase,
                   'C': matrix_data.clear_diecase,
                   'D': matrix_data.delete_diecase,
                   '': menu}
        try:
            while True:
                try:
                    ui.clear()
                    ui.display('Now working on diecase %s' % diecase_id)
                    matrix_data.show_diecase(diecase_id)
                    # Choose what to do
                    ui.simple_menu(header, options)(diecase_id)
                except exceptions.MenuLevelUp:
                    pass
        except exceptions.ReturnToMenu:
            # Go back to diecase selection
            pass

    prompt = ('Choose diecase from list by entering its number, '
              'or [A] to add a new diecase, '
              'or [Enter] to go back to main menu.\n\n'
              'Your choice? : ')
    options = {'A': matrix_data.add_diecase,
               '': menu}
    while True:
        # First list what diecases we have
        ui.clear()
        ui.display('\nList of available diecases:\n')
        available_diecases = matrix_data.list_diecases()
        all_options = {}
        all_options.update(options)
        all_options.update(available_diecases)
        choice = ui.simple_menu(prompt, all_options)
        try:
            if choice in available_diecases.values():
                # Safeguards against entering a wrong value
                diecase_id = choice
                work_on_diecase()
            elif choice in options.values():
                # Choice is a function
                choice()
        except exceptions.MenuLevelUp:
            pass
        except (KeyError,
                exceptions.NoMatchingData,
                exceptions.DatabaseQueryError):
            ui.display('Diecase number is incorrect!')


def wedge_menu():
    """Wedge manipulation functions - listing, adding, deleting"""

    def menu():
        """Exits to main menu"""
        exceptions.return_to_menu()

    def delete_wedge():
        """Lets user select and delete a wedge from database."""
        prompt = 'Number of a wedge to delete? (leave blank to exit): '
        choice = (ui.enter_data_or_blank(prompt) or
                  exceptions.return_to_menu())
        # Safeguards against entering a wrong number or non-numeric string
        try:
            (wedge_series, set_width, _, _) = available_wedges[choice]
            wedge_data.delete_wedge(wedge_series, set_width)
        except KeyError:
            ui.display('Wedge number is incorrect!')
        ui.confirm()
        # Ask for confirmation
    header = ('\nWedge manipulation menu:\n\n'
              '[A]dd new wedge\n'
              '[D]elete a wedge\n\n'
              '[Enter] to return to main menu\n\n'
              'Your choice? : ')
    options = {'A': wedge_data.add_wedge,
               'D': delete_wedge,
               '': menu}
    while True:
        available_wedges = wedge_data.list_wedges()
        try:
            ui.simple_menu(header, options)()
        except exceptions.MenuLevelUp:
            pass
