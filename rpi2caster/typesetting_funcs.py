# -*- coding: utf-8 -*-
"""
typesetting_functions:

Contains functions used for calculating line length, justification,
setting wedge positions, breaking the line etc.
"""
import io
from collections import deque
from . import exceptions as e
from .global_settings import UI
from .matrix_data import Diecase, Matrix
from .wedge_data import Wedge
from .typesetting_data import Ribbon

COMMANDS = {'^00': 'roman', '^01': 'bold', '^02': 'italic',
            '^03': 'smallcaps', '^04': 'subscript', '^05': 'superscript',
            '^CR': 'align_left', '^CC': 'align_center', '^CL': 'align_right',
            '^CF': 'align_both'}


class TypesettingSession(object):
    """Glue layer for the whole typesetting session"""
    def __init__(self):
        # Instantiate all we need
        self.settings = Settings()
        self.translator = Translator()
        self.input_data = InputData()
        self.output_data = OutputData()
        # Make yourself a bridge between the objects
        self.settings.session = self
        self.translator.session = self
        self.input_data.session = self
        self.output_data.session = self

    def setup(self):
        """Sets up the parameters for the session"""
        pass


class Settings(object):
    """Typesetting job settings"""
    def __init__(self, diecase_id=''):
        self.wedge = Wedge()
        self.diecase = matrix_data.Diecase(diecase_id,
                                           manual_choice=not diecase_id)

    def set_ligatures(self):
        """Chooses the max ligature size i.e. how many characters can form
        a ligature"""
        prompt = 'Ligature: how many characters? '
        self.ligatures = abs(UI.enter_data(prompt, int))

    def session_setup(self, diecase_id):
        """Sets up initial typesetting session parameters:

        -diecase
        -line length and measurement units
        -default alignment
        -spaces
        -manual mode (more control) or automatic mode (less control, faster)
        """
        # Ask if the composing mode is manual or automatic
        self._manual_or_automatic()
        # Choose dominant stype
        self._choose_style()
        # Set it as the current style
        self.current_style = self.main_style

    def _manual_or_automatic(self):
        """Allows to choose if typesetting will be done with more user control.
        """
        # Manual control allows for tweaking more parameters during typesetting
        self.manual_control = UI.confirm('Use manual mode? (more control) ')
        if self.manual_control:
            # Choose unit shift: yes or no?
            self.unit_shift = UI.confirm('Do you use unit-shift? ')
            # Choose alignment mode
            self._choose_alignment()
            # Select the composition mode
            self.compose = self.manual_compose
            # Set custom spaces
            self._configure_spaces()

    @property
    def diecase(self):
        """Gets the diecase layout from the assigned diecase."""
        diecase = self.__dict__.get('_diecase', matrix_data.Diecase())
        return diecase.layout

    @diecase.setter
    def diecase(self, diecase):
        """Sets up the diecase and chooses the wedge."""
        self.__dict__['_diecase'] = diecase
        self.wedge = diecase.wedge


class InputData(object):
    """Gets the input text, parses it, generates a sequence of characters
    or commands"""
    def __init__(self):
        # Commands for activating the typesetting functions
        self.text = ''
        self.ligatures = 3

    def open_file(self, filename=''):
        """Opens a text file with text that will be typeset"""
        while True:
            # Choose file
            filename = filename or UI.enter_input_filename()
            if not filename:
                return False
            # Open it
            with io.open(filename, 'r') as text_file:
                self.text = '\n'.join(line for line in text_file)
                return True

    def parse_input(self, input_text):
        """Generates a sequence of characters from the input text.
        For each character, this function predicts what two next characters
        and one next character are."""
        # This variable will prevent yielding a number of subsequent chars
        # after a ligature or command has been found and yielded.
        skip_steps = 0
        available_characters = COMMANDS + matrices + spaces
        # Characters which will be skipped
        ignored = ('\n',)
        # What if char in text not present in diecase? Hmmm...
        for index, _ in enumerate(input_text):
            if skip_steps:
                # Skip it, decrease counter, yield nothing
                skip_steps -= 1
                continue
            for i in range(self.ligatures, 0, -1):
                # Start from longest, end with shortest
                try:
                    char = input_text[index:index+i]
                    skip_steps = i - 1
                    if char not in ignored and char in available_characters:
                        # Try to look it up in spaces
                        yield spaces_names.get(char, char)
                        # End on first (largest) combination found
                        break
                except:
                    # Cannot generate a ligature (no more characters in input)
                    # Iterate further
                    pass
            # Should add a custom character definition here...


