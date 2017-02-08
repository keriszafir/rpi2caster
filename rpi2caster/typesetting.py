# -*- coding: utf-8 -*-
"""Typesetter program"""

import io
from contextlib import suppress
# from collections import deque
from . import exceptions as e
from . import typesetting_funcs as tsf
# from .justification import Box, Glue, Penalty, ObjectList
from .measure import Measure
from .typesetting_data import Ribbon
from .matrix_data import Diecase, diecase_operations, EMPTY_DIECASE
from .wedge_data import Wedge
from .rpi2caster import UI

# Constants for control codes
STYLE_COMMANDS = {'^00': 'r', '^rr': 'r', '^01': 'i', '^ii': 'i',
                  '^02': 'b', '^bb': 'b', '^03': 's', '^ss': 's',
                  '^04': 'l', '^ll': 'l', '^05': 'u', '^uu': 'u'}
ALIGNMENTS = {'^CR': tsf.justify_left, '^CC': tsf.justify_center,
              '^CL': tsf.justify_right, '^CF': tsf.justify_both,
              '\n\n': tsf.justify_both}


class TypesettingContext(object):
    """Mixin for setting diecase, wedge and measure"""
    def __init__(self, text_file='', ribbon_file='', ribbon_id='',
                 diecase_id='', wedge_name='', measure=''):
        self.diecase = Diecase(diecase_id)
        self.measure = Measure(self, measure)
        self.ribbon = Ribbon(filename=ribbon_file, ribbon_id=ribbon_id)
        self.source = open_file(text_file) if text_file else ''
        self.wedge = Wedge(wedge_name) if wedge_name else self.diecase.wedge

    @property
    def ribbon(self):
        """Ribbon for the casting session"""
        return self.__dict__.get('_ribbon') or Ribbon()

    @ribbon.setter
    def ribbon(self, ribbon):
        """Ribbon setter"""
        self.__dict__['_ribbon'] = ribbon or Ribbon()
        if ribbon.diecase_id:
            self.diecase = Diecase(ribbon.diecase_id)
        if ribbon.wedge_name:
            self.wedge = Wedge(ribbon.wedge_name)

    @property
    def wedge(self):
        """Get the diecase's alternative wedge"""
        return self.diecase.alt_wedge

    @wedge.setter
    def wedge(self, wedge):
        """Set the diecase's alternative wedge"""
        self.diecase.alt_wedge = wedge

    @property
    def diecase(self):
        """Get a diecase or empty diecase"""
        return self.__dict__.get('_diecase') or EMPTY_DIECASE

    @property
    def charset(self):
        """Get a {style: {char: Matrix object}} charset from the diecase"""
        return self.diecase.charset

    @property
    def spaceset(self):
        """Get a set of spaces for the diecase currently assigned."""
        return self.diecase.spaceset

    @diecase.setter
    def diecase(self, diecase):
        """Set a diecase; reset the wedge"""
        self.__dict__['_diecase'] = diecase

    def choose_diecase(self):
        """Chooses a diecase from database"""
        self.diecase = Diecase(manual_choice=True)

    def choose_wedge(self):
        """Chooses a wedge from registered ones"""
        self.wedge = Wedge(manual_choice=True)

    def change_measure(self):
        """Change a line length"""
        UI.display('Set the galley width...')
        self.measure = Measure(self, manual_choice=True)

    def choose_ribbon(self):
        """Chooses a ribbon from database or file"""
        self.ribbon = Ribbon(manual_choice=True)

    def edit_text(self):
        """Edits the input text"""
        self.source = UI.edit(self.source)


