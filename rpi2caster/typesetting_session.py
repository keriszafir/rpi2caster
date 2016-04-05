# -*- coding: utf-8 -*-
"""Typesetter program"""

from . import exceptions as e
from .typesetting_data import Ribbon
from .matrix_data import Diecase, Matrix
from .wedge_data import Wedge
from .global_settings import UI


class Typesetting(object):
    """Typesetting session - choose and translate text with control codes
    into a sequence of Monotype control codes, which can be sent to
    the machine to cast composed and justified type.
    """
    def __init__(self, text_file='', ribbon_file='', diecase_id='',
                 wedge_name='', manual_mode=False):

        self.ribbon = Ribbon(ribbon_file)
        self.diecase = Diecase(diecase_id, manual_choice=not diecase_id)
        self.wedge = Wedge(wedge_name or self.ribbon.wedge_name or
                           self.diecase.wedge.name or '')
        # Use a manual compositor (user decides where to break the line)
        # or automatic compositor (hyphenation and justification is done
        # automatically with the Knuth-Plass algorithm)
        if manual_mode:
            self.compositor = True
        else:
            self.compositor = False

    def main_menu(self):
        """Main menu for the typesetting utility."""
        def finish():
            """Stop the loop"""
            nonlocal finished
            finished = True

        def menu_options():
            """Build a list of options, adding an option if condition is met"""
            # Options are described with tuples:
            # (function, description, condition)
            diecase = bool(self.diecase)
            opts = [(finish, 'Exit', 'Exits the program', True),
                    ]
            # Built a list of menu options conditionally
            return [(function, description, long_description)
                    for (function, description, long_description, condition)
                    in opts if condition]

        header = ('rpi2caster - CAT (Computer-Aided Typecasting) '
                  'for Monotype Composition or Type and Rule casters.\n\n'
                  'Composition Menu:')
        # Keep displaying the menu and go back here after any method ends
        finished = False
        while not finished:
            # Catch any known exceptions here
            try:
                UI.menu(menu_options(), header=header, footer='')()
            except (e.ReturnToMenu, e.MenuLevelUp, KeyboardInterrupt):
                # Will skip to the end of the loop, and start all over
                pass
