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
            self.alignment = self.choose_alignment()
            # Select the composition mode
            self.compose = self.manual_compose
        else:
            # Align to the left
            self.alignment = align_left

    def choose_alignment(self):
        """Lets the user choose the text alignment in line or column."""
        options = {'L': align_left,
                   'C': align_center,
                   'R': align_right,
                   'B': align_both}
        message = ('Alignment? [L]eft, [C]enter, [R]ight, [B]oth: ')
        return ui.simple_menu(message, options)

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

    def get_space_codes(self, space_symbol, unit_width):
        """Gets coordinates for the space closest to the desired unit width"""
        # Space style: " " for low space and "_" for fixed space
        available_spaces = [sp for sp in self.diecase_layout if
                            sp[0] == space_symbol]
        # Check if space has specified unit value
        for space in available_spaces:
            if space[4] is None:
                # Get it from the wedge unit arrangement
                space_row = space[3]
                # We have to use unit-shift to get to 16th row anyway...
                if space_row == 16:
                    space_row = 15
                space[4] = self.unit_arrangement[space_row - 1]
        # Search for a best match, starting with some arbitrary difference
        differences = {}
        for space in available_spaces:
            difference = unit_width - space[-1]
            differences[tuple(space)] = difference
        for space in differences:
            # Found an exact match
            if differences[space] == 0:
                code = str(space[2]) + str(space[3])
                wedge_positions = (None, None)
                return (code, wedge_positions)
        # Fell off the end of the loop with no match

    def parse_and_compose(self, input_text):
        """Parses a text and generates a sequence of (character, style) pairs
        that can be translated into matrix coordinates.
        """
        # Start with setting the main style chosen during setup
        self.current_style = self.main_style
        # Work contains pages
        work = []
        # Page contains lines (with justification mode)
        page = []
        # Line contains text chunks (with style)
        line = []
        # The smallest chunk of text
        text_chunk = []

        # Define some parsing functions
        def set_roman():
            """Sets roman for the following text."""
            line.append((text_chunk, self.current_style))
            self.current_style = 'roman'

        def set_bold():
            """Sets bold for the following text."""
            line.append((text_chunk, self.current_style))
            self.current_style = 'bold'

        def set_italic():
            """Sets italic for the following text."""
            line.append((text_chunk, self.current_style))
            self.current_style = 'italic'

        def set_smallcaps():
            """Sets small caps for the following text."""
            line.append((text_chunk, self.current_style))
            self.current_style = 'smallcaps'

        def set_subscript():
            """Sets subscript for the following text."""
            line.append((text_chunk, self.current_style))
            self.current_style = 'subscript'

        def set_superscript():
            """Sets superscript for the following text."""
            line.append((text_chunk, self.current_style))
            self.current_style = 'superscript'

        def align_left():
            """Aligns the previous chunk to the left and ends the line."""
            char_units = self.get_unit_width(text_chunk)
            space_count = len([n for n in text_chunk if n == ' '])
            page.append(line)

        def align_right():
            """Aligns the previous chunk to the right and ends the line."""
            char_units = self.get_unit_width(text_chunk)
            space_count = len([n for n in text_chunk if n == ' '])
            page.append(line)

        def align_center():
            """Aligns the previous chunk to the center and ends the line."""
            char_units = self.get_unit_width(text_chunk)
            space_count = len([n for n in text_chunk if n == ' '])
            page.append(line)

        def align_both():
            """Aligns the previous chunk to both edges and ends the line."""
            char_units = self.get_unit_width(text_chunk)
            space_count = len([n for n in text_chunk if n == ' '])
            page.append(line)

        def page_break():
            """Ends a previous page, starts a new one."""
            work.append(page)

        # Commands for activating these functions
        commands = {'^00': 'set_roman',
                    '^01': 'set_bold',
                    '^02': 'set_italic',
                    '^03': 'set_smallcaps',
                    '^04': 'set_subscript',
                    '^05': 'set_superscript',
                    '^CR': 'align_left',
                    '^CL': 'align_right',
                    '^CC': 'align_center',
                    '^CF': 'align_both',
                    '^PG': 'page_break'}
        # Iterate over the input text
        for index, character in enumerate(input_text):
            try:
                triple = input_text[index:index+2]
            except IndexError:
                triple = None
            try:
                double = input_text[index:index+1]
            except IndexError:
                double = None
            # Now we have a char + two next, char + next, char
            # Try to use a command
            try:
                commands[triple]()
                # Command succeeded, skip the loop
                continue
            except KeyError:
                # Command failed
                pass
            # Search for ligatures
            if (self.ligatures == 3 and
                    triple in (matrix[0] for matrix in self.diecase_layout
                               if self.current_style in matrix[1])):
                text_chunk.append(triple)
            elif (self.ligatures >= 2 and
                  double in (matrix[0] for matrix in self.diecase_layout
                             if self.current_style in matrix[1])):
                text_chunk.append(double)
        work = []
        text_generator = ((char, style)
                          for page in work
                          for line in page
                          for (text_chunk, style) in line
                          for char in text_chunk)
        return text_generator

    def manual_compose(self, text):
        """manual_compose:

        Reads text fragments from input, then composes them, and justifies to a
        specified line length. Adds codes to the buffer.
        Text fragments is a list of tuples: ((text1, style1), ...)
        """
        # Enter the space settings
        (var_style, var_min_units, fixed_style, fixed_units,
         nb_sp_style, nb_sp_units) = self.space_settings()
        # Get the Monotype signals for the spaces
        fix_space_code = self.get_space_codes(fixed_style, fixed_units)
        nb_space_code = self.get_space_codes(nb_sp_style, nb_sp_units)
        # Choose if you want to use ligatures
        prompt = 'Ligatures: [1] - off, [2] characters, [3] characters? '
        options = {'1': False, '2': 2, '3': 3}
        self.ligatures = ui.simple_menu(prompt, options)
        # Inintialize with no chars and spaces count at 0
        text_generator = self.parse_and_compose(text)

    def auto_compose(self, text):
        """Composes text automatically, deciding when to end the lines."""
        text_generator = self.parse_and_compose(text)

    def get_unit_width(self, row):
        """Gets a unit width of a character"""
        unit_width = (self.unit_arrangement[row-1])
        return unit_width

    def translate_text(self, composed_text):
        """Translates a composed text to Monotype codes"""

    def translate_character(self, char, style):
        """translate_character:

        Gets character's coordinates in the diecase, determines and applies
        unit width correction (with unit shift or single justification).
        Returns coordinates (as a string) and unit width of a character.
        """
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

    def space_settings(self):
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
        # Variable space (justified) - minimum units
        variable_space = ui.simple_menu(var_prompt, {'L': ' ', 'H': '_'})
        min_units = ui.enter_data_spec_type_or_blank(
            var_units_prompt, int) or 4
        # Fixed space (allows line-breaking)
        fixed_space = ui.simple_menu(fixed_prompt, {'L': ' ', 'H': '_'})
        fixed_units = ui.enter_data_spec_type_or_blank(
            fix_units_prompt, int) or 9
        # Non-breaking space
        nb_space = ui.simple_menu(nbsp_prompt, {'L': ' ', 'H': '_'})
        nb_units = ui.enter_data_spec_type_or_blank(
            nbsp_units_prompt, int) or 9
        # Return decision
        return (variable_space, min_units,
                fixed_space, fixed_units,
                nb_space, nb_units)


