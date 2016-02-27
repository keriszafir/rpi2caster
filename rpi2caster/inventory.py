# -*- coding: utf-8 -*-
"""Inventory:

Allows to add, list and delete wedges and diecases.
"""
from . import exceptions as e
from . import matrix_data
from . import wedge_data
from .global_settings import UI


def main_menu():
    """Display the main menu for inventory management"""
    header = ('Matrix case  and wedge manipulation utility for rpi2caster.'
              '\n\nInventory Management menu:\n')
    options = [(e.exit_program, 'Exit',
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
        except (e.ReturnToMenu, e.MenuLevelUp):
            pass
        except e.NoMatchingData:
            UI.pause('No matching data found!', UI.MSG_MENU)
        except e.DatabaseQueryError:
            UI.pause('Database query error!', UI.MSG_MENU)
