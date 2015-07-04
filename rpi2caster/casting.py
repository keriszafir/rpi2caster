"""
casting:

A module for everything related to working on a Monotype composition caster:
-casting composed type,
-punching paper tape (ribbon) for casters without interfaces,
-casting l lines of m sorts from matrix with x, y coordinates,
-testing all valves, lines and pinblock,
-calibrating the space transfer wedge,
-heating the mould up,
-sending any codes/combinations to the caster.
"""

# IMPORTS:
# Built-in time library
import time
# Signals parsing methods for rpi2caster
from rpi2caster import parsing
# User interfaces module for rpi2caster:
from rpi2caster.global_settings import USER_INTERFACE as ui
# Custom exceptions
from rpi2caster import exceptions
# Typesetting functions module
from rpi2caster import typesetting_functions
# Diecase manipulation functions
from rpi2caster import matrix_data
# Wedge manipulation functions
from rpi2caster import wedge_data


def use_caster(func):
    """Method decorator for requiring the caster context"""
    def func_wrapper(self, *args, **kwargs):
        """Wrapper function"""
        with self.caster:
            return func(self, *args, **kwargs)
    return func_wrapper


class Casting(object):
    """Casting:

    Methods related to operating the composition caster.
    Requires configured:
    -caster
    -database
    -UI.

    These attributes need to be set up before casting anything.
    Normally, you instantiate the Session class and it takes care of all
    setup work.

    Ribbon filename is also an object's attribute, but it's usually
    set up via user interaction. You can also feed the filename
    to class on init.

    All methods related to operating a composition caster are here:
    -casting composition and sorts,
    -calibrating the caster,
    -testing the interface,
    -sending an arbitrary combination of signals,
    -casting spaces to heat up the mould."""

    def __init__(self, ribbon_file=''):
        # Caster - this will be set up later
        self.caster = None
        # You can initialize the casting job with a ribbon
        self.ribbon_file = ribbon_file
        # Ribbon contenrs
        self.ribbon = []
        # Indicates which line the last casting was aborted on
        self.line_aborted = None
        # Metadata read from file
        self.metadata = {}
        # Diecase parameters
        self.diecase_id = None
        self.diecase = None
        self.diecase_layout = None
        # Fount data
        self.type_series = None
        self.type_size = None
        self.set_width = None

    def __enter__(self):
        ui.debug_info('Entering casting job context...')
        main_menu()

    @use_caster
    def cast_composition(self):
        """cast_composition()

        Composition casting routine. The input file is read backwards -
        last characters are cast first, after setting the justification.
        """
        # Count all characters and lines in the ribbon
        [all_lines, all_chars] = parsing.count_lines_and_chars(self.ribbon)
        # Characters already cast - start with zero
        current_char = 0
        chars_left = all_chars
        # Line currently cast: since the caster casts backwards
        # (from the last to the first line), this will decrease.
        current_line = all_lines
        # The program counts galley trip sequences and determines line count.
        # The first code to send to machine is galley trip (which also sets the
        # justification wedges and turns the pump on). So, subtract this one
        # to have the correct number of lines.
        all_lines -= 1
        # Show the numbers to the operator
        ui.display('Lines found in ribbon: %i' % all_lines)
        ui.display('Characters: %i' % all_chars)
        # For casting, we need to read the contents in reversed order
        content = reversed(self.ribbon)
        # Display a little explanation
        intro = ('\nThe combinations of Monotype signals will be displayed '
                 'on screen while the machine casts the type.\n'
                 'Turn on the machine and the program will start.\n')
        ui.display(intro)
        # Start only after the machine is running
        self.caster.detect_rotation()
        # Read the reversed file contents, line by line, then parse
        # the lines, display comments & code combinations, and feed the
        # combinations to the caster
        for line in content:
            # Parse the row, return a list of signals and a comment.
            # Both can have zero or positive length.
            [raw_signals, comment] = parsing.comments_parser(line)
        # Parse the signals
            signals = parsing.signals_parser(raw_signals)
            # A list with information for user: signals, comments, etc.
            info_for_user = []
            if parsing.check_newline(signals):
                # Decrease the counter for each started new line
                current_line -= 1
                # Percent of all lines done:
                line_percent_done = (100 * (all_lines - current_line) /
                                     all_lines)
                # Display number of the working line,
                # number of all remaining lines, percent done
                info_for_user.append('Starting line: %i of %i, %i%% done...\n'
                                     % (current_line, all_lines,
                                        line_percent_done))
            elif parsing.check_character(signals):
                # Increase the current character and decrease characters left,
                # then do some calculations
                current_char += 1
                chars_left -= 1
                # % of chars to cast in the line
                char_percent_done = 100 * current_char / all_chars
                # Display number of chars done,
                # number of all and remaining chars, % done
                info_for_user.append('Casting character: %i / %i, '
                                     '%i remaining, %i%% done...\n'
                                     % (current_char, all_chars,
                                        chars_left, char_percent_done))
            # Append signals to be cast
            info_for_user.append(' '.join(signals).ljust(15))
        # Add comment
            info_for_user.append(comment)
            # Display the info
            ui.display(''.join(info_for_user))
        # Proceed with casting only if code is explicitly stated
        # (i.e. O15 = cast, empty list = don't cast)
            if signals:
                signals = parsing.strip_o_and_15(signals)
                # Cast the sequence
                try:
                    self.caster.process_signals(signals)
                except exceptions.CastingAborted:
                    # On failure - abort the whole job.
                    # Check the aborted line so we can get back to it.
                    self.line_aborted = current_line
                    ui.display('\nCasting aborted on line %i.'
                               % self.line_aborted)
                    ui.hold_on_exit()
                    return False
        # After casting is finished, notify the user
        ui.display('\nCasting finished successfully!')
        ui.hold_on_exit()
        return True

    @use_caster
    def punch_composition(self):
        """punch_composition():

        When punching, the input file is read forwards. An additional line
        (O+15) is switched on for operating the paper tower, if less than
        two signals are found in a sequence.

        We can't use automatic machine cycle detection like we do in
        cast_composition, because keyboard's paper tower doesn't run
        by itself - it must get air into tubes to operate, punches
        the perforations, and doesn't give any feedback.

        For punching, O+15 are needed if <2 lines are active.
        That's because of how the keyboard's paper tower is built -
        it has a balance mechanism that advances paper tape only if two
        signals can outweigh constant air pressure on the other side.
        Basically: less than two signals - no ribbon advance...
        """
        # Count a number of combinations punched in ribbon
        all_combinations = parsing.count_combinations(self.ribbon)
        ui.display('Combinations in ribbon: %i', all_combinations)
        # Wait until the operator confirms.
        intro = ('\nThe combinations of Monotype signals will be displayed '
                 'on screen while the paper tower punches the ribbon.\n')
        ui.display(intro)
        prompt = ('\nInput file found. Turn on the air, fit the tape '
                  'on your paper tower and press return to start punching.')
        ui.confirm(prompt)
        for line in self.ribbon:
            # Parse the row, return a list of signals and a comment.
            # Both can have zero or positive length.
            [raw_signals, comment] = parsing.comments_parser(line)
            # Parse the signals
            signals = parsing.signals_parser(raw_signals)
            # A string with information for user: signals, comments, etc.
            info_for_user = ''
            # Add signals to be cast
            if signals:
                info_for_user += ' '.join(signals).ljust(20)
            # Add comment
            if comment:
                info_for_user += comment
            # Display the info
            ui.display(info_for_user)
            # Send the signals, adding O+15 whenever needed
            if signals:
                # Convert O or 15 to a combined O+15 signal:"""
                signals = parsing.convert_o15(signals)
                if len(signals) < 2:
                    signals.append('O15')
                # Punch it!"""
                self.caster.activate_valves(signals)
                # The pace is arbitrary, let's set it to 200ms/200ms
                time.sleep(0.2)
                self.caster.deactivate_valves()
                time.sleep(0.2)
        # After punching is finished, notify the user:"""
        ui.display('\nPunching finished!')
        ui.hold_on_exit()
        return True

    @use_caster
    def line_test(self):
        """line_test():

        Tests all valves and composition caster's inputs to check
        if everything works and is properly connected. Signals will be tested
        in order: 0075 - S - 0005, 1 towards 14, A towards N, O+15.
        """
        intro = ('This will check if the valves, pin blocks and 0075, S, '
                 '0005 mechanisms are working. Press return to continue... ')
        ui.confirm(intro)
        combinations = (['0075', 'S', '0005'] +
                        [str(n) for n in range(1, 15)] +
                        [s for s in 'ABCDEFGHIJKLMNO'])
        # Send all the combinations to the caster, one by one.
        # Set _machine_stopped timeout at 120s.
        try:
            for code in combinations:
                ui.display(code)
                code = parsing.signals_parser(code)
                code = parsing.convert_o15(code)
                self.caster.process_signals(code, 120)
        except exceptions.CastingAborted:
            return False
        else:
            ui.display('\nTesting finished!')
            ui.hold_on_exit()
            return True

    def cast_sorts(self):
        """cast_sorts():

        Sorts casting routine, based on the position in diecase.
        Ask user about the diecase row & column, as well as number of sorts.
        """
        while True:
            # Outer loop
            ui.clear()
            ui.display('Calibration and Sort Casting:\n\n')
            prompt = 'Enter column and row symbols (default: G 5): '
            # Got no signals? Use G5.
            signals = ui.enter_data(prompt) or 'G 5'
            # Ask for number of sorts and lines
            try:
                prompt = '\nHow many sorts? (default: 10): '
                sorts = ui.enter_data(prompt)
                sorts = abs(int(sorts))
            except ValueError:
                sorts = 10
            try:
                prompt = '\nHow many lines? (default: 1): '
                lines = ui.enter_data(prompt)
                lines = abs(int(lines))
            except ValueError:
                lines = 1
            # Warn if we want to cast too many sorts from a single matrix
            warning = ('Warning: you want to cast a single character more than'
                       ' 10 times. This may lead to matrix overheating!\n')
            if sorts > 10:
                ui.display(warning)
            # After entering parameters, ask the operator if they're OK
            try:
                while True:
                    # Inner loop
                    # Menu subroutines
                    def cast_it():
                        """Cast the combination or go back to menu"""
                        if self.cast_from_matrix(signals, sorts, lines):
                            ui.display('Casting finished successfully.')
                        else:
                            raise exceptions.ReturnToMenu
                    # End of menu subroutines.
                    options = {'C': cast_it,
                               'D': exceptions.change_parameters,
                               'M': exceptions.return_to_menu,
                               'E': exceptions.exit_program}
                    message = ('Casting %s, %i lines of %i sorts.\n'
                               '[C]ast it, [D]ifferent code/quantity, '
                               '[M]enu or [E]xit? '
                               % (signals, lines, sorts))
                    choice = ui.simple_menu(message, options).upper()
                    # Execute choice
                    options[choice]()
            except exceptions.ChangeParameters:
                # Skip the menu and casting altogether, repeat the outer loop
                pass

    @use_caster
    def cast_from_matrix(self, signals, num=5, lines=1,
                         wedge_positions=(3, 8)):
        """cast_from_matrix(combination, n, lines, (pos0075, pos0005)):

        Casts n sorts from combination of signals (list),
        with correction wedges if S needle is in action.

        By default, it sets 0075 wedge to 3 and 0005 wedge to 8 (neutral).
        Determines if single justification (0075 only) or double
        justification (0005 + 0075) is used.

        N, K and J signals are for alternate justification scheme,
        used with unit-adding attachment and turned on/off with a large
        IN/OUT valve at the backside of the caster:
        NJ = 0005
        NK = 0075
        NKJ = 0005 + 0075
        """
        # Reset the aborted line counter
        self.line_aborted = None
        (pos_0075, pos_0005) = (str(x) for x in wedge_positions)
        # Signals for setting 0005 and 0075 justification wedges
        set_0005 = ('N', 'J', '0005', pos_0005)
        set_0075 = ('N', 'K', '0075', pos_0075)
        # Galley trip signal
        galley_trip = ('N', 'K', 'J', '0005', '0075')
        # Parse the combination
        combination = parsing.signals_parser(signals)
        combination = parsing.strip_o_and_15(combination)
        # Check if the machine is running first, end here if not
        ui.display('Start the machine...')
        self.caster.detect_rotation()
        # We're here because the machine is rotating. Start casting the job...
        for current_line in range(1, lines + 1):
            # Cast each line and if the CastingAborted exception is caught,
            # remember the last line and stop casting.
            try:
                # Cast the sorts: set wedges, turn pump on, cast, line out
                # Set up the justification, turn the pump on
                ui.display('Casting line %i of %i' % (current_line, lines))
                ui.display('0005 wedge at ' + pos_0005)
                self.caster.process_signals(set_0005)
                ui.display('0075 wedge at ' + pos_0075)
                ui.display('Starting the pump...')
                self.caster.process_signals(set_0075)
                # Start casting characters
                ui.display('Casting characters...')
                # Cast n combinations of row & column, one by one
                for i in range(1, num + 1):
                    info = ('%s - casting character %i of %i, %i%% done.'
                            % (' '.join(combination).ljust(20),
                               i, num, 100 * i / num))
                    ui.display(info)
                    parsing.strip_o_and_15(combination)
                    self.caster.process_signals(combination)
                    # If everything went normally, put the line to the galley
                ui.display('Putting line to the galley...')
                self.caster.process_signals(galley_trip)
                # After casting sorts we need to stop the pump
                ui.display('Stopping the pump...')
                self.caster.process_signals(set_0005)
            except exceptions.CastingAborted:
                self.line_aborted = current_line
                ui.display('Casting aborted on line %i' % self.line_aborted)
                return False
        # We'll be here if casting ends successfully
        return True

    @use_caster
    def send_combination(self):
        """send_combination():

        This function allows us to give the program a specific combination
        of Monotype codes, and will keep the valves on until we press return
        (useful for calibration). It also checks the signals' validity.
        """
        while True:
            # You can enter new signals or exit
            prompt = ('Enter the signals to send to the caster, '
                      'or leave empty to return to menu: ')
            signals = ui.enter_data(prompt)
            # Turn off any valves that were on (from previous combination)
            self.caster.deactivate_valves()
            if not signals:
                # Escape the infinite loop here
                raise exceptions.ReturnToMenu
            # Parse the combination, get the signals (first item returned
            # by the parsing function)
            signals = parsing.signals_parser(signals)
            # Add O+15 signal if it was desired
            signals = parsing.convert_o15(signals)
            # Turn the valves on
            ui.display(' '.join(signals))
            self.caster.activate_valves(signals)
            # Start over.

    def align_wedges(self, space_position='G5'):
        """align_wedges(space_position='G5'):

        Allows to align the justification wedges so that when you're
        casting a 9-unit character with the S-needle at 0075:3 and 0005:8
        (neutral position), the    width is the same.

        It works like this:
        1. 0075 - turn the pump on,
        2. cast 10 spaces from the specified matrix (default: G9),
        3. put the line to the galley & set 0005 to 8, 0075 to 3, pump on,
        4. cast 10 spaces with the S-needle from the same matrix,
        5. put the line to the galley, then 0005 to turn the pump off.
        """
        intro = ('Transfer wedge calibration:\n\n'
                 'This function will cast 10 spaces, then set the correction '
                 'wedges to 0075:3 and 0005:8, \nand cast 10 spaces with the '
                 'S-needle. You then have to compare the length of these two '
                 'sets. \nIf they are identical, all is OK. '
                 'If not, you have to adjust the 52D space transfer wedge.')
        ui.display(intro)
        while True:
            # Subroutines for menu options
            def continue_aligning():
                """Cast spaces with and without S-needle"""
                pass
            # Finished. Return to menu.
            options = {'C': continue_aligning,
                       'M': exceptions.return_to_menu,
                       'E': exceptions.exit_program}
            message = '\n[C]ontinue, [M]enu or [E]xit? '
            choice = ui.simple_menu(message, options).upper()
            # Execute choice
            options[choice]()
            # Cast 10 spaces without correction.
            # End here if casting unsuccessful.
            ui.display('Now casting with a normal wedge only.')
            if not self.cast_from_matrix(space_position, 5):
                continue
            # Cast 10 spaces with the S-needle.
            # End here if casting unsuccessful.
            ui.display('Now casting with justification wedges...')
            if not self.cast_from_matrix(space_position + 'S', 5):
                continue
            # At the end of successful sequence, some info for the user:
            ui.display('Done. Compare the lengths and adjust if needed.')

    def linotype_mode(self):
        """linotype_mode:

        Allows us to use caster in a "linotype mode".
        This means that the user enters a text to be cast,
        gives the line length, chooses alignment and diecase.
        Then, the program composes the line, justifies it, translates it
        to Monotype code combinations, and starts casting.

        This is a transitional function to be used before the real
        typesetting program is ready.

        It can be used for casting one-liners, names etc.
        """
        # Enter text
        text = ui.enter_data("Enter text to compose: ")
        # Enter line length
        line_length = ui.enter_data_spec_type('Line length? : ', int)
        # Choose alignment mode
        options = {'L': typesetting_functions.align_left,
                   'C': typesetting_functions.align_center,
                   'R': typesetting_functions.align_right,
                   'B': typesetting_functions.align_both}
        message = ('Alignment: [L]eft, [C]enter, [R]ight, [B]oth? ')
        alignment = ui.simple_menu(message, options)
        # Choose unit shift: yes or no?
        options = {'Y': True, 'N': False}
        message = ('Do you use unit-shift: [Y]es, [N]o? ')
        unit_shift = ui.simple_menu(message, options)
        # Choose type series
        type_series = ui.enter_data('Typeface series? : ')
        # Choose type size
        type_size = ui.enter_data_spec_type('Type size? : ', int)
        # Find the diecase
        self.diecase = matrix_data.lookup_diecase(type_series, type_size)
        # Read the parameters
        self.diecase_id = self.diecase[0]
        self.type_series = self.diecase[1]
        type_size = self.diecase[2]
        self.set_width = self.diecase[3]
        # European Didot diecase or not? Type size has the answer
        didot = type_size.endswith('D')
        self.type_size = int(type_size.strip('D'))
        #  Typeface name - optional
        if isinstance(self.diecase[4], str):
            typeface_name = self.diecase[4]
            ui.display('Using typeface: %s' % typeface_name)
        # Determine the layout
        self.diecase_layout = self.diecase[-1]
        # Determine the wedge unit arrangement
        wedge_name = self.diecase[-2]
        wedge = wedge_data.wedge_by_name_and_width(wedge_name, self.set_width)
        wedge_unit_arrangement = wedge[4]
        wedge_brit_pica = wedge[3]
        if didot == wedge_brit_pica:
            ui.display('The wedge and diecase use British pica')
        # Translate the text to Monotype signals
        self.ribbon = typesetting_functions.translate(text, line_length,
                                                      self.diecase_layout,
                                                      alignment,
                                                      wedge_unit_arrangement,
                                                      unit_shift)
        # Ask whether to display buffer contents
        options = {'Y': True, 'N': False}
        message = ('Display the codes? [Y]es, [N]o ')
        if ui.simple_menu(message, options):
            self.preview_ribbon()

    def preview_ribbon(self):
        """preview_ribbon:

        Determines if we have a ribbon file that can be previewed,
        and displays its contents line by line, or displays
        an error message.
        """
        ui.clear()
        ui.display('Ribbon preview:\n')
        ui.display('\n'.join([line for line in self.ribbon]))
        ui.hold_on_exit()

    def __exit__(self, *args):
        ui.debug_info('Exiting casting job context.')