class OutputData(object):
    """Responsible for justifying, adding comments and outputting the
    ribbon"""
    def __init__(self):
        self.comments = False
        self.buffer = []
        self.ribbon = Ribbon()

    def _justify_line(self, mode=1):
        """justify_line(mode=1)

        Justify the row; applies to all alignment routines.
        This function supports various modes:
        0: justification only by variable spaces
        1: filling the line with one block of fixed spaces, then dividing
           the remaining units among variable spaces
        2: as above but with two blocks of fixed spaces
        3, 4... - as above but with 3, 4... blocks of fixed spaces
        Add fixed spaces only if mode is greater than 0
        """
        # Add as many fixed spaces as we can
        # Don't exceed the line length (in units) specified in setup!
        # Predict if the increment will exceed it or not
        UI.debug_info('Justifying line...')
        fill_spaces_number = 0
        space_units = self.spaces['fixed']['units']
        # Determine if we have to add any spaces (otherwise - skip the loop)
        result_length = self.current_units + mode * space_units
        # Start with no spaces
        fill_spaces = []
        while mode and result_length < self.unit_line_length:
            # Add units
            self.current_units += mode * self.spaces['fixed']['units']
            # Add a mode-dictated number of fill spaces
            fill_spaces_number += mode
            # Determine and add the space code to the line
            space = list(self.spaces['fixed']['code'])
            space.append('Fixed space %i units wide'
                         % self.spaces['fixed']['units'])
            space = tuple(space)
            # Add as many spaces as needed
            fill_spaces = [space for i in range(fill_spaces_number)]
            # Update resulting length
            result_length = self.current_units + mode * space_units
        # The remaining units must be divided among the justifying spaces
        # Determine the unit width
        remaining_units = self.unit_line_length - self.current_units
        var_space_units = remaining_units / self.current_line_var_spaces
        # Return the space chunk (that will be appended at the beginning
        # or the end of the line, or both) and unit width
        return (fill_spaces, var_space_units)

    def _start_new_line(self, var_space_units):
        """Starts a new line during typesetting"""
        # Pass the unit width to the justify method later on
        self.line_buffer.append(('newline', var_space_units, 'New line'))
        self.buffer.extend(self.line_buffer)
        self.line_buffer = []
        self.current_units = 0
        self.current_line_var_spaces = 0

    def _align_left(self):
        """Aligns the previous chunk to the left."""
        UI.debug_info('Aligning line to the left...')
        (spaces, var_space_units) = self._justify_line(mode=1)
        self.line_buffer.extend(spaces)
        self._start_new_line(var_space_units)

    def _align_right(self):
        """Aligns the previous chunk to the right."""
        UI.debug_info('Aligning line to the right...')
        (spaces, var_space_units) = self._justify_line(mode=1)
        self.line_buffer = spaces + self.line_buffer
        self._start_new_line(var_space_units)

    def _align_center(self):
        """Aligns the previous chunk to the center."""
        UI.debug_info('Aligning line to the center...')
        (spaces, var_space_units) = self._justify_line(mode=2)
        # Prepare the line: (content, wedge_positions)
        self.line_buffer = spaces + self.line_buffer + spaces
        self._start_new_line(var_space_units)

    def _align_both(self):
        """Aligns the previous chunk to both edges and ends the line."""
        UI.debug_info('Aligning line to both edges...')
        (_, var_space_units) = self._justify_line(mode=0)
        self._start_new_line(var_space_units)


