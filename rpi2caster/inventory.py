# -*- coding: utf-8 -*-
"""Inventory:

Allows to add, list and delete wedges and diecases.
"""
from rpi2caster.global_settings import USER_INTERFACE as ui
from rpi2caster import exceptions
from rpi2caster import matrix_data
from rpi2caster import wedge_data


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
            ui.hold_on_exit()
        except exceptions.ReturnToMenu:
            pass
        except exceptions.NoMatchingData:
            ui.display('No matching data found!')
            ui.hold_on_exit()
        except exceptions.DatabaseQueryError:
            ui.display('Database query error!')
            ui.hold_on_exit()
        except (KeyboardInterrupt, exceptions.ExitProgram):
            ui.exit_program()


def matrix_menu():
    """Matrix manipulation functions - creating, viewing, editing, deleting"""

    def another(*args):
        """Exits the diecase manipulation menu"""
        exceptions.menu_level_up()

    def menu(*args):
        """Exits to main menu"""
        exceptions.return_to_menu()

    def work_on_diecase():
        """Options for working on a chosen diecase"""
        header = ('[G]et matrix case parameters\n'
                  '[S]how matrix case layout\n'
                  '[E]dit matrix case layout\n'
                  '[C]lear matrix case layout\n'
                  '[L]oad matrix case layout from file\n'
                  '[D]elete the matrix case\n\n'
                  '[Enter] to choose another diecase\n'
                  '[M] to return to main menu\n\n'
                  'Your choice? : ')
        options = {'S': matrix_data.show_diecase,
                   'L': matrix_data.load_layout,
                   'E': matrix_data.edit_diecase,
                   'C': matrix_data.clear_diecase,
                   'D': matrix_data.delete_diecase,
                   'G': matrix_data.get_diecase_parameters,
                   '': another,
                   'M': menu}
        prompt = 'Number of a diecase or [Enter] to exit: '
        try:
            while True:
                choice = (ui.enter_data_or_blank(prompt) or
                          exceptions.return_to_menu())
                # Safeguards against entering a wrong value
                try:
                    diecase_id = available_diecases[choice]
                    break
                except (KeyError,
                        exceptions.NoMatchingData,
                        exceptions.DatabaseQueryError):
                    ui.display('Diecase number is incorrect!')
            while True:
                ui.display('\nNow working on diecase %s\n\n' % diecase_id)
                choice = ui.simple_menu(header, options)
                ui.display('\n')
                choice(diecase_id)
                ui.confirm('[Enter] to continue...')
        except exceptions.MenuLevelUp:
            pass

    header = ('Matrix case manipulation menu\n\n'
              '[A]dd diecase\n'
              '[C]hoose diecase to work on\n\n'
              '[Enter] to go back to main menu\n\n'
              'Your choice? : ')
    options = {'A': matrix_data.add_diecase,
               'C': work_on_diecase,
               '': menu}
    while True:
        try:
            available_diecases = matrix_data.list_diecases()
            ui.simple_menu(header, options)()
            ui.confirm('[Enter] to continue...')
        except exceptions.MenuLevelUp:
            pass


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
        ui.confirm('[Enter] to continue...')
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
