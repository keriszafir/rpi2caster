# -*- coding: utf-8 -*-
"""Typesetter program"""

import io
from . import exceptions as e
from . import typesetting_funcs as tsf
from .measure import Measure
from .typesetting_data import Ribbon
from .matrix_data import Diecase, diecase_operations
from .wedge_data import Wedge
from .global_settings import UI


class Typesetting(object):
    """Typesetting session - choose and translate text with control codes
    into a sequence of Monotype control codes, which can be sent to
    the machine to cast composed and justified type.
    """
    def __init__(self, text_file='', ribbon_file='', diecase_id='',
                 manual_mode=False):

        self.measure = Measure(manual=False)
        self.ribbon = Ribbon(ribbon_file)
        self.diecase = Diecase(diecase_id)
        self.source = text_file and open_file(text_file) or []
        # Use a manual compositor (user decides where to break the line)
        # or automatic compositor (hyphenation and justification is done
        # automatically with the Knuth-Plass algorithm)
        self.compositor = (manual_mode and ManualCompositor(self) or
                           AutoCompositor(self))

    def main_menu(self):
        """Main menu for the typesetting utility."""
        def finish():
            """Stop the loop"""
            nonlocal finished
            finished = True

        def choose_diecase():
            """Chooses a diecase from database"""
            self.diecase = Diecase(manual_choice=True)

        def choose_wedge():
            """Chooses a wedge from registered ones"""
            self.diecase.alt_wedge = Wedge(manual_choice=True)

        def change_measure():
            """Change a line length"""
            UI.display('Set the galley width...')
            self.measure = Measure()

        def menu_options():
            """Build a list of options, adding an option"""
            # Options are described with tuples:
            # (function, description, condition)
            opts = [(finish, 'Exit', 'Exits the program'),
                    (choose_diecase, 'Select diecase',
                     'Select a matrix case from database (current: %s)'
                     % (self.diecase or 'not selected')),
                    (choose_wedge, 'Select wedge',
                     'Enter a wedge designation (current: %s)'
                     % self.diecase.alt_wedge),
                    (change_measure, 'Change measure',
                     'Set new line length (current: %s)' % self.measure),
                    (self.diecase.show_layout, 'Show diecase layout',
                     'View the matrix case layout'),
                    (diecase_operations, 'Matrix manipulation',
                     'Work on matrix cases')]
            # Built a list of menu options conditionally
            return [(function, description, long_description)
                    for (function, description, long_description) in opts]

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


class Compositor(object):
    """Composition engine class"""
    def __init__(self, context):
        self.context = context


class ManualCompositor(Compositor):
    """Manual composition - allows more control over typesetting process"""
    def __init__(self, context):
        super().__init__(context)


class AutoCompositor(Compositor):
    """Automatic composition with hyphenation and justification"""
    def __init__(self, context):
        super().__init__(context)


def open_file(filename=''):
    """Opens a text file with text that will be typeset"""
    while True:
        # Choose file
        try:
            filename = filename or UI.enter_input_filename()
        except e.ReturnToMenu:
            return []
        # Open it
        with io.open(filename, 'r') as text_file:
            return text_file.readlines()
