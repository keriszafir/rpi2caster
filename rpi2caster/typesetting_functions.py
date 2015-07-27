"""
typesetting_functions:

Contains functions used for calculating line length, justification,
setting wedge positions, breaking the line etc.
"""
from rpi2caster import exceptions
from rpi2caster.global_settings import USER_INTERFACE as ui
from rpi2caster import matrix_data
from rpi2caster import wedge_data


class Typesetter(object):
    """Typesetting class"""
    def __init__(self, diecase_id=None):
        # Begin with setting up default parameters
        self.ligatures = 3
        self.unit_shift = False
        self.compose = self.auto_compose
        self.main_alignment = self.align_left
        # Set up the spaces
        self.spaces = {'var_space_char': ' ',
                       'var_space_min_units': 4,
                       'var_space_code': 'GS2',
                       'fixed_space_char': '_',
                       'fixed_space_units': 9,
                       'fixed_space_code': 'G5',
                       'nb_space_char': '~',
                       'nb_space_units': 9,
                       'nb_space_code': 'G5',
                       'em_quad_code': 'O15'}
        # Choose a matrix case if ID not supplied
        diecase_id = diecase_id or matrix_data.choose_diecase()
        # Get matrix case parameters
        diecase_parameters = matrix_data.get_diecase_parameters(diecase_id)
        # Parse the matrix case parameters
        (type_series, self.type_size, self.wedge_series, self.set_width,
         typeface_name, self.diecase_layout) = diecase_parameters
        # Get unit arrangement for the wedge
        self.unit_arrangement = wedge_data.get_unit_arrangement(
            self.wedge_series, self.set_width)
        # Ask whether to show the matrix case layout
        # (often useful if we have to alter it)
        self.show_layout()
        # Warn if the wedge could be incompatible with the matrix case
        self.check_if_wedge_is_ok()
        # Enter the line length for typesetting, and calculate it
        # into units of self.set_width
        self.enter_line_length()
        # Ask if the composing mode is manual or automatic
        self.manual_or_automatic()
        # Choose dominant stype
        self.choose_style()
        # Set it as the current style
        self.current_style = self.main_style
        # Current units in the line - start with 0
        self.current_units = 0
        # Unit correction: -2 ... +10 applied to a character or a fragment
        self.unit_correction = 0
        # Commands for activating the typesetting functions
        self.typesetting_commands = {'^00': self.style_roman,
                                     '^01': self.style_bold,
                                     '^02': self.style_italic,
                                     '^03': self.style_smallcaps,
                                     '^04': self.style_subscript,
                                     '^05': self.style_superscript,
                                     '^CR': self.align_left,
                                     '^CL': self.align_right,
                                     '^CC': self.align_center,
                                     '^CF': self.align_both}
        # Source text generator - at the start, sets none
        self.text_source = None
        # Combination buffer - empty now
        self.buffer = []
        self.line_buffer = []
        self.output_buffer = []
        # Display info for the user
        ui.display('Composing for %s %s - %s' % (typeface_name, self.type_size,
                                                 type_series))
        ui.display('Wedge used: %s - %s set' % (self.wedge_series,
                                                self.set_width))

    def parse_and_generate(self, input_text):
        """parse_and_generate:

        Generates a sequence of characters from the input text.
        For each character, this function predicts what two next characters
        and one next character are."""
        # This variable will prevent yielding a number of subsequent chars
        # after a ligature or command has been found and yielded.
        skip_steps = 0
        for index, character in enumerate(input_text):
            if skip_steps:
                # Skip it, decrease counter, yield nothing
                skip_steps -= 1
                continue
            if character in (' ', '_', '~'):
                # This is a space: variable, fixed, non-breaking
                yield character
                continue
            elif character in ('\n', '\t'):
                # Don't care about line breaks and tabulation
                continue
            # Not space? Get the character and two next chars (triple),
            # a character and one next char (double)
            try:
                # Get two following characters if we can
                # Can cause problems at the end, so catch an exception
                triple = input_text[index:index+3]
            except IndexError:
                triple = None
            try:
                # Try the above with one additional character
                double = input_text[index:index+2]
            except IndexError:
                double = None
            # Now we have a character + two next, character + one next,
            # and a character
            # If it is a command, yield it and move on
            if triple in self.typesetting_commands:
                skip_steps = 2
                yield triple
                continue
            # Search for ligatures - 3-character first, if using
            # 3-character ligatures was specified in setup...
            if (self.ligatures == 3 and
                    triple in (matrix[0] for matrix in self.diecase_layout
                               if self.current_style in matrix[1])):
                skip_steps = 2
                yield triple
                continue
            # ...then look for 2-character ligatures...
            elif (self.ligatures >= 2 and
                  double in (matrix[0] for matrix in self.diecase_layout
                             if self.current_style in matrix[1])):
                skip_steps = 1
                yield double
                continue
            # No ligatures found? Just yield a single character.
            else:
                yield character
                continue

    def check_if_wedge_is_ok(self):
        """Checks if the wedge matches the chosen matrix case."""
        # European Didot or Fournier diecase or not?
        # Type size has the answer...
        didot = self.type_size.endswith('D')
        fournier = self.type_size.endswith('F')
        # Check if we're using an old-pica wedge
        self.brit_pica = wedge_data.is_old_pica(self.wedge_series,
                                                self.set_width)
        if (didot or fournier) and not self.brit_pica:
            ui.display('Warning: your wedge is not based on pica=0.1667"!'
                       '\nIt may lead to wrong type width.')

    def show_layout(self):
        """Asks whether to show the diecase layout. If so, prints it."""
        if ui.yes_or_no('Show the layout?'):
            ui.display('\n\n')
            matrix_data.display_diecase_layout(self.diecase_layout,
                                               self.unit_arrangement)
            ui.display('\n\n')

    def manual_or_automatic(self):
        """manual_or_automatic:

        Allows to choose if typesetting will be done with more user control.
        """
        # Manual control allows for tweaking more parameters during typesetting
        self.manual_control = ui.yes_or_no('Use manual mode? (more control) ')
        if self.manual_control:
            # Choose unit shift: yes or no?
            self.unit_shift = ui.yes_or_no('Do you use unit-shift? ')
            # Choose alignment mode
            self.choose_alignment()
            # Select the composition mode
            self.compose = self.manual_compose
            # Set custom spaces
            self.configure_spaces()
            # Set ligatures for the job
            self.set_ligatures()

    def set_ligatures(self):
        """set_ligatures:

        Choose if you want to use no ligatures, 2-character
        or 3-character ligatures.
        """
        prompt = 'Ligatures: [1] - off, [2] characters, [3] characters? '
        options = {'1': False, '2': 2, '3': 3}
        self.ligatures = ui.simple_menu(prompt, options)

    def choose_alignment(self):
        """Lets the user choose the text alignment in line or column."""
        options = {'L': self.align_left,
                   'C': self.align_center,
                   'R': self.align_right,
                   'B': self.align_both}
        message = ('Default alignment: [L]eft, [C]enter, [R]ight, [B]oth? ')
        self.main_alignment = ui.simple_menu(message, options)

    def choose_style(self):
        """Parses the diecase for available styles and lets user choose one."""
        available_styles = matrix_data.get_styles(self.diecase_layout)
        options = {str(i): style for i, style in
                   enumerate(available_styles, start=1)}
        # Nothing to choose from? Don't display the menu
        if len(options) == 1:
            self.main_style = options['1']
        # Otherwise, let user choose
        styles_list = ['%s : %s' % (x, options[x]) for x in sorted(options)]
        styles_list = ', '.join(styles_list)
        prompt = 'Choose a style: %s ' % styles_list
        self.main_style = ui.simple_menu(prompt, options)

    def get_space_code(self, space_symbol, unit_width):
        """get_space_code:

        Gets coordinates for the space of a desired unit width.
        First, looks for spaces of matching width. If it fails,
        uses unit-shift (if available) for a broader choice of spaces,
        and if this fails too, applies justification with the S-needle.

        Returns (space_code, wedge_positions).
        Adds 'S' to the space code if justification is applied. In this case,
        wedge_positions are (pos0075, pos0005) - min. (1, 1), max (15, 15).
        Wedge positions are (None, None) if justification is not applied.
        """
        # Space style: " " for low space and "_" for fixed space
        available_spaces = [sp for sp in self.diecase_layout if
                            sp[0] == space_symbol]
        spaces = []
        shifted_spaces = []
        # Gather non-shifted spaces
        for space in available_spaces:
            # Get the unit value for this space
            column = space[2]
            row = space[3]
            if row < 16:
                space_unit_width = self.unit_arrangement[row]
                space_code = column + str(row)
                spaces.append((space_unit_width, space_code))
            # Now check if unit-shift is available and gather shifted spaces
            if self.unit_shift and row > 1:
                # Convert non-shifted to shifted signals
                shifted_column = column.replace('D', 'EF') + 'D'
                shifted_row = row - 1
                shifted_space_unit_width = self.unit_arrangement[shifted_row]
                shifted_space_code = shifted_column + str(shifted_row)
                shifted_spaces.append((shifted_space_unit_width,
                                       shifted_space_code))
        # Try matching a space
        for (space_unit_width, space_code) in spaces:
            if space_unit_width == unit_width:
                return (space_code, (None, None))
        # Fell off the end of the loop - no match
        # Try with unit-shift
        for (space_unit_width, space_code) in shifted_spaces:
            if space_unit_width == unit_width:
                return (space_code, (None, None))
        # This also failed? Need to use justification wedges...
        # First try to use the spaces narrower than desired unit width,
        # and add units to them
        corrected_spaces = ({unit_width - space_unit_width: space_code
                             for (space_unit_width, space_code) in spaces
                             if space_unit_width in range(-2, 10)})
        corrected_spaces = dict(spaces)
        # Find a matching space code
        try:
            # Get the smallest positive difference
            difference = min([x for x in corrected_spaces if x > 0])
            space_code = corrected_spaces[difference] + 'S'
        except ValueError:
            # Get the negative difference closest to zero
            difference = max([x for x in corrected_spaces if x < 0])
            space_code = corrected_spaces[difference] + 'S'
        wedge_positions = self.calculate_wedges(difference)
        return (space_code, wedge_positions)

    def configure_spaces(self):
        """Chooses the spaces that will be used in typesetting."""
        # List available spaces
        # Matrix in layout is defined as follows:
        # (character, (style1, style2...)) : (column, row, unit_width)
        var_prompt = 'Variable space: [L]ow or [H]igh? '
        var_units_prompt = 'How many units min. (default: 4)? '
        fixed_prompt = 'Fixed space: [L]ow or [H]igh? '
        fix_units_prompt = 'How many units (default: 9)? '
        nbsp_prompt = 'Non-breaking space: [L]ow or [H]igh? '
        nbsp_units_prompt = 'How many units (default: 9)? '
        # Choose spaces
        spaces = {}
        # Variable space (justified) - minimum units
        variable_space = ui.simple_menu(var_prompt, {'Low': ' ', 'High': '_'})
        spaces['var_space_char'] = variable_space
        var_space_min_units = ui.enter_data_spec_type_or_blank(
            var_units_prompt, int) or 4
        spaces['var_space_min_units'] = var_space_min_units
        spaces['var_space_code'] = self.get_space_code(variable_space,
                                                       var_space_min_units)
        # Fixed space (allows line-breaking)
        fixed_space = ui.simple_menu(fixed_prompt, {'L': ' ', 'H': '_'})
        spaces['fixed_space_char'] = fixed_space
        fixed_space_units = ui.enter_data_spec_type_or_blank(
            fix_units_prompt, int) or 9
        spaces['fixed_space_units'] = fixed_space_units
        spaces['fixed_space_code'] = self.get_space_code(fixed_space,
                                                         fixed_space_units)
        # Non-breaking space
        nb_space = ui.simple_menu(nbsp_prompt, {'L': ' ', 'H': '_'})
        spaces['nb_space_char'] = nb_space
        nb_space_units = ui.enter_data_spec_type_or_blank(
            nbsp_units_prompt, int) or 9
        spaces['nb_space_units'] = nb_space_units
        spaces['nb_space_code'] = self.get_space_code(nb_space, nb_space_units)
        # Finalize setup
        self.spaces = spaces

    def translate(self, char):
        """translate:

        Translates the character to a combination of Monotype signals,
        applying single or double justification whenever necessary.
        """
        # Get the matrix data: [char, style, column, row, units]
        matrix = ([mat for mat in self.diecase_layout if mat[0] == char and
                   self.current_style in mat[1]])
        # If char units is the same as the row units, no correction is needed
        # Wedge positions for such character are null
        wedge_positions = (None, None)
        # Get coordinates
        column = matrix[2]
        row = matrix[3]
        unit_width = matrix[4]
        row_units = self.unit_arrangement[row]
        # Add or subtract current unit correction
        char_units = unit_width + self.unit_correction
        # Trying to access the 16th row with no unit shift activated
        if row == 16 and not self.unit_shift:
            self.convert_to_unit_shift()
        # Detect any spaces
        if char == ' ':
            combination = 'var_space'
        elif char == '_':
            combination = 'fixed_space'
        elif char == '~':
            combination = 'nb_space'
        # Shifted values apply only to unit-shift, start with empty
        shifted_row, shifted_column, shifted_row_units = 0, '', 0
        # If we use unit shift, we can move the diecase one row further
        # This would mean e.g. that when using the 5-series wedge, with UA:
        # 5, 6, 7, 8, 9... - we can put the 8-unit character at A5
        # (i.e. 9-unit position, normally), cast it with unit shift (add D
        # to the column sequence) and have 8 units.
        # Casting from column D will need us to replace the "D" signal,
        # that we use normally, with combined "EF".
        if self.unit_shift:
            shifted_row = row - 1
            column.replace('D', 'EF')
            shifted_column = column + 'D'
            shifted_row_units = self.unit_arrangement[shifted_row]
        # Check if the character needs unit correction at all
        # Add it if not
        if char_units == row_units:
            combination = column + str(row)
        # Try unit-shift next
        elif char_units == shifted_row_units:
            combination = shifted_column + str(shifted_row)
        # Then try using the justification wedges
        else:
            # Calculate the difference between desired width and row width
            difference = char_units - row_units
            # Cast it with the S-needle
            combination = column + 'S' + str(row)
            wedge_positions = self.calculate_wedges(difference)
        # Finally, add combination and wedge positions to the buffer
        self.buffer.append([combination, wedge_positions, char])

    def manual_compose(self):
        """manual_compose:

        Reads text fragments from input, then composes them, and justifies to a
        specified line length. Adds codes to the buffer.
        Text fragments is a list of tuples: ((text1, style1), ...)
        """

    def auto_compose(self):
        """Composes text automatically, deciding when to end the lines."""
        pass

    def enter_line_length(self):
        """enter_line_length:

        Asks user to enter line length and specify measurement units.
        Returns line length in inches for further calculations.
        """
        line_length = ui.enter_data_spec_type('Line length? : ', float)
        # Choose the measurement unit - and its equivalent in inches
        options = {'A': 0.1660,
                   'B': 0.1667,
                   'C': 0.3937,
                   'D': 0.1776,
                   'F': 0.1629}
        message = ('Measurement? [A]merican pica = Johnson, '
                   '[B]ritish pica = DTP, '
                   '[C]entimeter, [D]idot cicero, [F]ournier cicero: ')
        # Calculate the line length in inches
        inches = ui.simple_menu(message, options) * line_length
        # Choose pica based on wedge, calculate line length in picas
        if self.brit_pica:
            picas = inches / 0.1667
        else:
            picas = inches / 0.166
        # Display the info
        ui.display('Line length in inches: %s' % round(inches, 2))
        ui.display('Line length in picas: %s' % round(picas, 2))
        # 1 pica em is equal to 18 units 12-set
        # Units of a given set = 18 * pica_length * set_width / 12
        # Return the result
        self.unit_line_length = round(18 * picas * self.set_width / 12, 2)
        ui.display('Line length in %s-set units: %s' % (self.set_width,
                                                        self.unit_line_length))

    # Define some parsing functions
    def style_roman(self):
        """Sets roman for the following text."""
        self.current_style = 'roman'

    def style_bold(self):
        """Sets bold for the following text."""
        self.current_style = 'bold'

    def style_italic(self):
        """Sets italic for the following text."""
        self.current_style = 'italic'

    def style_smallcaps(self):
        """Sets small caps for the following text."""
        self.current_style = 'smallcaps'

    def style_subscript(self):
        """Sets subscript for the following text."""
        self.current_style = 'subscript'

    def style_superscript(self):
        """Sets superscript for the following text."""
        self.current_style = 'superscript'

    def fill_line(self):
        """Justify the row; applies to all alignment routines"""
        # Do the alignment and justification
        # Fill spaces number: all spaces in line will be fixed
        fill_spaces_number = 0
        while self.current_units < self.unit_line_length:
            # Add a specified number of units
            fill_spaces_number += 1
            # Add units
            self.current_units += self.spaces['fixed_space_units']
        # Return the spaces number
        return fill_spaces_number

    def align_left(self):
        """Aligns the previous chunk to the left."""
        fill_spaces_number = self.fill_line()
        spaces = ([' ' for i in range(fill_spaces_number)], 'roman')
        # Prepare the line: (content, wedge_positions)
        self.line_buffer = spaces + self.line_buffer

    def align_right(self):
        """Aligns the previous chunk to the right."""
        fill_spaces_number = self.fill_line()
        spaces = ([' ' for i in range(fill_spaces_number)], 'roman')
        # Prepare the line: (content, wedge_positions)
        self.line_buffer = self.line_buffer + spaces

    def align_center(self):
        """Aligns the previous chunk to the center."""
        fill_spaces_number = self.fill_line()
        spaces = ([' ' for i in range(fill_spaces_number / 2)], 'roman')
        # Prepare the line: (content, wedge_positions)
        self.line_buffer = spaces + self.line_buffer + spaces

    def align_both(self):
        """Aligns the previous chunk to both edges and ends the line."""
        space_count = 0

    def calculate_wedges(self, difference):
        """calculate_wedges:

        Calculates and returns wedge positions for character.
        Uses pre-calculated unit width difference between row's unit width
        and character's width (with optional corrections).
        """
        # Check if corrections are needed at all
        # (delta = 0 - no corrections, wedges at neutral position i.e. 3/8)
        if not difference:
            return (None, None)
        # Delta is in units of a given set
        # To get wedge steps, calculate delta to inches
        # First, we must know whether pica = .1667" or .166"
        if self.brit_pica:
            pica = 0.1667
        else:
            pica = 0.166
        # Calculate the inch width of delta
        # pica = 18 units * set_width / 12
        # unit_width = 12 * pica / (set width * 18)
        difference_inches = difference * 12 * pica / (18 * self.set_width)
        # We can calculate the steps of 0005 and 0075 wedges
        # Each step is calculated with 0075:3 and 0005:8 as base
        steps_0075 = difference_inches // 0.0075
        steps_0005 = difference_inches % 0.0075 // 0.0005
        # We now can calculate the wedge positions and return them
        return (3 + steps_0075, 8 + steps_0005)

    def convert_to_unit_shift(self):
        """convert_to_unit_shift:

        Sometimes using unit-shift is necessary to cast - i.e. we have to
        access 16th row on a 16x17 matrix case. This function will activate
        unit shift for the current typesetting session, but also convert
        all codes in a buffer so that they use EF instead of D signals
        in column number.
        """
        prompt = ('\nWARNING: You must use the unit-shift attachment. '
                  'Do you wish to compose for unit-shift? \n')
        self.unit_shift = ui.yes_or_no(prompt)
        if self.unit_shift():
            for (combination, _, _) in self.buffer:
                combination.replace('D', 'EF')

    def apply_justification(self):
        """apply_justification:

        Reads the buffer backwards and decides when to apply single
        or double justification (for row). Outputs the ready sequence.
        """
        line_wedge_positions = (3, 8)
        current_wedge_positions = (3, 8)
        while self.buffer:
            # Take the last combination off
            (combination, wedge_positions, character) = self.buffer.pop()
            # New line - use double justification
            if combination == 'newline':
                line_wedge_positions = wedge_positions
                self.double_justification(wedge_positions)
            # Justifying space - if wedges were set to different positions,
            # reset them to line justification positions
            elif combination == 'space':
                if current_wedge_positions != line_wedge_positions:
                    self.single_justification(line_wedge_positions)
                self.output_buffer.append(self.spaces['var_space_code'])
            # No corrections needed
            elif wedge_positions == (None, None):
                self.output_buffer.append(combination + ' // ' + character)
            # Correction needed - determine if wedges are already set
            elif wedge_positions != current_wedge_positions:
                self.single_justification(wedge_positions)
                current_wedge_positions = wedge_positions
                self.output_buffer.append(combination + ' // ' + character)

    def write_output(self):
        """Returns an output buffer - from first character codes to last/"""
        return reversed(self.output_buffer)

    def single_justification(self, wedge_positions):
        """single_justification:

        Single justification: the caster sets 0005, then 0075 + pump resumes.
        Function adds a 0075-b, then 0005-a combination to buffer.
        Supports both normal (0075, 0005, 0005+0075) and alternate
        (NK, NJ, NKJ) justification modes.
        """
        # This function is used during backwards-parsing and converting
        # the combinations sequence after typesetting
        # Codes are placed in the sequence that will be read by the caster
        # So, we get 0005 first, then 0075
        (pos0075, pos0005) = wedge_positions
        # Add 0005-N-J-pos0005 first:
        self.output_buffer.append(str(pos0005) + 'NJ 0005')
        # Add 0075-N-K-pos0075 next:
        self.output_buffer.append(str(pos0075) + 'NK 0075')
        return True

    def double_justification(self, wedge_positions):
        """double_justification:

        Double justification: the caster sets 0005+0075 and puts the line
        to the galley, then sets 0075 and pump resumes.
        Function adds a 0075-b, then 0005-a combination to buffer.
        Supports both normal (0075, 0005, 0005+0075)
        and alternate (NK, NJ, NKJ) justification modes.
        """
        (pos0075, pos0005) = wedge_positions
        # Add 0075-N-K-pos0075 first:
        self.output_buffer.append(str(pos0075) + 'NK 0075')
        # Add 0005-N-J-pos0005 next:
        self.output_buffer.append(str(pos0005) + 'NKJ 0005 0075')
        return True