class Translator(object):
    """Typesetting class"""
    def __init__(self):
        self.settings = {'unit_line_length': 0, 'current_units': 0,
                         'ligatures': 3, 'current_line_var_spaces': 0,
                         'custom_characters': [], 'current_unit_correction': 0,
                         'main_style': 'roman', 'current_style': 'roman',
                         'current_alignment': 'align_left'}
        # Set up the spaces
        self.spaces = {'var': {'high': False, 'units': 4, 'symbol': ' ',
                               'code': 'GS2'},
                       'fixed': {'high': False, 'units': 9, 'code': 'G5',
                                 'symbol': '_'},
                       'nb': {'high': False, 'units': 9, 'code': 'G5',
                              'symbol': '~'},
                       'quad': {'high': False, 'units': 18, 'code': 'O15',
                                'symbol': '\t'}}
        self.buffers = {'line': [], 'work': []}
        self.compose = self.auto_compose
        self.current_alignment = self._align_left
        # By default use automatic typesetting - less user control
        self.manual_control = False

    def _choose_alignment(self):
        """Lets the user choose the text alignment in line or column."""
        options = {'L': 'align_left',
                   'C': 'align_center',
                   'R': 'align_right',
                   'B': 'align_both'}
        message = ('Default alignment: [L]eft, [C]enter, [R]ight, [B]oth? ')
        self.settings['current_alignment'] = UI.simple_menu(message, options)

    def translate(self, char):
        """translate:

        Translates the character to a combination of Monotype signals,
        applying single or double justification whenever necessary.
        Returns an unit value of the character, so that it can be added
        to current line's unit length.
        """
        try:
            # Is that a command?
            self.typesetting_commands[char]()
            # Return 0 unit increment
            return 0
        except KeyError:
            # If not, then continue
            pass
        # Detect any spaces and quads
        for name in self.spaces:
            if char == self.spaces[name]['symbol']:
                units = self.spaces[name]['units']
                self.line_buffer.append((name, units,
                                         self.spaces[name]['desc']))
                if name == 'var':
                    self.current_line_var_spaces += 1
                return units
        # Space not recognized - so this is a character.
        # Get the matrix data: [char, style, column, row, units]
        # First try custom-defined characters (overrides)
        # If empty - try diecase layout
        matches = ([mat for mat in self.custom_characters
                    if mat[0] == char and self.current_style in mat[1]] or
                   [mat for mat in self.diecase_layout if mat[0] == char and
                    self.current_style in mat[1]])
        while not matches:
            # Nothing found in the diecase for this character?
            # Define it then yourself!
            matrix = []
            UI.display('Enter the position for character %s, style: %s'
                       % (char, self.current_style))
            row = UI.enter_data('Column? ').upper
            column = UI.enter_data('Row? ', int)
            matrix = [mat for mat in self.diecase_layout
                      if mat[2] == column and mat[3] == row]
        if len(matches) == 1:
            matrix = matches[0]
        elif len(matches) > 1:
            options = dict(enumerate(matches, start=1))
            matrix = UI.simple_menu('Choose a matrix for the character %s, '
                                    'style: %s' % (char, self.current_style),
                                    options)
            self.custom_characters.append(matrix)
        # If char units is the same as the row units, no correction is needed
        # Get coordinates
        column = matrix[2]
        row = matrix[3]
        # Combination to be cast
        combination = column + str(row)
        normal_unit_width = matrix[4]
        # Add or subtract current unit correction
        char_units = normal_unit_width + self.unit_correction
        # Finally add the translated character to output buffer
        self.line_buffer.append((combination, char_units, char))
        # Return the character's unit width
        return char_units

    def manual_compose(self):
        """Reads text fragments from input, then composes them, and justifies
        to a specified line length. Adds codes to the buffer.
        Text fragments is a list of tuples: ((text1, style1), ...)
        """

    def auto_compose(self):
        """Composes text automatically, deciding when to end the lines."""
        # Start with the empty work buffer
        self.buffer = []
        self.line_buffer = []
        self.current_units = 0
        finished = False
        # Entering a line
        while not finished:
            # Keep looping over all characters and lines
            # Try to fill the line and not hyphenate
            while self.current_units < self.unit_line_length - 50:
                # Get the character from input
                try:
                    character = next(self.text_source)
                # Translate the character (add it to buffer),
                # get unit width for the character from function's retval
                    self.current_units += self.translate(character)
                except StopIteration:
                    finished = True
                    break
            # Line composed now, align and justify it
            UI.debug_info('Line finished. Now aligning...')
            self.current_alignment()
        # Now we're done typesetting
        UI.pause('Typesetting finished!')
        return True

    def justify(self):
        """justify:

        Reads the codes buffer backwards and checks if character needs
        unit width correction (unit_difference != 0) - if so, calls
        calculate_wedges to get the 0075 and 0005 wedge positions for the char.
        If corrections are needed, applies single justification.
        If "newline" combination is found, sets the wedges for a line.
        Outputs the ready sequence.
        """
        line_wedge_positions = (3, 8)
        current_wedge_positions = (3, 8)
        var_space_high = self.spaces['var']['high']
        while self.buffer:
            # Take the last combination off
            (combination, unit_difference, comment) = self.buffer.pop()
            # If comments are enabled, and there is one, append it
            # Else, append an empty string
            comment = self.comments and comment and ' // ' + comment or ''
            # New line - use double justification;
            # instead of unit difference between row and mat, we have
            # unit width of a variable space
            if combination == 'newline':
                # Variable space parameters: (var_space_code, wedge_positions)
                var_space_code = self._get_space_code(unit_difference,
                                                      var_space_high) + 'S'
                current_wedge_positions = line_wedge_positions
                self.double_justification(line_wedge_positions)
            # Justifying space - if wedges were set to different positions,
            # reset them to line justification positions
            elif combination == 'var_space':
                if current_wedge_positions != line_wedge_positions:
                    # Set the line justification
                    current_wedge_positions = line_wedge_positions
                    single_justification(current_wedge_positions)
                self.output_buffer.append(self.spaces['var']['code'] + comment)
            elif combination == 'fixed_space':
                pass
            elif not unit_difference:
                # No corrections needed
                self.output_buffer.append(combination + comment)
            if wedge_positions != current_wedge_positions:
                # Correction needed - determine if wedges are already set
                single_justification(wedge_positions)
                current_wedge_positions = wedge_positions
                self.output_buffer.append(combination + comment)
        return self.output_buffer