class Typesetting(TypesettingContext):
    """Typesetting session - choose and translate text with control codes
    into a sequence of Monotype control codes, which can be sent to
    the machine to cast composed and justified type.
    """

    def __init__(self, text_file='', ribbon_file='', ribbon_id='',
                 diecase_id='', wedge_name='', measure='', manual=True):
        super().__init__(text_file, ribbon_file, ribbon_id, diecase_id,
                         wedge_name, measure)
        self.compose = self.manual_compose if manual else self.auto_compose

    def main_menu(self):
        """Main menu for the typesetting utility."""
        def finish():
            """Stop the loop"""
            nonlocal finished
            finished = True

        def menu_options():
            """Build a list of options, adding an option"""
            # Options are described with tuples:
            # (function, description, condition)
            opts = [(finish, 'Exit', 'Exits the program', True),
                    (self.edit_text, 'Edit the source text',
                     'Enter or edit the text you want to translate', True),
                    (self.compose, 'Typesetting', 'Translate the text',
                     self.diecase and self.source),
                    (self.choose_diecase, 'Select diecase',
                     'Select a matrix case from database (current: %s)'
                     % (self.diecase or 'not selected'), True),
                    (self.choose_wedge, 'Select wedge',
                     'Enter a wedge designation (current: %s)'
                     % self.diecase.alt_wedge, True),
                    (self.change_measure, 'Change measure',
                     'Set new line length (current: %s)' % self.measure, True),
                    (self.diecase.show_layout, 'Show diecase layout',
                     'View the matrix case layout', True),
                    (diecase_operations, 'Matrix manipulation',
                     'Work on matrix cases', True)]
            # Built a list of menu options conditionally
            return [(func, desc, long_desc)
                    for (func, desc, long_desc, condition) in opts
                    if condition]

        header = ('rpi2caster - CAT (Computer-Aided Typecasting) '
                  'for Monotype Composition or Type and Rule casters.\n\n'
                  'Composition Menu:')
        # Keep displaying the menu and go back here after any method ends
        finished = False
        while not finished:
            with suppress(e.ReturnToMenu, e.MenuLevelUp, KeyboardInterrupt):
                UI.menu(menu_options(), header=header, footer='')()

    def manual_compose(self):
        """Manual composition engine. As the end of the line is reached,
        the user decides where to break (with or without hyphenation)."""
        print(self.charset)
        print('roman', self.charset.get('r'))
        print('bold', self.charset.get('b'))
        input('Enter to continue')

    def auto_compose(self):
        """Automatic composition engine. Hyphenates and justifies on its own,
        giving less control over the typesetting proces, but saving a lot
        of time for the user, especially for repetitive work."""
        pass


class InputText(object):
    """Gets the input text, parses it, generates a sequence of characters
    or commands"""

    def __init__(self, context, text):
        self.context = context
        self.text = text

    def parse_input(self):
        """Generates a sequence of characters from the input text.
        For each character, this function predicts what two next characters
        and one next character are."""
        # Cache the character set and spaces instead of generating
        # them ad hoc
        charset = self.context.diecase.charset
        spaceset = self.context.diecase.spaceset
        # This variable will prevent yielding a number of subsequent chars
        # after a ligature or command has been found and yielded.
        skip_steps = 0
        # Default style is roman
        style = 'r'
        # Characters which will be skipped
        ignored_tokens = ('\n',)
        # Determine the length of character combinations parsed
        # Min = command length i.e. 3
        # Max = ligature length - dictated by diecase
        max_len = max(3, self.context.diecase.ligature_length)
        # What if char in text not present in diecase? Hmmm...
        for index, _ in enumerate(self.text):
            if skip_steps:
                # Skip the characters to be skipped
                skip_steps -= 1
                continue
            for i in range(max_len, 0, -1):
                # Start from longest, end with shortest
                with suppress(KeyError):
                    chunk = self.text[index:index+i]
                    skip_steps = i - 1
                    if chunk in ignored_tokens:
                        break
                    elif chunk in STYLE_COMMANDS:
                        style = STYLE_COMMANDS.get(chunk, 'r')
                        break
                    else:
                        yield spaceset.get(chunk) or charset[style][chunk]
                        break

class Paragraph(object):
    """A page is broken into a series of paragraphs."""
    def __init__(self, text, alignment):
        self.text = text
        self.alignment = alignment
        self.lines = []


