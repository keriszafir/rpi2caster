"""
casting:

A module for everything related to working on a Monotype composition caster:
-casting composed type,
-punching paper tape (ribbon) for casters without interfaces,
-casting l lines of m sorts from matrix with x, y coordinates,
-composing and casting a line of text
-testing all valves, lines and pinblock,
-calibrating the space transfer wedge,
-heating the mould up,
-sending any codes/combinations to the caster and keeping them on.
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
from rpi2caster import typesetting
# Diecase manipulation functions
from rpi2caster import matrix_data
# Wedge manipulation functions
from rpi2caster import wedge_data
# Read ribbon files
from rpi2caster import typesetting_data


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
        # Filename will be displayed
        self.ribbon_file = ribbon_file
        # Ribbon contents and metadata
        self.ribbon_contents = None
        self.ribbon_metadata = None
        # Indicates which line the last casting was aborted on
        self.line_aborted = 0
        # Diecase parameters
        self.diecase = None
        self.diecase_id = None
        self.diecase_layout = None
        # Unit arrangement: default is the S5 wedge
        self.wedge = None
        self.unit_arrangement = wedge_data.WEDGES['5']

    def __enter__(self):
        ui.debug_info('Entering casting job context...')
        main_menu()

    @use_caster
    def cast_composition(self):
        """cast_composition()

        Composition casting routine. The input file is read backwards -
        last characters are cast first, after setting the justification.
        """
        if not self.ribbon_contents:
            ui.confirm('You must select a ribbon! [Enter] to continue...')
            return False
        # Count all characters and lines in the ribbon
        (all_lines, all_chars) = parsing.count_lines_and_chars(
            self.ribbon_contents)
        # Show the numbers to the operator
        ui.display('Lines found in ribbon: %i' % all_lines)
        ui.display('Characters: %i' % all_chars)
        # Check the line previous job has been aborted on
        # Ask how many lines to skip; add two previous lines if possible
        # so that the mould temperature has a chance to stabilize
        lines_skipped = self.line_aborted - 2
        # This must be non-negative
        if lines_skipped < 0:
            lines_skipped = 0
        ui.display('You can skip a number of lines so that you can e.g. start '
                   'a casting job aborted earlier.')
        prompt = 'How many lines to skip? (default: %s) : ' % lines_skipped
        lines_skipped = (ui.enter_data_spec_type_or_blank(prompt, int) or
                         lines_skipped)
        prompt = 'How many times do you want to cast this? (default: 1) : '
        repetitions = ui.enter_data_spec_type_or_blank(prompt, int) or 1
        # For casting, we need to check if the ribbon has to be read
        # forwards or backwards
        if parsing.rewind_ribbon(self.ribbon_contents):
            ui.display('Ribbon starts with pump stop sequence - rewinding...')
            queue = [line for line in reversed(self.ribbon_contents)]
        else:
            ui.display('Ribbon starts with galley trip - not rewinding...')
            queue = [line for line in self.ribbon_contents]
        # Display a little explanation
        intro = ('\nThe combinations of Monotype signals will be displayed '
                 'on screen while the machine casts the type.\n'
                 'Turn on the machine and the program will start.\n')
        ui.display(intro)
        # Start only after the machine is running
        self.caster.detect_rotation()
        # Dict for telling the user whether sth is on or off
        status = {True: 'ON', False: 'OFF'}
        # Initially the pump is not working...
        pump_working = False
        # Current run number
        current_run = 1
        # Repeat casting the whole sequence as many times as we would like
        while current_run <= repetitions:
            ui.display('\n\nCASTING RUN %d / %d (%d left)...\n\n'
                       % (current_run, repetitions, repetitions - current_run))
            current_run += 1
            # Characters already cast - start with zero
            current_char = 0
            chars_left = all_chars
            # Line currently cast: since the caster casts backwards
            # (from the last to the first line), this will decrease.
            current_line = all_lines
            # Lines done: this will increase
            # We start with a galley trip
            lines_done = 0
            # Wedges are initially unset - 15/15
            pos_0075, pos_0005 = '15', '15'
            # Read the reversed file contents, line by line, then parse
            # the lines, display comments & code combinations, and feed the
            # combinations to the caster
            for line in queue:
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
                    line_percent_done = 100 * lines_done / (all_lines - 1)
                    # Up the completed lines counter
                    lines_done += 1
                    # Display number of the working line,
                    # number of all remaining lines, percent done
                    if not current_line:
                        info_for_user.append('All lines successfully cast.\n')
                    else:
                        info_for_user.append('Starting line no. %i (%i of %i),'
                                             ' %i remaining [%i%% done]...\n'
                                             % (current_line, lines_done,
                                                all_lines - 1,
                                                all_lines - lines_done,
                                                line_percent_done))
                    # The pump will be working - set the flag
                    pump_working = True
                elif parsing.check_pump_start(signals):
                    pump_working = True
                elif parsing.check_pump_stop(signals):
                    pump_working = False
                elif parsing.check_character(signals):
                    # Increase the current character and decrease characters
                    # left, then do some calculations
                    current_char += 1
                    chars_left -= 1
                    # % of chars to cast in the line
                    char_percent_done = 100 * (current_char - 1) / all_chars
                    # Display number of chars done,
                    # number of all and remaining chars, % done
                    info = ('Casting line no. %i (%i of %i), character: '
                            '%i of %i, %i remaining [%i%% done]...\n'
                            % (current_line, lines_done, all_lines - 1,
                               current_char, all_chars,
                               chars_left, char_percent_done))
                    info_for_user.append(info)
                    info_for_user.append('Pump is %s\n' % status[pump_working])
                # Skipping the unneeded lines:
                # Just don't cast anything until we get to the correct line
                if lines_done <= lines_skipped:
                    continue
                # Determine if wedge positions change
                (new_0075, new_0005) = parsing.check_wedge_positions(signals)
                pos_0075 = new_0075 or pos_0075
                pos_0005 = new_0005 or pos_0005
                # Display wedge positions and pump status
                pump_info = ('0075 wedge at %s, 0005 wedge at %s\n'
                             % (pos_0075, pos_0005))
                info_for_user.append(pump_info)
                # Append signals to be cast
                info_for_user.append(' '.join(signals).ljust(15))
                # Add comment
                info_for_user.append(comment + '\n')
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
        ui.display('Casting finished successfully!\n')
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
        if not self.ribbon_contents:
            ui.confirm('You must select a ribbon! [Enter] to continue...')
            return False
        # Count a number of combinations punched in ribbon
        all_combinations = parsing.count_combinations(self.ribbon_contents)
        ui.display('Combinations in ribbon: %i', all_combinations)
        # Wait until the operator confirms.
        intro = ('\nThe combinations of Monotype signals will be displayed '
                 'on screen while the paper tower punches the ribbon.\n')
        ui.display(intro)
        prompt = ('\nInput file found. Turn on the air, fit the tape '
                  'on your paper tower and press return to start punching.')
        ui.confirm(prompt)
        for line in self.ribbon_contents:
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
    def test_air(self):
        """test_air():

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
        # We need to choose a wedge unless we did it earlier
        wedge = self.wedge or wedge_data.choose_wedge()
        (_, _, set_width, brit_pica, unit_arrangement) = wedge
        while True:
            # Outer loop
            ui.clear()
            ui.display('Sorts casting by matrix coordinates\n\n')
            prompt = 'Column: NI, NL, A...O? (default: G): '
            # Got no signals? Use G5.
            column = ''
            column_symbols = ['NI', 'NL'] + [ltr for ltr in 'ABCDEFGHIJKLMNO']
            while column not in column_symbols:
                column = ui.enter_data_or_blank(prompt).upper() or 'G'
            prompt = 'Row: 1...16? (default: 5): '
            # Initially set this to zero to enable the while loop
            row = 0
            units = 0
            # Not using unit shift by default
            unit_shift = False
            # Ask for row number
            while row not in range(1, 17):
                try:
                    row = ui.enter_data_spec_type_or_blank(prompt, int) or 5
                    row = abs(row)
                except TypeError:
                    row = 0
            if row == 16:
                question = 'Trying to access 16th row. Use unit shift?'
                unit_shift = ui.yes_or_no(question)
                row = 15
                if not unit_shift:
                    ui.display('Cannot access the 16th row; using 15 instead')
                    ui.yes_or_no('Is it okay?') or exceptions.return_to_menu()
            # Correct the column number if using unit shift
            if unit_shift:
                column = column.replace('D', 'E F')
                column += ' D'
            # Determine the unit width for a row
            try:
                row_units = unit_arrangement[row - 1]
            except (IndexError, KeyError):
                row_units = 5
            prompt = 'Unit width value? (decimal, default: %s) : ' % row_units
            while (units < 2 or units > 25):
                units = (ui.enter_data_spec_type_or_blank(prompt, float) or
                         row_units)
            # Calculate the unit width difference and apply justification
            difference = units - row_units
            wedge_positions = typesetting.calculate_wedges(difference,
                                                           set_width,
                                                           brit_pica)
            if difference:
                # If we need to correct the width -
                # we must cast with the S needle
                signals = column + ' S ' + str(row)
            else:
                signals = column + ' ' + str(row)
            # Ask for number of sorts and lines, no negative numbers here
            prompt = '\nHow many sorts per line? (default: 10): '
            sorts = abs(ui.enter_data_spec_type_or_blank(prompt, int) or 10)
            prompt = '\nHow many lines? (default: 1): '
            lines = abs(ui.enter_data_spec_type_or_blank(prompt, int) or 1)
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
                        if self.cast_from_matrix(signals, sorts, lines,
                                                 wedge_positions):
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
                    ui.simple_menu(message, options)()
            except exceptions.ChangeParameters:
                # Skip the menu and casting altogether, repeat the outer loop
                pass

    def cast_spaces(self):
        """cast_spaces():

        Spaces casting routine, based on the position in diecase.
        Ask user about the space width and measurement unit.
        """
        # Ask about line length
        prompt = 'Galley line length? [pica or cicero] (default: 25) : '
        line_length = ui.enter_data_spec_type_or_blank(prompt, int) or 25
        line_length = abs(line_length)
        # Measurement system
        options = {'A': 0.1660,
                   'B': 0.1667,
                   'D': 0.1776,
                   'F': 0.1629}
        message = ('Measurement? [A]merican Johnson pica = 0.166", '
                   '[B]ritish pica = 0.1667",\n [D]idot cicero = 0.1776", '
                   '[F]ournier cicero = 0.1629": ')
        pica_def = ui.simple_menu(message, options)
        # We need to choose a wedge unless we did it earlier
        wedge = self.wedge or wedge_data.choose_wedge()
        (_, _, set_width, brit_pica, unit_arrangement) = wedge
        # Unit line length:
        unit_line_length = int(18 * pica_def / 0.1667 * line_length *
                               set_width / 12)
        # Now we can cast multiple different spaces
        while True:
            ui.clear()
            ui.display('Spaces / quads casting\n\n')
            prompt = 'Column: NI, NL, A...O? (default: G): '
            # Got no signals? Use G5.
            column = ''
            column_symbols = ['NI', 'NL'] + [ltr for ltr in 'ABCDEFGHIJKLMNO']
            while column not in column_symbols:
                column = ui.enter_data_or_blank(prompt).upper() or 'G'
            prompt = 'Row: 1...16? (default: 2): '
            # Initially set this to zero to enable the while loop
            row = 0
            width = 0
            # Not using unit shift by default
            unit_shift = False
            # Ask for row number
            while row not in range(1, 17):
                row = abs(ui.enter_data_spec_type_or_blank(prompt, int) or 2)
            if row == 16:
                question = 'Trying to access 16th row. Use unit shift?'
                unit_shift = ui.yes_or_no(question)
                row = 15
                if not unit_shift:
                    ui.display('Cannot access the 16th row; using 15 instead')
                    ui.yes_or_no('Is it okay?') or exceptions.return_to_menu()
            # Correct the column number if using unit shift
            if unit_shift:
                column = column.replace('D', 'E F')
                column += ' D'
            # Determine the unit width for a row
            try:
                row_units = unit_arrangement[row - 1]
            except (IndexError, KeyError):
                row_units = 6
            prompt = '\nHow many lines? (default: 1): '
            lines = abs(ui.enter_data_spec_type_or_blank(prompt, int) or 1)
            # Space width in points
            options = {'6': 1/6,
                       '4': 1/4,
                       '3': 1/3,
                       '2': 1/2,
                       '1': 1,
                       'C': 0}
            message = ('Space width? [6] = 1/6em, [4] = 1/4em, [3] = 1/3em, '
                       '[2] = 1/2em, [1] = 1em, [C] for custom width: ')
            # Width in points
            width = ui.simple_menu(message, options) * 12
            # Ask about custom value, then specify units
            if not width:
                while width < 1 or width > 20:
                    prompt = 'Custom width in points (decimal, 1...20) ? : '
                    width = ui.enter_data_spec_type_or_blank(prompt, float)
            # We now have width in pica points
            # If we don't use an old British pica wedge, we must take
            # the pica difference into account
            # Calculate unit width of said number of points
            # We do it this way:
            # units = picas * set_width/12 * 18
            # a pica is 12 points, so:
            # units = points * set_width/12 * 1 / 12 * 18
            # 18 / (12*12) = 0.125, hence division by 8
            factor = pica_def / 0.1667
            sort_units = round(width * factor * set_width / 8, 2)
            # How many spaces will fit in a line? Calculate it...
            # We add 5 em-quads at O15 before and after the proper spaces
            # We need 180 additional units for that - need to subtract
            allowance = unit_line_length - 180
            sorts_number = int(allowance // sort_units)
            # The first line will be filled to the brim with em-quads
            # i.e. 18-unit spaces
            # Put as many as we can
            quads_number = int(unit_line_length // 18)
            # Check if the corrections are needed at all
            difference = sort_units - row_units
            # Calculate the wedge positions
            wedge_positions = typesetting.calculate_wedges(difference,
                                                           set_width,
                                                           brit_pica)
            if difference:
                # If we need to correct the width -
                # we must cast with the S needle
                signals = column + ' S ' + str(row)
            else:
                signals = column + ' ' + str(row)
            # Determine the number of quads per line to cast
            # After entering parameters, ask the operator if they're OK
            try:
                while True:
                    # Inner loop
                    # Menu subroutines
                    def cast_it():
                        """Cast the combination or go back to menu"""
                        message = ('\nFirst, we cast a line of em-quads '
                                   'to heat up the mould. Discard them.\n')
                        ui.display(message)
                        self.cast_from_matrix('O15', quads_number)
                        for n in range(lines):
                            ui.display('Now casting line %s' % str(n + 1))
                            ui.display('\nFive quads before - discard them.\n')
                            self.cast_from_matrix('O15', end_galley_trip=False,
                                                  machine_check=False)
                            ui.display('\nSpaces of desired width...\n')
                            self.cast_from_matrix(signals, sorts_number, 1,
                                                  wedge_positions,
                                                  end_galley_trip=False,
                                                  machine_check=False)
                            ui.display('\nFive quads after - discard them.\n')
                            self.cast_from_matrix('O15', machine_check=False)
                    # End of menu subroutines.
                    options = {'C': cast_it,
                               'D': exceptions.change_parameters,
                               'M': exceptions.return_to_menu,
                               'E': exceptions.exit_program}
                    info = ['Row: %s' % row,
                            'Column: %s' % column,
                            'Width in points: %s' % width,
                            'Width in %s-set units: %s' % (set_width,
                                                           sort_units),
                            '0075 wedge at: %s' % wedge_positions[0],
                            '0005 wedge at: %s' % wedge_positions[1],
                            'Line length in picas/ciceros: %s' % line_length,
                            'Number of sorts per line: %s' % sorts_number,
                            'Number of lines: %s' % lines]
                    for message in info:
                        ui.display(message)
                    message = ('[C]ast it, [D]ifferent parameters, '
                               '[M]enu or [E]xit? ')
                    ui.simple_menu(message, options)()
            except exceptions.ChangeParameters:
                # Skip the menu and casting altogether, repeat the outer loop
                pass

    @use_caster
    def cast_from_matrix(self, signals, num=5, lines=1,
                         wedge_positions=(3, 8),
                         start_galley_trip=False,
                         end_galley_trip=True,
                         machine_check=True):
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
        self.line_aborted = 0
        (pos_0075, pos_0005) = (str(x) for x in wedge_positions)
        # Signals for setting 0005 and 0075 justification wedges
        # Strip O and 15
        set_0005 = parsing.signals_parser('N J S 0005 %s' % pos_0005, True)
        set_0075 = parsing.signals_parser('N K S 0075 %s' % pos_0075, True)
        # Galley trip signal
        galley_trip = parsing.signals_parser('N K J S 0005 0075 %s' % pos_0005)
        # Parse the combination
        combination = parsing.signals_parser(signals, strip_o15=True)
        # Check if the machine is running first, end here if not
        if machine_check:
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
                if start_galley_trip:
                    # Double justification
                    ui.display('Starting the pump and putting the line out...')
                    self.caster.process_signals(galley_trip)
                    self.caster.process_signals(set_0075)
                else:
                    # Starting a job
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
                if end_galley_trip:
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
            signals = ui.enter_data_or_blank(prompt)
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
            ui.simple_menu('\n[C]ontinue, [M]enu or [E]xit? ', options)()
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

    def align_mould(self):
        """align_mould:

        Calculates the width, displays it and casts some 9-unit characters.
        Then, the user measures the width and adjusts the mould opening width.
        """
        intro = ('Mould blade opening calibration:\n'
                 'Cast some 9-unit characters, then measure the width.\n'
                 'Adjust if needed.')
        ui.display(intro)
        # Check if wedge is selected
        if self.wedge:
            set_width = self.wedge[2]
            brit_pica = self.wedge[3]
        else:
            set_width = ui.enter_data_spec_type('Set width? : ', float)
            brit_pica = ui.yes_or_no('British old pica wedge - .1667"? : ')
        # Selected
        if brit_pica:
            pica = 0.1667
        else:
            pica = 0.166
        # We calculate the width of double 9 units = 18 units, i.e. 1 pica em
        em_width = pica * set_width / 12
        ui.display('Type 9 units (1en) width: %s' % round(em_width / 2, 4))
        ui.display('Type 18 units (1em) width: %s' % round(em_width, 4))
        while True:
            # Subroutines for menu options
            def continue_aligning():
                """Do nothing"""
                pass
            # Finished. Return to menu.
            options = {'C': continue_aligning,
                       'M': exceptions.return_to_menu,
                       'E': exceptions.exit_program}
            ui.simple_menu('\n[C]ontinue, [M]enu or [E]xit? ', options)()
            # Cast 5 nine-unit quads
            # End here if casting unsuccessful.
            ui.display('Now casting 9-units spaces')
            if not self.cast_from_matrix('G5', 7):
                continue
            # At the end of successful sequence, some info for the user:
            ui.display('Done. Compare the lengths and adjust if needed.')

    def align_diecase(self):
        """align_diecase:

        Casts the "en dash" characters for calibrating the character X-Y
        relative to type body.
        """
        intro = ('X-Y character calibration:\n'
                 'Cast some en-dashes and/or lowercase "n" letters, '
                 'then check the position of the character relative to the '
                 'type body.\nAdjust if needed.')
        ui.display(intro)
        try:
            # Find the en-dash automatically
            dash_position = [mat[2] + str(mat[3])
                             for mat in self.diecase_layout
                             if mat[0] == '–'][0]
        except (exceptions.MatrixNotFound, TypeError, IndexError):
            # Choose it manually
            dash_position = ui.enter_data_or_blank('En dash (–) at: ').upper()
        try:
            # Find the "n" letter automatically
            lowercase_n_position = [mat[2] + str(mat[3])
                                    for mat in self.diecase_layout
                                    if mat[0] == 'n'][0]
        except (exceptions.MatrixNotFound, TypeError, IndexError):
            # Choose itmanually
            lowercase_n_position = ui.enter_data_or_blank('"n" at: ').upper()
        while True:
            # Subroutines for menu options
            def continue_aligning():
                """Do nothing"""
                pass
            # Finished. Return to menu.
            options = {'C': continue_aligning,
                       'M': exceptions.return_to_menu,
                       'E': exceptions.exit_program}
            ui.simple_menu('\n[C]ontinue, [M]enu or [E]xit? ', options)()
            # Cast 5 nine-unit quads
            # End here if casting unsuccessful.
            if dash_position:
                ui.display('Now casting en dash')
                if not self.cast_from_matrix(dash_position, 7):
                    continue
            if lowercase_n_position:
                ui.display('Now casting lowercase "n"')
                if not self.cast_from_matrix(lowercase_n_position, 7):
                    continue
            # At the end of successful sequence, some info for the user:
            ui.display('Done. Compare the lengths and adjust if needed.')

    def line_casting(self):
        """line_casting:

        Allows us to use caster for casting single lines.
        This means that the user enters a text to be cast,
        gives the line length, chooses alignment and diecase.
        Then, the program composes the line, justifies it, translates it
        to Monotype code combinations.

        This allows for quick typesetting of short texts, like names etc.
        """
        # Initialize the typesetter for a chosen diecase
        typesetter = typesetting.Typesetter()
        typesetter.session_setup(self.diecase_id)
        # Enter text
        text = ui.enter_data("Enter text to compose: ")
        typesetter.text_source = typesetter.parse_and_generate(text)
        # Translate the text to Monotype signals
        # Compose the text
        typesetter.compose()
        self.ribbon_contents = typesetter.apply_justification()
        # Ask whether to display buffer contents
        if ui.yes_or_no('Show the codes?'):
            self.preview_ribbon()
        # We're casting
        if ui.yes_or_no('Cast it?'):
            try:
                self.cast_composition()
            except exceptions.ReturnToMenu:
                # If casting aborted - don't go back to menu
                pass

    def preview_ribbon(self):
        """preview_ribbon:

        Determines if we have a ribbon file that can be previewed,
        and displays its contents line by line, or displays
        an error message.
        """
        ui.clear()
        ui.display('Ribbon preview:\n')
        try:
            for line in self.ribbon_contents:
                ui.display(line)
        except KeyboardInterrupt:
            # Press ctrl-C to abort displaying long ribbons
            pass
        ui.hold_on_exit()

    def heatup(self):
        """heatup

        Allows to heat up the mould before casting, in order to
        stabilize the mould temperature (affects the type quality).
        Casts two lines of em-quads, which can be thrown back to the pot.
        """
        ui.clear()
        self.cast_from_matrix('O15', num=20, lines=2)

    def service_menu(self):
        """Settings and alignment menu for servicing the caster"""
        # Subroutines end here
        options = [('Return to main menu', exceptions.menu_level_up),
                   ('Test the pneumatics, signal after signal', self.test_air),
                   ('Send specified signals to caster', self.send_combination),
                   ('Calibrate the space transfer wedge', self.align_wedges),
                   ('Calibrate mould opening', self.align_mould),
                   ('Calibrate diecase X-Y', self.align_diecase),
                   ('Cast some quads to heat up the mould', self.heatup)]
        header = ('Diagnostics and machine calibration menu:\n\n')
        # Keep displaying the menu and go back here after any method ends
        while True:
            try:
                # Catch "return to menu" and "exit program" exceptions here
                ui.menu(options, header=header)()
            except exceptions.ReturnToMenu:
                # Stay in the menu
                pass

    def display_additional_info(self):
        """Collect ribbon, diecase and wedge data here"""
        displayed_info = []
        if self.ribbon_metadata:
            displayed_info.append('Ribbon title: %s' % self.ribbon_metadata[0])
            displayed_info.append('Author: %s' % self.ribbon_metadata[1])
        if self.diecase:
            displayed_info.append('Diecase: %s' % self.diecase_id)
            displayed_info.append('Typeface: %s' % self.diecase[4])
            displayed_info.append('Type series: %s' % self.diecase[0])
            displayed_info.append('Type size: %s' % self.diecase[1])
        if self.wedge:
            displayed_info.append('Wedge series: %s' % self.wedge[1])
            displayed_info.append('Set width: %s' % self.wedge[2])
            displayed_info.append('British pica wedge?: %s' % self.wedge[3])
            displayed_info.append('Unit values: %s' % self.wedge[4])
        return '\n'.join(displayed_info)

    def show_diecase_layout(self):
        """Shows the diecase layout"""
        layout = self.diecase_layout
        unit_arrangement = self.unit_arrangement or None
        matrix_data.display_diecase_layout(layout, unit_arrangement)
        ui.confirm('[Enter] to continue...')

    def data_menu(self):
        """Choose the ribbon and diecase, if needed"""
        # Start with an empty options list
        options = []

        # Define subroutines used only here
        def ribbon_from_file():
            """ribbon_from_file

            Asks the user for the ribbon filename.
            Checks if the file is readable, and pre-processes it.
            """
            ribbon_file = ui.enter_input_filename()
            ribbon_contents = parsing.read_file(ribbon_file)
            metadata = parsing.get_metadata(ribbon_contents)
            # Clear the previous ribbon, diecase, wedge selections
            self.ribbon_contents = None
            self.ribbon_file = None
            self.ribbon_metadata = None
            self.diecase = None
            self.diecase_id = None
            self.diecase_layout = None
            self.unit_arrangement = None
            self.wedge = None
            author, title, unit_shift, diecase_id = None, None, False, None
            if 'diecase' in metadata:
                diecase_id = metadata['diecase']
                # Try to choose the diecase
                try:
                    choose_diecase(diecase_id)
                except (KeyError, exceptions.MenuLevelUp):
                    pass
            if 'author' in metadata:
                author = metadata['author']
            if ('unit-shift' in metadata and
                    metadata['unit-shift'].lower() in ['true', 'on', '1']):
                unit_shift = True
            if ('unit-shift' in metadata and
                    metadata['unit-shift'].lower() in ['false', 'off', '0']):
                unit_shift = False
            if 'title' in metadata:
                title = metadata['title']
            # Reset the "line aborted" on a new casting job
            self.line_aborted = 0
            # Set up casting session attributes
            self.ribbon_file = ribbon_file
            self.ribbon_contents = ribbon_contents
            self.ribbon_metadata = [title, author, diecase_id, unit_shift]
            self.diecase_id = diecase_id
            # Get back to menu
            exceptions.menu_level_up()

        def ribbon_from_db():
            """Get the ribbon stored in database"""
            # Choose the ribbon
            ribbon_id = typesetting_data.choose_ribbon()
            # If canot choose the ribbon, go back to menu
            if not ribbon_id:
                return False
            # Clear the previous ribbon, diecase, wedge selections
            self.ribbon_contents = None
            self.ribbon_file = None
            self.ribbon_metadata = None
            self.diecase = None
            self.diecase_id = None
            self.diecase_layout = None
            self.unit_arrangement = None
            self.wedge = None
            ribbon_metadata = typesetting_data.get_ribbon_metadata(
                ribbon_id)
            ribbon_contents = typesetting_data.get_ribbon_contents(
                ribbon_id)
            # Get the metadata
            diecase_id = ribbon_metadata[2]
            # Select the matrix case automatically
            try:
                choose_diecase(diecase_id)
            except (KeyError, exceptions.MenuLevelUp):
                pass
            # Reset the "line aborted" on a new casting job
            self.line_aborted = 0
            # Set up casting session attributes
            self.ribbon_contents = ribbon_contents
            self.ribbon_metadata = ribbon_metadata
            self.diecase_id = diecase_id
            # Get back to menu
            exceptions.menu_level_up()

        def choose_diecase(diecase_id=None):
            """choose_diecase

            Allows the user to choose the diecase manually.
            Deletes any ribbon choice (to prevent casting the ribbon with a
            wrong diecase).
            """
            # Display a warning if function called without argument
            # and diecase and ribbon are chosen
            if self.ribbon_metadata and self.diecase and not diecase_id:
                ui.display('WARNING: you have already chosen a ribbon!\n'
                           'A diecase has been selected automatically.'
                           '\nChoosing a different diecase will unselect '
                           'the ribbon.')
                if not ui.yes_or_no('Proceed?'):
                    return False
                # Clear any ribbon and wedge choice
                self.ribbon_metadata = None
                self.ribbon_contents = None
            # Wedge will be automatically or manually selected soon
            # Temporarily, no wedge
            self.wedge = None
            # Choose a diecase automatically (if fed to function)
            # or manually
            self.diecase_id = diecase_id or matrix_data.choose_diecase()
            # Get diecase parameters
            self.diecase = matrix_data.get_diecase_parameters(self.diecase_id)
            # Often used parameters deserve their own object attributes
            self.diecase_layout = self.diecase[5]
            # Get wedge parameters
            try:
                # Look up the wedge in database automatically
                self.wedge = wedge_data.wedge_by_name_and_width(
                    self.diecase[2], self.diecase[3])
            except exceptions.NoMatchingData:
                # Select it manually
                try:
                    choose_wedge()
                # Catch the exception at the end of choose_wedge
                except exceptions.MenuLevelUp:
                    pass
            # Read the UA for the wedge
            self.unit_arrangement = self.wedge[-1]
            # Ask whether to show diecase layout:
            if self.diecase_layout and ui.yes_or_no('Show diecase layout?'):
                self.show_diecase_layout()
            exceptions.menu_level_up()

        def choose_wedge():
            """Sets or changes a wedge to user-selected one"""
            if self.diecase and self.wedge:
                ui.display('WARNING: A proper wedge has been selected '
                           'automatically when selecting a diecase.\n'
                           'Changing this may led to casting type either '
                           'too narrow or to wide!')
                if not ui.yes_or_no('Proceed?'):
                    return False
            self.wedge = wedge_data.choose_wedge()
            self.unit_arrangement = self.wedge[-1]
            exceptions.menu_level_up()

        def check_database():
            """Displays database-related options"""
            opts = (('View ribbons in database', typesetting_data.show_ribbon),
                    ('Choose the ribbon from database', ribbon_from_db))
            if typesetting_data.check_if_ribbons():
                for option in opts:
                    options.append(option)

        # Subroutines end here
        # Header is static
        header = 'Input data choice menu:\n\n'
        # Keep displaying the menu and go back here after any method ends
        while True:
            # Options list is dynamic
            options = [('Return to main menu', exceptions.menu_level_up)]
            check_database()
            options.extend([('Choose the ribbon from file', ribbon_from_file),
                            ('Choose the matrix case', choose_diecase),
                            ('Choose the wedge', choose_wedge)])
            try:
                # Catch "return to menu" and "exit program" exceptions here
                ui.menu(options, header=header,
                        footer=self.display_additional_info())()
            except exceptions.ReturnToMenu:
                # Stay in the menu
                pass

    def __exit__(self, *args):
        ui.debug_info('Exiting casting job context.')


def main_menu(work=Casting()):
    """main_menu:

    Calls ui.menu() with options, a header and a footer.
    Options: {option_name : description}
    Header: string displayed over menu
    Footer: string displayed under menu (all info will be added here).
    """
    # Empty options list
    options = []

    # Declare subroutines
    def debug_notice():
        """Prints a notice if the program is in debug mode."""
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
        # Display the line last casting was aborted on, if applicable:
        if work.line_aborted:
            info.append('Last casting was aborted on line ' +
                        str(work.line_aborted))
        # Convert it all to a multiline string
        return '\n'.join(info)

    def cast_or_punch():
        """cast_or_punch:

        Determines if the caster specified for the job is actually
        a perforator - if so, a "punch ribbon" feature will be
        available instead of "cast composition".
        """
        if work.caster.is_perforator and work.ribbon_contents:
            options.append(('Punch composition', work.punch_composition))
        elif work.ribbon_contents:
            options.append(('Cast composition', work.cast_composition))

    def check_diecase():
        """Checks if diecase is set and enables certain options"""
        opts = (('View the matrix case layout', work.show_diecase_layout),
                ('Compose and cast a line of text', work.line_casting))
        if work.diecase:
            for option in opts:
                options.append(option)

    def check_ribbon():
        """Checks if ribbon is selected and allows to display it"""
        if work.ribbon_contents:
            options.append(('Preview ribbon', work.preview_ribbon))

    # End of menu subroutines
    # Header is static, menu content is dynamic
    header = ('rpi2caster - CAT (Computer-Aided Typecasting) '
              'for Monotype Composition or Type and Rule casters.'
              '\n\n'
              'This program reads a ribbon (input file) '
              'and casts the type on a composition caster.' +
              debug_notice() + '\n\nMain Menu:')
    # Keep displaying the menu and go back here after any method ends
    while True:
        try:
            # Menu content is dynamic and must be refreshed each time
            # Now construct the menu, starting with available options
            options = [('Exit program', exceptions.exit_program),
                       ('Select ribbon or diecase...', work.data_menu)]
            check_ribbon()
            cast_or_punch()
            check_diecase()
            options.extend([('Cast sorts from matrix coordinates',
                             work.cast_sorts),
                            ('Cast spaces / quads', work.cast_spaces),
                            ('Caster diagnostics and calibration...',
                             work.service_menu)])
            # Catch "return to menu" and "exit program" exceptions here
            footer = additional_info() + '\n' + work.display_additional_info()
            ui.menu(options, header=header, footer=footer)()
        except (exceptions.ReturnToMenu, exceptions.MenuLevelUp):
            # Will skip to the end of the loop, and start all over
            pass
        except (KeyboardInterrupt, exceptions.ExitProgram):
            # Will exit program
            ui.exit_program()
