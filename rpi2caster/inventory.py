# -*- coding: utf-8 -*-

"""Inventory:

Allows to add, list and delete wedges and diecases.
"""
from rpi2caster import text_ui as ui
from rpi2caster import exceptions
from rpi2caster import matrix_data
from rpi2caster import wedge_data


def main_menu():
    """Display the main menu for inventory management"""
    options = [('Exit program', exceptions.exit_program),
               ('List matrix cases', matrix_data.list_diecases),
               ('Show matrix case layout', matrix_data.show_diecase_layout),
               ('Add a new, empty matrix case', matrix_data.add_diecase),
               ('Edit matrix case layout', matrix_data.edit_diecase),
               ('Clear matrix case layout', matrix_data.clear_diecase),
               ('Delete matrix case', matrix_data.delete_diecase),
               ('List wedges', wedge_data.list_wedges),
               ('Add wedge', wedge_data.add_wedge),
               ('Delete wedge', wedge_data.delete_wedge)]
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
        except exceptions.DatabaseQueryError:
            ui.display('Database query error!')
            ui.hold_on_exit()
        except (KeyboardInterrupt, exceptions.ExitProgram):
            ui.exit_program()
