# -*- coding: utf-8 -*-
"""Typesetter program"""
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
ALIGNMENTS = {'^CR': 'left', '^CC': 'center', '^CL': 'right', '^CF': 'both'}


class SourceMixin(object):
    """Mixin for source text"""
    @property
    def source(self):
        """Source text for typesetting"""
        return self.__dict__.get('_source') or ''

    @source.setter
    def source(self, text):
        """Source setter"""
        self.__dict__['_source'] = text

    @source.setter
    def input_text(self, text):
        """Set a string of text as the typesetting source"""
        if text:
            self.source = text

    @source.setter
    def text_file(self, text_file):
        """Use a file object as a source of text"""
        # If a string or None is passed as an argument,
        # AttributeError would be raised. We'd rather ignore it.
        with suppress(AttributeError), text_file:
            self.source = ''.join(text_file.readlines())

    def edit_text(self):
        """Edits the input text"""
        self.source = UI.edit(self.source)


class DiecaseMixin(object):
    """Mixin for diecase-related operations"""
    @property
    def wedge(self):
        """Get the diecase's alternative wedge"""
        return self.diecase.alt_wedge

    @wedge.setter
    def wedge(self, wedge):
        """Set the diecase's alternative wedge"""
        self.diecase.alt_wedge = wedge

    @wedge.setter
    def wedge_name(self, wedge_name):
        """Set the wedge with a given name"""
        self.wedge = Wedge(wedge_name) if wedge_name else self.diecase.wedge

    @property
    def diecase(self):
        """Get a diecase or empty diecase"""
        return self.__dict__.get('_diecase') or EMPTY_DIECASE

    @diecase.setter
    def diecase(self, diecase):
        """Set a diecase; reset the wedge"""
        self.__dict__['_diecase'] = diecase

    @diecase.setter
    def diecase_id(self, diecase_id):
        """Set a diecase with a given diecase ID"""
        self.diecase = Diecase(diecase_id)

    @property
    def charset(self):
        """Get a {style: {char: Matrix object}} charset from the diecase"""
        return self.diecase.charset

    @property
    def spaceset(self):
        """Get a set of spaces for the diecase currently assigned."""
        return self.diecase.spaceset

    def choose_diecase(self):
        """Chooses a diecase from database"""
        self.diecase = Diecase(manual_choice=True)

    def choose_wedge(self):
        """Chooses a wedge from registered ones"""
        self.wedge = Wedge(manual_choice=True)


class RibbonMixin(object):
    """Mixin for ribbon-related operations"""
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

    @ribbon.setter
    def ribbon_file(self, ribbon_file):
        """Use a ribbon file"""
        if ribbon_file:
            self.ribbon = Ribbon(file=ribbon_file)

    @ribbon.setter
    def ribbon_id(self, ribbon_id):
        """Use a ribbon with a given ID"""
        self.ribbon = Ribbon(ribbon_id=ribbon_id)

    def choose_ribbon(self):
        """Chooses a ribbon from database or file"""
        self.ribbon = Ribbon(manual_choice=True)


class TypesettingContext(SourceMixin, DiecaseMixin, RibbonMixin):
    """Mixin for setting diecase, wedge and measure"""
    @property
    def measure(self):
        """Typesetting measure i.e. line length"""
        return self.__dict__.get('_measure') or Measure(self)

    @measure.setter
    def measure(self, measure):
        """Measure setter"""
        self.__dict__['_measure'] = measure

    @measure.setter
    def line_length(self, measure):
        """Set the line length for typesetting"""
        if measure:
            self.measure = Measure(self, measure)

    @property
    def manual_mode(self):
        """Decides whether to use an automatic or manual typesetting engine."""
        # On by default
        return self.__dict__.get('_manual_mode') or False

    @manual_mode.setter
    def manual_mode(self, manual_mode):
        """Manual mode setter"""
        self.__dict__['_manual_mode'] = True if manual_mode else False

    @property
    def default_alignment(self):
        """Default alignment:
        Determines how paragraphs ending with a double newline ("\n\n")
        and the end of the source text will be aligned.
        Valid options: "left", "right", "center", "both".
        """
        return self.__dict__.get('_default_alignment') or 'left'

    @default_alignment.setter
    def default_alignment(self, alignment):
        """Default alignment setter"""
        options = {'cr': 'left', 'cc': 'center', 'cl': 'right', 'cf': 'both',
                   'left': 'left', 'center': 'center', 'right': 'right',
                   'flat': 'both', 'both': 'both', 'f': 'both',
                   'l': 'left', 'c': 'center', 'r': 'right', 'b': 'both'}
        string = alignment.strip().replace('^', '').lower()
        value = options.get(string)
        if value:
            self.__dict__['_default_alignment'] = value

    def change_measure(self):
        """Change a line length"""
        UI.display('Set the galley width...')
        self.measure = Measure(self, manual_choice=True)

    def change_alignment(self):
        """Changes the default text alignment"""
        UI.display('Default alignment for paragraphs:')
        message = 'Choose alignment: [L]eft, [C]enter, [R]ight, [B]oth? '
        options = {'l': 'left', 'r': 'right', 'c': 'center', 'b': 'both'}
        self.default_alignment = UI.simple_menu(message, options)

    def toggle_manual_mode(self):
        """Changes the manual/automatic typesetting mode"""
        self.manual_mode = not self.manual_mode


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
                     % self.diecase.alt_wedge, True),
                    (self.change_measure, 'Change measure',
                     'Set new line length (current: %s)' % self.measure, True),
                    (self.change_alignment, 'Change default alignment',
                     'Set a text alignment if no code is present (current: %s)'
                     % self.default_alignment, True),
                    (self.toggle_manual_mode, 'Change the typesetting mode',
                     'Switch to automatic typesetting', self.manual_mode),
                    (self.toggle_manual_mode, 'Change the typesetting mode',
                     'Switch to manual typesetting', not self.manual_mode),
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
            with suppress(e.ReturnToMenu, e.MenuLevelUp,
                          UI.Abort, EOFError, KeyboardInterrupt):
                UI.menu(menu_options(), header=header, footer='')()

    def get_paragraphs(self):
        """Parse a text into paragraphs with justification modes."""
        # Get a dict of alignment codes
        # Add a default alignment for double line break i.e. new paragraph
        alignments = {k: v for (k, v) in ALIGNMENTS.items()}
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
