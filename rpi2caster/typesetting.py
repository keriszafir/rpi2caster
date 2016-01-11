# -*- coding: utf-8 -*-
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
    def __init__(self):
        # No input data yet
        self.type_size = None
        self.wedge_series = None
        self.diecase_layout = None
        self.set_width = None
        self.unit_arrangement = None
        self.unit_line_length = None
        self.brit_pica = None
        # Begin with setting up default parameters
        self.ligatures = 3
        self.unit_shift = False
        self.compose = self.auto_compose
        self.current_alignment = self._align_left
        # Set up the spaces
        self.spaces = {'var': {'high': False,
                               'units': 4,
                               'symbol': ' ',
                               'code': 'GS2'},
                       'fixed': {'high': False,
                                 'units': 9,
                                 'code': 'G5',
                                 'symbol': '_'},
                       'nb': {'high': False,
                              'units': 9,
                              'code': 'G5',
                              'symbol': '~'},
                       'quad': {'high': False,
                                'units': 18,
                                'code': 'O15',
                                'symbol': '\t'}}
        # Current units in the line - start with 0
        self.current_units = 0
        # Justifying spaces number
        self.current_line_var_spaces = 0
        # Unit correction: -2 ... +10 applied to a character or a fragment
        self.unit_correction = 0
        # Commands for activating the typesetting functions
        self.typesetting_commands = {'^00': self._style_roman,
                                     '^01': self._style_bold,
                                     '^02': self._style_italic,
                                     '^03': self._style_smallcaps,
                                     '^04': self._style_subscript,
                                     '^05': self._style_superscript,
                                     '^CR': self._align_left,
                                     '^CL': self._align_right,
                                     '^CC': self._align_center,
                                     '^CF': self._align_both}
        # Source text generator - at the start, sets none
        self.text_source = None
        # Custom character definitions - e.g. if multiple alternatives
        # are found
        self.custom_characters = []
        # Add comments to the ribbon?
        self.comments = True
        # Work with roman by default
        self.main_style = 'roman'
        self.current_style = 'roman'
        # By default use automatic typesetting - less user control
        self.manual_control = False
        # Combination buffer - empty now
        self.line_buffer = []
        self.buffer = []
        self.output_buffer = []

    def session_setup(self, diecase_id):
        """Sets up initial typesetting session parameters:

        -diecase
        -line length and measurement units
        -default alignment
        -spaces
        -manual mode (more control) or automatic mode (less control, faster)
        """
        # Choose a matrix case if ID not supplied
        diecase = matrix_data.choose_diecase(diecase_id)
        # Parse the matrix case parameters
        (diecase_id, type_series, self.type_size,
         self.wedge_series, self.set_width,
         typeface_name, self.diecase_layout) = diecase
        # Get unit arrangement for the wedge
        self.unit_arrangement = wedge_data.get_unit_arrangement(
            self.wedge_series, self.set_width)
        # Warn if the wedge could be incompatible with the matrix case
        self._check_if_wedge_is_ok()
        # Enter the line length for typesetting, and calculate it
        # into units of self.set_width
        self._enter_line_length()
        # Ask if the composing mode is manual or automatic
        self._manual_or_automatic()
        # Choose dominant stype
        self._choose_style()
        # Set it as the current style
        self.current_style = self.main_style
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
        spaces_names = {self.spaces[name]['symbol']: name
                        for name in self.spaces}
        # Construct a list of characters that the diecase contains
        command_codes = [code for code in self.typesetting_commands]
        matrices = [mat[0] for mat in self.diecase_layout
                    if self.current_style in mat[1]]
        spaces = [space for space in spaces_names]
        available_characters = command_codes + matrices + spaces
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
                        try:
                            yield spaces_names[char]
                        except KeyError:
                            yield char
                        # End on first (largest) combination found
                        break
                except IndexError:
                    # Cannot generate a ligature (no more characters in input)
                    # Iterate further
                    pass
            # Should add a custom character definition here...

    def _check_if_wedge_is_ok(self):
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
            ui.display_diecase_layout(self.diecase_layout,
                                      self.unit_arrangement)
            ui.display('\n\n')

    def _manual_or_automatic(self):
        """manual_or_automatic:

        Allows to choose if typesetting will be done with more user control.
        """
        # Manual control allows for tweaking more parameters during typesetting
        self.manual_control = ui.yes_or_no('Use manual mode? (more control) ')
        if self.manual_control:
            # Choose unit shift: yes or no?
            self.unit_shift = ui.yes_or_no('Do you use unit-shift? ')
            # Choose alignment mode
            self._choose_alignment()
            # Select the composition mode
            self.compose = self.manual_compose
            # Set custom spaces
            self._configure_spaces()
            # Set ligatures for the job
            self._set_ligatures()

    def _set_ligatures(self):
        """set_ligatures:

        Choose if you want to use no ligatures, 2-character
        or 3-character ligatures.
        """
        prompt = 'Ligatures: [1] - off, [2] characters, [3] characters? '
        options = {'1': False, '2': 2, '3': 3}
        self.ligatures = ui.simple_menu(prompt, options)

    def _choose_alignment(self):
        """Lets the user choose the text alignment in line or column."""
        options = {'L': self._align_left,
                   'C': self._align_center,
                   'R': self._align_right,
                   'B': self._align_both}
        message = ('Default alignment: [L]eft, [C]enter, [R]ight, [B]oth? ')
        self.current_alignment = ui.simple_menu(message, options)

    def _choose_style(self):
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
        prompt = 'Choose a dominant style: %s ' % styles_list
        self.main_style = ui.simple_menu(prompt, options)

    def _get_space_code(self, desired_unit_width, high_space=False):
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
        # Space style: " " for low space and "_" for high space
        space_symbols = {'□': False, ' ': False, '_': True, '▣': True}
        available_spaces = [sp for sp in self.diecase_layout if
                            sp[0] == space_symbols[high_space]]
        spaces = []
        # Gather non-shifted spaces
        for space in available_spaces:
            # Get the unit value for this space
            column = space[2]
            row = space[3]
            if row < 16:
                space_unit_width = self.unit_arrangement[row]
                space_code = column + str(row)
                spaces.append((space_unit_width, space_code))
        # Try matching a first available space
        for (space_unit_width, space_code) in spaces:
            unit_difference = desired_unit_width - space_unit_width
            if 0 <= unit_difference < 10:
                # Unit correction: add max 10
                return space_code
        else:
            # Return the space that is narrower and units can be added
            return False

    def _configure_spaces(self):
        """Chooses the spaces that will be used in typesetting."""
        # To make lines shorter
        enter = ui.enter_data_or_blank
        enter_type = ui.enter_data_spec_type_or_blank
        get_space_code = self._get_space_code
        y_n = ui.yes_or_no
        # List available spaces
        # Matrix in layout is defined as follows:
        # (character, (style1, style2...)) : (column, row, unit_width)
        var_units_prompt = 'How many units min. (default: 4)? '
        var_symbol_prompt = ('Variable space symbol in text file? '
                             '(default: " ") ? ')
        fixed_units_prompt = 'How many units (default: 9)? '
        fixed_symbol_prompt = ('Fixed space symbol in text file? '
                               '(default: "_") ? ')
        nbsp_units_prompt = 'How many units (default: 9)? '
        nbsp_symbol_prompt = ('Non-breaking space symbol in text file? '
                              '(default: "~") ? ')
        quad_symbol_prompt = ('Em-quad symbol in text file? '
                              '(default: "\\t") ? ')
        # Choose spaces
        spaces = {}
        # Variable space (justified) - minimum units
        # Ask if low or high and save the choice
        variable_space = y_n('Variable: is a high space? ')
        spaces['var']['high'] = variable_space
        # Ask for minimum number of units of given set for the variable space
        spaces['var']['units'] = enter_type(var_units_prompt, int) or 4
        # Variable space code will be determined during justification
        # Don't do it now yet - we don't know the wedge positions
        spaces['var']['code'] = 'GS2'
        # Ask for the symbol representing the space in text
        spaces['var']['symbol'] = enter(var_symbol_prompt) or ' '
        # Fixed space (allows line-breaking)
        # Ask if low or high and save the choice
        spaces['fixed']['high'] = y_n('Fixed: is a high space? ')
        # Ask for unit-width of this space
        spaces['fixed']['units'] = enter_type(fixed_units_prompt, int) or 9
        # Determine fixed space code
        spaces['fixed']['code'] = get_space_code(spaces['fixed']['high'],
                                                 spaces['fixed']['units'])
        # Ask for the symbol representing the space in text
        spaces['fixed']['symbol'] = enter(fixed_symbol_prompt) or '_'
        # Non-breaking space
        # Ask if low or high and save the choice
        spaces['nb']['high'] = y_n('Non-breaking: is a high space? ')
        # Ask for unit-width of this space
        spaces['nb']['units'] = enter_type(nbsp_units_prompt, int) or 9
        # Determine non-breaking space code
        spaces['nb']['code'] = get_space_code(spaces['nb']['high'],
                                              spaces['nb']['units'])
        # Ask for the symbol representing the space in text
        spaces['nb']['symbol'] = enter(nbsp_symbol_prompt) or '~'
        # Set up the quad code arbitrarily
        spaces['quad']['code'] = 'O15'
        spaces['quad']['high'] = False
        spaces['quad']['units'] = 18
        # Em quad symbol choice
        spaces['quad']['symbol'] = enter(quad_symbol_prompt) or '\t'
        # Finalize setup
        self.spaces = spaces

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
            ui.display('Enter the position for character %s, style: %s'
                       % (char, self.current_style))
            row = ui.enter_data('Column? ').upper
            column = ui.enter_data_spec_type('Row? ', int)
            matrix = [mat for mat in self.diecase_layout
                      if mat[2] == column and mat[3] == row]
        if len(matches) == 1:
            matrix = matches[0]
        elif len(matches) > 1:
            options = dict(enumerate(matches, start=1))
            matrix = ui.simple_menu('Choose a matrix for the character %s, '
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
        """manual_compose:

        Reads text fragments from input, then composes them, and justifies to a
        specified line length. Adds codes to the buffer.
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
            ui.debug_info('Line finished. Now aligning...')
            self.current_alignment()
        # Now we're done typesetting
        ui.confirm('Typesetting finished! [Enter] to continue...')
        return True

    def _enter_line_length(self):
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
    def _style_roman(self):
        """Sets roman for the following text."""
        self.current_style = 'roman'

    def _style_bold(self):
        """Sets bold for the following text."""
        self.current_style = 'bold'

    def _style_italic(self):
        """Sets italic for the following text."""
        self.current_style = 'italic'

    def _style_smallcaps(self):
        """Sets small caps for the following text."""
        self.current_style = 'smallcaps'

    def _style_subscript(self):
        """Sets subscript for the following text."""
        self.current_style = 'subscript'

    def _style_superscript(self):
        """Sets superscript for the following text."""
        self.current_style = 'superscript'

    def _start_new_line(self, var_space_units):
        """Starts a new line during typesetting"""
        # Pass the unit width to the justify method later on
        self.line_buffer.append(('newline', var_space_units, 'New line'))
        self.buffer.extend(self.line_buffer)
        self.line_buffer = []
        self.current_units = 0
        self.current_line_var_spaces = 0

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
        ui.debug_info('Justifying line...')
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

    def _align_left(self):
        """Aligns the previous chunk to the left."""
        ui.debug_info('Aligning line to the left...')
        (spaces, var_space_units) = self._justify_line(mode=1)
        self.line_buffer.extend(spaces)
        self._start_new_line(var_space_units)

    def _align_right(self):
        """Aligns the previous chunk to the right."""
        ui.debug_info('Aligning line to the right...')
        (spaces, var_space_units) = self._justify_line(mode=1)
        self.line_buffer = spaces + self.line_buffer
        self._start_new_line(var_space_units)

    def _align_center(self):
        """Aligns the previous chunk to the center."""
        ui.debug_info('Aligning line to the center...')
        (spaces, var_space_units) = self._justify_line(mode=2)
        # Prepare the line: (content, wedge_positions)
        self.line_buffer = spaces + self.line_buffer + spaces
        self._start_new_line(var_space_units)

    def _align_both(self):
        """Aligns the previous chunk to both edges and ends the line."""
        ui.debug_info('Aligning line to both edges...')
        (_, var_space_units) = self._justify_line(mode=0)
        self._start_new_line(var_space_units)

    def convert_to_unit_shift(self):
        """convert_to_unit_shift:

        Sometimes using unit-shift is necessary to cast - i.e. we have to
        access 16th row on a 16x17 matrix case. This function will activate
        unit shift for the current typesetting session, but also convert
        all codes in a buffer so that they use EF instead of D signals
        in column number.
        """
        prompt = ('\nWARNING: You are trying to use 16th row on a matrix case.'
                  '\nFor that you must use the unit-shift attachment. '
                  'Do you wish to compose for unit-shift? \n')
        self.unit_shift = ui.yes_or_no(prompt)
        if self.unit_shift:
            for (combination, _, _) in self.buffer:
                combination.replace('D', 'EF')

    def correct_units(self, combination, char_units, comment):
        """Determines if unit correction is needed for a character"""
        (column, row) = parse_combination(combination)
        row_units = self.unit_arrangement[row]
        # Is the character width correction needed at all?
        unit_difference = char_units - row_units
        # Tell us what we are translating
        ui.debug_info('Character:', comment, 'style:', self.current_style)
        ui.debug_info('Matrix at:', combination)
        # Trying to access the 16th row with no unit shift activated
        if row == 16 and not self.unit_shift:
            self.convert_to_unit_shift()
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
            # Check if unit shift is needed for this character (if it's on)
            if unit_difference and char_units == shifted_row_units:
                # No unit difference between char and row
                # (that's why we used unit shift)
                unit_difference = 0
                # Info for user
                ui.debug_info('Correcting the width by unit shift...')
                ui.debug_info('Character units:', char_units,
                              'row units:', row_units)
                # Override previous combination
                combination = shifted_column + str(shifted_row)
            elif row == 16:
                # Use unit shift for these even if you have to add units
                unit_difference = char_units - shifted_row_units
                ui.debug_info('Casting from row 16 - unit shift is necessary')
                ui.debug_info('Character units:', char_units,
                              'row units:', shifted_row_units)
                combination = shifted_column + str(shifted_row)
            # Combination after corrections
            ui.debug_info('Combination with unit shift:', combination, '')
        # Check if we need unit corrections at all...
        if not unit_difference:
            ui.debug_info('No unit corrections needed.')
        elif unit_difference << 0:
            ui.debug_info('Taking away %s units' % -1 * unit_difference)
        elif unit_difference >> 0:
            ui.debug_info('Adding %s units' % unit_difference)

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
                    self.single_justification(current_wedge_positions)
                self.output_buffer.append(self.spaces['var']['code'] + comment)
            elif combination == 'fixed_space':
                pass
            elif not unit_difference:
                # No corrections needed
                self.output_buffer.append(combination + comment)
            if wedge_positions != current_wedge_positions:
                # Correction needed - determine if wedges are already set
                self.single_justification(wedge_positions)
                current_wedge_positions = wedge_positions
                self.output_buffer.append(combination + comment)
        return self.output_buffer

    def single_justification(self, wedge_positions):
        """single_justification:

        Single justification: the caster sets 0005, then 0075 + pump resumes.
        Function adds a 0075-b, then 0005-a combination to buffer.
        Supports both normal (0075, 0005, 0005+0075) and alternate
        (NK, NJ, NKJ) justification modes. Adds an extra "S" signal
        to assist setting the 0005 and 0075 levers in place (some machines
        have a problem with that).
        """
        # This function is used during backwards-parsing and converting
        # the combinations sequence after typesetting
        # Codes are placed in the sequence that will be read by the caster
        # So, we get 0005 first, then 0075
        (pos0075, pos0005) = wedge_positions
        # Inform the user about wedge positions
        comment1 = ' // Pump off; setting 0005 to ' + str(pos0005)
        comment2 = ' // Setting 0075 wedge to ' + str(pos0075) + ', pump on...'
        # Add 0005-N-J-S-pos0005 first:
        self.output_buffer.append(str(pos0005) + 'NJS 0005' + comment1)
        # Add 0075-N-K-S-pos0075 next:
        self.output_buffer.append(str(pos0075) + 'NKS 0075' + comment2)
        return True

    def double_justification(self, wedge_positions):
        """double_justification:

        Double justification: the caster sets 0005+0075 and puts the line
        to the galley, then sets 0075 and pump resumes.
        Function adds a 0075-b, then 0005-a combination to buffer.
        Supports both normal (0075, 0005, 0005+0075)
        and alternate (NK, NJ, NKJ) justification modes.
        Adds an "S" signal also - to help delivering the suitable force
        to the 0005 and 0075 levers (some machines have a problem with that).
        """
        (pos0075, pos0005) = wedge_positions
        # Inform the user about the wedge positions
        comment1 = ' // Line to the galley, setting 0005 to ' + str(pos0005)
        comment2 = ' // Setting 0075 to ' + str(pos0075) + ', pump on...'
        # Add 0005-N-J-S-pos0005 first:
        self.output_buffer.append(str(pos0005) + 'NKJS 0005 0075' + comment1)
        # Add 0075-N-K-S-pos0075 next:
        self.output_buffer.append(str(pos0075) + 'NKS 0075' + comment2)
        return True

# Functions needed elsewhere


def calculate_wedges(difference, set_width, brit_pica=False):
    """calculate_wedges:

    Calculates and returns wedge positions for character.
    Uses pre-calculated unit width difference between row's unit width
    and character's width (with optional corrections).
    """
    # Delta is in units of a given set
    # First, we must know whether pica = .1667" or .166" and correct the width
    # if needed.
    if brit_pica:
        coefficient = 1
    else:
        coefficient = 0.1660 / 0.1667
    # Calculate the inch width of delta
    # 1 pica = 18 units 12 set = 0.1667 (old British pica) or 0.1660 (Am. pica)
    # unit_width = 12 * pica / (set width * 18)
    steps = difference * set_width * coefficient * 2000 / 1296
    # Adjust the wedges
    # You do it in respect to the neutral position i.e. 3/8:
    # 3 steps of 0075 and 8 steps of 0005 wedge.
    # You can get from 1 to 15 steps of each wedge.
    # Example: 16 steps of 0005 = 1 step of 0075 and 1 step of 0005
    # 3 / 8 = 1 * 15 + 8 = 53 "raw" steps of 0005 wedge
    pos_0075 = 0
    steps += 53
    # Add safeguards against wrong wedge positions
    # Minimum wedge positions (0075/0005) are 1/1, maximum 15/15
    # This is equivalent to 1*15+1=16 steps (min) and 15*15+15=240 steps (max)
    # Upper limit:
    steps = min(steps, 240)
    # Lower limit:
    steps = max(16, steps)
    # We're in these constraints now - but there is one more constraint:
    # matrix size = .2x.2" (small composition)
    # Opening the mould more than that will lead to lead splashes between mats
    # (this is not a risk with low spaces, as the upper mould blade is closed)
    while steps > 15:
        steps -= 15
        pos_0075 += 1
    # Round the remainder down
    pos_0005 = int(steps)
    # We now can return the wedge positions
    return (pos_0075, pos_0005)


def parse_combination(combination):
    """Simple function that gets the row and column from combination string."""
    combination = str(combination).upper()
    rows = []
    # Look for column numbers from earliest to latest
    column_numbers = ['NI', 'NL'] + list('ABCDEFGHIJKLMNO')
    for num in column_numbers:
        if num in combination:
            column = num
            break
    else:
        # No signal for column means we go all the way to "O" pin
        column = 'O'
    # Now look for a row number
    # We can't look for them in ascending order though
    for num in range(16, 0, -1):
        if str(num) in combination:
            combination = combination.replace(str(num), '')
            rows.append(num)
    # Get the minimum number
    print(rows)
    try:
        row = min(rows)
    except ValueError:
        # This happens if no rows found - default to 15
        row = 15
    return {'column': column, 'row': row}
