# -*- coding: utf-8 -*-
"""Inventory:

Allows to add, list and delete wedges and diecases.
"""
from . import exceptions
from . import matrix_data
wedge_data = matrix_data.wedge_data
UI = matrix_data.UI


def main_menu():
    """Display the main menu for inventory management"""
    header = ('Matrix case  and wedge management utility for rpi2caster.'
              '\n\nMain menu:\n')
    options = [(exceptions.exit_program, 'Exit',
                'Exits the inventory management'),
               (matrix_data.diecase_operations, 'Matrix operations...',
                'Work on matrix cases'),
               (wedge_data.wedge_operations, 'Wedge operations...',
                'List, add and remove wedge definitions'),
               (wedge_data.generate_wedge_collection,
                'Generate S5 collection',
                'Generates all definitions for S5 wedges for 5...14.75set')]
    while True:
        try:
            UI.menu(options, header=header, footer='')()
        except (exceptions.ReturnToMenu, exceptions.MenuLevelUp):
            pass
        except exceptions.NoMatchingData:
            UI.confirm('No matching data found!', UI.MSG_MENU)
        except exceptions.DatabaseQueryError:
            UI.confirm('Database query error!', UI.MSG_MENU)