class GalleyBuilder(object):
    """Builds a galley from input sequence"""
    def __init__(self, context, source):
        self.source = (x for x in source)
        self.diecase = context.diecase
        self.units = context.measure.wedge_set_units
        # Cooldown: whether to separate sorts with spaces
        self.cooldown_spaces = False
        # Fill line: will add quads/spaces nutil length is met
        self.fill_line = True
        self.quad_padding = 1

    def make_ribbon(self):
        """Instantiates a Ribbon() object from whatever we've generated"""
        pass

    def build_galley(self):
        """Builds a line of characters from source"""
        def decode_mat(mat):
            """Gets the mat's parameters and stores them
            to avoid recalculation"""
            parameters = {}
            if mat:
                parameters['wedges'] = mat.wedge_positions()
                parameters['units'] = mat.units
                parameters['code'] = str(mat)
                parameters['lowspace'] = mat.is_low_space
            return parameters

        def start_line():
            """Starts a new line"""
            nonlocal units_left, queue
            units_left = self.units - 2 * self.quad_padding * quad['units']
            quads = [quad['code'] + ' quad padding'] * self.quad_padding
            queue.extend(quads)

        def build_line():
            """Puts the matrix in the queue, changing the justification
            wedges if needed, and adding a space for cooldown, if needed."""
            # Declare variables in non-local scope to preserve them
            # after the function exits
            nonlocal queue, units_left, working_mat, current_wedges
            # Take a mat from stash if there is any
            working_mat = working_mat or decode_mat(next(self.source, None))
            # Try to add another character to the line
            # Empty mat = end of line, start filling
            if units_left > working_mat.get('units', 1000):
                # Store wedge positions
                new_wedges = working_mat.get('wedges', (3, 8))
                # Wedges change? Drop in some single justification
                # (not needed if wedge positions were 3, 8)
                if current_wedges != new_wedges:
                    if current_wedges and current_wedges != (3, 8):
                        queue.extend(tsf.single_justification(current_wedges))
                    current_wedges = new_wedges
                # Add the mat
                queue.append(working_mat['code'])
                units_left -= working_mat['units']
                # We need to know what comes next
                working_mat = decode_mat(next(self.source, None))
                if working_mat:
                    next_units = space['units'] + working_mat['units']
                    space_needed = (units_left > next_units and not
                                    working_mat.get('lowspace', True))
                    if self.cooldown_spaces and space_needed:
                        # Add a space for matrix cooldown
                        queue.append(space['code'] + ' for cooldown')
                        units_left -= space['units']
                    # Exit and loop further
                    return
            # Finish the line
            var_sp = self.diecase.decode_matrix('G1')
            wedges = current_wedges
            current_wedges = None
            if self.fill_line:
                while units_left > quad['units']:
                    # Coarse fill with quads
                    queue.append(quad['code'] + ' coarse filling line')
                    units_left -= quad['units']
                while units_left > space['units'] * 2:
                    # Fine fill with fixed spaces
                    queue.append(space['code'] + ' fine filling line')
                    units_left -= space['units']
                if units_left >= var_sp.get_min_units():
                    # Put an adjustable space if possible to keep lines equal
                    if wedges:
                        queue.extend(tsf.single_justification(wedges))
                    var_sp.units = units_left
                    queue.append(str(var_sp))
                    wedges = var_sp.wedge_positions()
            # Always cast as many quads as needed, then put the line out
            queue.extend([quad['code'] + ' quad padding'] * self.quad_padding)
            queue.extend(tsf.double_justification(wedges or (3, 8)))
            units_left = 0

        # Store the code and wedge positions to speed up the process
        space = decode_mat(self.diecase.decode_matrix('G1'))
        quad = decode_mat(self.diecase.decode_matrix('O15'))
        working_mat = None
        current_wedges = None
        queue, units_left = tsf.end_casting(), 0
        # Build the whole galley, line by line
        while working_mat != {}:
            start_line()
            while units_left > 0:
                build_line()
        return queue


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
            return '\n'.join(text_file.readlines())
