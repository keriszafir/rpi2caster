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
               ('List matrix cases', matrix_data.list_diecases),
               ('Add a new, empty matrix case', matrix_data.add_diecase),
               ('List wedges', wedge_data.list_wedges),
               ('Add wedge', wedge_data.add_wedge),
               ('Delete wedge', wedge_data.delete_wedge)]
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

    header = ('\nMatrix case manipulation menu:\n\n'
              '[G]et matrix case parameters\n'
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
    while True:
        diecase_id = matrix_data.choose_diecase()[0]
        try:
            while True:
                ui.display('\nNow working on diecase %s' % diecase_id)
                choice = ui.simple_menu(header, options)
                ui.display('\n')
                choice(diecase_id)
                ui.confirm('[Enter] to continue...')
        except exceptions.MenuLevelUp:
            pass
