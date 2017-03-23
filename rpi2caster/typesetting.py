# -*- coding: utf-8 -*-
"""Typesetter program"""
from contextlib import suppress
from copy import deepcopy
# from collections import deque
from . import exceptions as e
from . import typesetting_funcs as tsf
# from .justification import Box, Glue, Penalty, ObjectList
from .ribbon_controller import TypesettingContext
from .ui import UIFactory, Abort

UI = UIFactory()

# Constants for control codes
STYLE_COMMANDS = {'^00': 'r', '^rr': 'r', '^01': 'i', '^ii': 'i',
                  '^02': 'b', '^bb': 'b', '^03': 's', '^ss': 's',
                  '^04': 'l', '^ll': 'l', '^05': 'u', '^uu': 'u'}
ALIGNMENTS = {'^CR': 'left', '^CC': 'center', '^CL': 'right', '^CF': 'both'}


class Typesetting(TypesettingContext):
    """Typesetting session - choose and translate text with control codes
    into a sequence of Monotype control codes, which can be sent to
    the machine to cast composed and justified type.
    """
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
                     % self.wedge, True),
                    (self.change_measure, 'Change measure',
                     'Set new line length (current: %s)' % self.measure, True),
                    (self.change_alignment, 'Change default alignment',
                     'Set a text alignment if no code is present (current: %s)'
                     % self.default_alignment, True),
                    (self.toggle_manual_mode, 'Change the typesetting mode',
                     'Switch to automatic typesetting', self.manual_mode),
                    (self.toggle_manual_mode, 'Change the typesetting mode',
                     'Switch to manual typesetting', not self.manual_mode),
                    (self.display_diecase_layout, 'Show diecase layout',
                     'View the matrix case layout', True),
                    (self.diecase_manipulation, 'Matrix manipulation',
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
            with suppress(e.ReturnToMenu, e.MenuLevelUp,
                          Abort, EOFError, KeyboardInterrupt):
                UI.menu(menu_options(), header=header, footer='')()

    def get_paragraphs(self):
        """Parse a text into paragraphs with justification modes."""
        # Get a dict of alignment codes
        # Add a default alignment for double line break i.e. new paragraph
        alignments = deepcopy(ALIGNMENTS)
        alignments['\n\n'] = self.default_alignment
        # Make a generator function and loop over it
        paragraph_generator = token_parser(self.source, alignments,
                                           skip_unknown=False)
        paragraphs, tokens = [], []
        finished = False
        while not finished:
            try:
                token = next(paragraph_generator)
            except StopIteration:
                # Processed the whole text; any non-whitespace remaining part
                # must be also cast! (will be left-justified)
                end_text = ''.join(tokens).strip()
                if end_text:
                    last = Paragraph(end_text, self.default_alignment)
                    paragraphs.append(last)
                finished = True
            try:
                # Justification token detected - end paragrapgh
                justification = ALIGNMENTS[token]
                current_text = ''.join(tokens)
                # Reset the tokens on line currently worked on
                tokens = []
                paragraphs.append(Paragraph(current_text, justification))
            except KeyError:
                # No justification detected = keep adding more characters
                tokens.append(token)
        return paragraphs

    def compose(self):
        """Main composition engine."""
        paragraphs = self.get_paragraphs()
        for paragraph in paragraphs:
            paragraph.display_text()


class Paragraph(object):
    """A page is broken into a series of paragraphs."""
    def __init__(self, text, alignment):
        self.text = text
        self.alignment = alignment
        self.lines = []

    def display_text(self):
        """Prints the text"""
        UI.display(self.text)


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
                parameters['code'] = mat.pos + mat.comment
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
            var_sp = self.get_space(units=6)
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
        space = decode_mat(self.get_space(units=6))
        quad = decode_mat(self.get_space(units=18))
        working_mat = None
        current_wedges = None
        queue, units_left = tsf.end_casting(), 0
        # Build the whole galley, line by line
        while working_mat != {}:
            start_line()
            while units_left > 0:
                build_line()
        return queue


def token_parser(source, *token_sources, skip_unknown=True):
    """Yields tokens (characters, control sequences), one by one,
    as they are found in the source.
    input_stream - iterable;
    skip_unknown - yield only the characters found in token_sources (default),
                   otherwise, unknown characters are also yielded
    token_sources - any number of iterables containing the tokens
                    we are looking for"""
    # Collect all tokens (characters, control sequences) from token_sources
    tokens = [token for sequence in token_sources for token in sequence]
    # Determine the maximum length of a token
    max_len = max(len(t) for t in tokens)
    # We have to skip a number of subsequent input stream characters
    # after a multi-character token is encountered
    skip_steps = 0
    # Characters which will be ignored and not redirected to output
    ignored_tokens = ('\n',)
    # What if char in text not present in diecase? Hmmm...
    for index, _ in enumerate(source):
        if skip_steps:
            # Skip the characters to be skipped
            skip_steps -= 1
            continue
        for i in range(max_len, 0, -1):
            # Start from longest, end with shortest
            with suppress(TypeError, AttributeError, ValueError):
                chunk = source[index:index+i]
                skip_steps = i - 1
                if chunk in ignored_tokens:
                    break
                elif chunk in tokens or i == 1 and not skip_unknown:
                    # Make sure that the function will yield chunks of 1 char
                    yield chunk
                    break