class GalleyBuilder(object):
    """Builds a galley from input sequence"""
    def __init__(self, source, diecase=None, measure=0):
        self.source = (x for x in source)
        self.measure = measure or enter_measure('galley width')
        self.diecase = diecase or matrix_data.Diecase()
        self.cooldown = False
        self.mould_heatup = True
        self.quad_padding = 1

    def preheat_mould(self):
        """Appends two lines of em-quads at the end"""
        chunk = []
        if self.mould_heatup:
            quad = self.diecase.decode_matrix('O15')
            quad_qty = int(self.measure // quad.points)
            chunk = ['%s preheat' % quad] * quad_qty
            comment = 'Casting quads for mould heatup'
            chunk.extend(double_justification(comment=comment))
        return chunk * 2

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
                parameters['points'] = mat.points
                parameters['code'] = str(mat)
                parameters['lowspace'] = mat.islowspace()
            return parameters

        def start_line():
            """Starts a new line"""
            nonlocal points_left, queue
            points_left = self.measure - 2 * self.quad_padding * quad['points']
            quads = [quad['code'] + ' quad padding'] * self.quad_padding
            queue.extend(quads)

        def build_line():
            """Puts the matrix in the queue, changing the justification
            wedges if needed, and adding a space for cooldown, if needed."""
            # Declare variables in non-local scope to preserve them
            # after the function exits
            nonlocal queue, points_left, working_mat, current_wedges
            # Take a mat from stash if there is any
            working_mat = working_mat or decode_mat(next(self.source, None))
            # Try to add another character to the line
            if points_left > working_mat['points']:
                # Store wedge positions
                new_wedges = working_mat.get('wedges', (3, 8))
                # Wedges change? Drop in some single justification
                # (not needed if wedge positions were 3, 8)
                if current_wedges != new_wedges:
                    if current_wedges and current_wedges != (3, 8):
                        queue.extend(single_justification(current_wedges))
                    current_wedges = new_wedges
                # Add the mat
                queue.append(working_mat['code'])
                points_left -= working_mat['points']
                # We need to know what comes next
                working_mat = decode_mat(next(self.source, None))
                if working_mat:
                    next_points = space['points'] + working_mat['points']
                    space_needed = (points_left > next_points and not
                                    working_mat.get('lowspace', True))
                    if self.cooldown and space_needed:
                        # Add a space for matrix cooldown
                        queue.append(space['code'] + ' for cooldown')
                        points_left -= space['points']
                    # Exit and loop further
                    return
            # Finish the line
            var_sp = self.diecase.decode_matrix('G1')
            wedges = current_wedges
            current_wedges = None
            while points_left > quad['points']:
                # Coarse fill with quads
                queue.append(quad['code'] + ' coarse filling line')
                points_left -= quad['points']
            while points_left > space['points'] * 2:
                # Fine fill with fixed spaces
                queue.append(space['code'] + ' fine filling line')
                points_left -= space['points']
            if points_left >= var_sp.get_min_points():
                # Put an adjustable space if possible to keep lines equal
                if wedges:
                    queue.extend(single_justification(wedges))
                var_sp.points = points_left
                queue.append(str(var_sp))
                wedges = var_sp.wedge_positions()
            # Always cast as many quads as needed, then put the line out
            queue.extend([quad['code'] + ' quad padding'] * self.quad_padding)
            queue.extend(double_justification(wedges))
            points_left = 0

        # Store the code and wedge positions to speed up the process
        space = decode_mat(self.diecase.decode_matrix('G1'))
        quad = decode_mat(self.diecase.decode_matrix('O15'))
        working_mat = None
        current_wedges = None
        queue, points_left = end_casting(), 0
        # Build the whole galley, line by line
        while working_mat != {}:
            start_line()
            while points_left > 0:
                build_line()
        return queue + self.preheat_mould()


def single_justification(wedge_positions=(3, 8),
                         comment='Single justification'):
    """Add 0075 + pos_0075, then 0005 + pos_0005"""
    (pos_0075, pos_0005) = wedge_positions
    return pump_start(pos_0075, comment) + pump_stop(pos_0005)


def double_justification(wedge_positions=(3, 8),
                         comment='Double justification'):
    """Add 0075 + pos_0075, then 0005-0075 + pos_0005"""
    (pos_0075, pos_0005) = wedge_positions
    return pump_start(pos_0075, comment) + galley_trip(pos_0005)


def galley_trip(pos_0005=8, comment='Line to the galley'):
    """Put the line to the galley"""
    attach = comment and (' // ' + comment) or ''
    return ['NKJS 0075 0005 %s%s' % (pos_0005, attach)]


def pump_start(pos_0075=3, comment='Starting the pump'):
    """Start the pump and set 0075 wedge"""
    attach = comment and (' // ' + comment) or ''
    return ['NKS 0075 %s%s' % (pos_0075, attach)]


def pump_stop(pos_0005=8, comment='Stopping the pump'):
    """Stop the pump"""
    attach = comment and (' // ' + comment) or ''
    return ['NJS 0005 %s%s' % (pos_0005, attach)]


def end_casting():
    """Alias for ending the casting job"""
    return (pump_stop(comment='End casting') +
            galley_trip(comment='Last line out'))


def enter_measure(name='line length', default_length='25cc',
                  default_unit='cc'):
    """Enter the line length, choose measurement units
    (for e.g. British or European measurement system).
    Return length in DTP points."""
    prompt = ('Enter the desired value for %s and measurement unit:\n'
              'cc - cicero (.1776"), dd - Didot point,\n'
              'Pp - US printer\'s pica (.1660"), pp - US pica point,\n'
              'Pt - DTP pica (.1667"), pt - DTP pica point,\n'
              '", in - inch, mm - millimeter, cm - centimeter?\n '
              '(default: %s) : ' % (name, default_unit))
    factor = 1.0
    # We need an ordered sequence here
    symbols = ['Pt', 'pt', 'Pp', 'pp', 'cc', 'dd', 'cm' 'mm', 'in', '"', '']
    units = {'Pt': 12.0, 'pt': 1.0,
             'Pp': 12*0.166/0.1667, 'pp': 0.166/0.1667,
             'cc': 12*0.1776/0.1667, 'dd': 0.1776/0.1667,
             'cm': 0.3937*72, 'mm': 0.03937*72, '"': 72.0, 'in': 72.0}
    while True:
        raw_string = UI.enter_data_or_default(prompt, default_length).lower()
        try:
            for symbol in symbols:
                # Get the units
                if raw_string.endswith(symbol):
                    if not symbol:
                        symbol = default_unit
                    factor = units.get(symbol, 1)
                    input_string = raw_string.replace(symbol, '')
                    input_string = input_string.strip()
                    break
            # Calculate length in DTP points and finish
            return round(float(input_string) * factor, 2)
        except (TypeError, ValueError):
            print('Incorrect value - enter again...')