# Functions

def single_justification(wedge_positions, buffer):
    """single_justification:

    Single justification: the caster sets 0005, then 0075 + pump resumes.
    Function adds a 0075-b, then 0005-a combination to buffer.
    Supports both normal (0075, 0005, 0005+0075) and alternate (NK, NJ, NKJ)
    justification modes.
    """
    (pos0075, pos0005) = wedge_positions
    # Add 0075-N-K-pos0075 first:
    buffer.append(str(pos0075) + 'NK 0075')
    # Add 0005-N-J-pos0005 next:
    buffer.append(str(pos0005) + 'NJ 0005')
    return True


def double_justification(wedge_positions, buffer):
    """double_justification:

    Double justification: the caster sets 0005+0075 and puts the line
    to the galley, then sets 0075 and pump resumes.
    Function adds a 0075-b, then 0005-a combination to buffer.
    Supports both normal (0075, 0005, 0005+0075)
    and alternate (NK, NJ, NKJ) justification modes.
    """
    (pos0075, pos0005) = wedge_positions
    # Add 0075-N-K-pos0075 first:
    buffer.append(str(pos0075) + 'NK 0075')
    # Add 0005-N-J-pos0005 next:
    buffer.append(str(pos0005) + 'NKJ 0005 0075')
    return True


def align_left(buffer, line_length, characters_unit_length):
    """Aligns the text to the left."""
    pass


def align_center(text, line_length):
    """Centers the text."""
    pass


def align_right(text, line_length):
    """Aligns the text to the right."""
    pass


def align_both(text, line_length):
    """Aligns the text to both margins."""
    pass