def main_menu(work=Casting()):
    """main_menu:

    Calls ui.menu() with options, a header and a footer.
    Options: {option_name : description}
    Header: string displayed over menu
    Footer: string displayed under menu (all info will be added here).
    """
    # Declare subroutines for menu options
    def choose_ribbon_filename():
        """choose_ribbon_filename

        Asks the user for the ribbon filename.
        Checks if the file is readable, and pre-processes it.
        """
        work.ribbon_file = ui.enter_input_filename()
        work.ribbon = parsing.read_file(work.ribbon_file)
        # If file read failed, end here
        if not work.ribbon:
            ui.display('Error reading file!')
            time.sleep(1)
            return False
        # Read the metadata at the beginning of the ribbon file
        work.metadata = parsing.get_metadata(work.ribbon)
        try:
            work.diecase = work.metadata['diecase']
        except KeyError:
            pass
        # Reset the "line aborted" on a new casting job
        work.line_aborted = None
        return True

    def debug_notice():
        """debug_notice

        Prints a notice if the program is in debug mode.
        """
        if ui.DEBUG_MODE:
            return '\n\nThe program is now in debugging mode!'
        else:
            return ''

    def additional_info():
        """additional_info:

        Displays additional info as a menu footer.
        Starts with an empty list, and checks whether the casting job
        objects has attributes that are parameters to be displayed.
        """
        info = []
        # Add ribbon filename, if any
        if work.ribbon_file:
            info.append('Input file name: ' + work.ribbon_file)
        # Add a caster name
        info.append('Using caster: ' + work.caster.name)
        # Add metadata for ribbon
        for parameter in work.metadata:
            value = str(work.metadata[parameter])
            info.append(str(parameter).capitalize() + ': ' + value)
        # Display the line last casting was aborted on, if applicable:
        if work.line_aborted:
            info.append('Last casting was aborted on line ' +
                        str(work.line_aborted))
        # Convert it all to a multiline string
        return '\n'.join(info)

    def heatup():
        """heatup

        Allows to heat up the mould before casting, in order to
        stabilize the mould temperature (affects the type quality).
        Casts two lines of em-quads, which can be thrown back to the pot.
        """
        ui.clear()
        work.cast_from_matrix('O15', num=20, lines=2)

    def cast_or_punch():
        """cast_or_punch:

        Determines if the caster specified for the job is actually
        a perforator - if so, a "punch ribbon" feature will be
        available instead of "cast composition".
        """
        if work.caster.is_perforator:
            return ('Punch composition', work.punch_composition)
        else:
            return ('Cast composition', work.cast_composition)

    # End of menu subroutines
    # Now construct the menu, starting with available options
    options = [('Exit program', exceptions.exit_program),
               ('Load a ribbon file', choose_ribbon_filename),
               ('Preview ribbon', work.preview_ribbon),
               cast_or_punch(),
               ('Linotype mode', work.linotype_mode),
               ('Cast sorts', work.cast_sorts),
               ('Test the valves and pinblocks', work.line_test),
               ('Send specified signals to caster', work.send_combination),
               ('Calibrate the space transfer wedge', work.align_wedges),
               ('Cast some quads to heat up the mould', heatup)]

    header = ('rpi2caster - CAT (Computer-Aided Typecasting) '
              'for Monotype Composition or Type and Rule casters.'
              '\n\n'
              'This program reads a ribbon (input file) '
              'and casts the type on a composition caster.' +
              debug_notice() + '\n\nMain Menu:')
    # Keep displaying the menu and go back here after any method ends
    while True:
        try:
            # Catch "return to menu" and "exit program" exceptions here
            ui.menu(options, header=header, footer=additional_info())()
        except exceptions.ReturnToMenu:
            # Will skip to the end of the loop, and start all over
            pass
        except (KeyboardInterrupt, exceptions.ExitProgram):
            # Will exit program
            ui.exit_program()
