# -*- coding: utf-8 -*-
"""
casting:

A module for everything related to working on a Monotype composition caster:
-casting composed type,
-punching paper tape (ribbon) for casters without interfaces,
-casting typecases based on character frequencies,
-casting a desired number of characters from matrix with x, y coordinates,
-composing and casting a line of text (not there yet)
-testing all valves, lines and pinblocks,
-calibrating the space transfer wedge, mould opening, diecase draw rods,
 position of character on type body
-sending any codes/combinations to the caster.
"""

# IMPORTS:
from collections import deque
from contextlib import suppress
from itertools import cycle
from time import sleep
# Signals parsing methods for rpi2caster
from . import parsing as p
# Custom exceptions
from . import exceptions as e
# Constants shared between modules
from . import constants as c
# Caster backend
from .monotype import MonotypeCaster
# Casting stats
from .casting_stats import Stats
# Globally selected UI
from .ui import UIFactory, Abort
# Typecase casting needs this
from . import letter_frequencies
# Typesetting functions
from . import typesetting_funcs as tsf
# Decorator functions
from . import decorators as dec
# Matrix, wedge and typesetting data models
from .ribbon_controller import TypesettingContext
from .typesetting import GalleyBuilder

UI = UIFactory()


class Casting(TypesettingContext):
    """Casting:

    Methods related to operating the composition caster.
    Requires configured caster.

    All methods related to operating a composition caster are here:
    -casting composition and sorts, punching composition,
    -calibrating the caster,
    -testing the interface,
    -sending an arbitrary combination of signals,
    -casting spaces to heat up the mould."""

    def __init__(self):
        # Caster for this job
        self.caster = MonotypeCaster()
        self.stats = Stats(self)

    @dec.choose_sensor_and_driver
    def cast_ribbon(self, ribbon):
        """
        Main casting routine.
        Cast or punch a sequence of codes, displaying the statistics.
        First choose a number of repetitions and lines skipped (for casting),
        diagnostics and punching will be processed from start to end.
        For each run, display statistics and send signals to the caster
        one by one, until a whole sequence is cast.
        If casting multiple runs, repeat until all are done.
        A run may not be successful (casting is aborted by machine stop
        or ctrl-C interrupt) - in this case, lines cast successfully
        may be skipped, and the rest will be cast.
        """
        def rewind_if_needed():
            """Decide whether to rewind the ribbon or not"""
            nonlocal ribbon
            forward = (mode.testing or mode.punching or not
                       p.stop_comes_first(ribbon))
            ribbon = ribbon if forward else [x for x in reversed(ribbon)]

        def skip_lines():
            """Skip a definite number of lines"""
            nonlocal queue
            # Apply constraints: 0 <= lines_skipped < lines in ribbon
            lines_skipped = self.stats.lines_skipped
            if lines_skipped:
                UI.display('Skipping %s lines' % lines_skipped)
            # Take away combinations until we skip the desired number of lines
            # BEWARE: ribbon starts with galley trip!
            # We must give it back after lines are taken away
            code = ''
            queue = deque(ribbon)
            while lines_skipped > 0:
                parsed = p.ParsedRecord(queue.popleft())
                lines_skipped -= 1 * parsed.code.is_newline
            # give the last code back
            queue.appendleft(code)

        def set_runs():
            """Set a number of casting runs"""
            prompt = 'How many times do you want to cast this?'
            # Set the number of runs before starting the job
            # 0 is a valid option here
            runs = -1 if mode.casting else 1
            while runs < 0:
                runs = UI.enter(prompt, default=1, datatype=int)
            self.stats.runs = runs

        def set_session_lines_skipped():
            """Skip lines before casting or after aborting the job"""
            lines_in_ribbon = max(1, self.stats.get_ribbon_lines())
            if mode.casting and self.stats.runs > 1 and lines_in_ribbon > 2:
                prompt = ('How many lines to skip for ALL runs?\n'
                          'min: 0, max: %s' % (lines_in_ribbon - 2))
                # Skip lines effective for ALL runs
                lines_skipped = -1
                while not 0 <= lines_skipped < lines_in_ribbon:
                    lines_skipped = UI.enter(prompt, default=0, datatype=int)
            else:
                lines_skipped = 0
            self.stats.session_lines_skipped = lines_skipped

        def set_run_lines_skipped():
            """Set lines to skip for the upcoming run only"""
            lines_in_ribbon = max(1, self.stats.get_ribbon_lines())
            lines_ok = self.stats.get_lines_done()
            # Offer to skip lines only if enough of them were cast
            prompt = ('How many lines to skip for THIS run? '
                      'min: 0, max: %s' % (lines_in_ribbon - 2))
            # Skip lines effective for UPCOMING run only
            if mode.casting and lines_in_ribbon > 2:
                if lines_ok > 0:
                    UI.display('%s lines were cast in the last run.\n'
                               'We can skip up to %s.'
                               % (lines_ok, lines_in_ribbon - 2))
                lines_skipped = -1
                while not 0 <= lines_skipped <= lines_in_ribbon - 2:
                    lines_skipped = UI.enter(prompt,
                                             default=lines_ok, datatype=int)
            else:
                lines_skipped = 0
            self.stats.run_lines_skipped = lines_skipped

        def preheat_if_needed():
            """Things to do only once during the whole casting session"""
            prompt = 'Cast two lines of quads to heat up the mould?'
            # Use this only in casting or calibration;
            # enable by default in casting, disable in calibration
            casting = mode.casting or mode.calibration
            if casting and UI.confirm(prompt, not mode.calibration):
                quad = self.quad
                quad_qty = int(self.measure.wedge_set_units // quad.units)
                text = 'Casting quads for mould heatup'
                heatup = (['%s preheat' % quad] * quad_qty +
                          tsf.double_justification(comment=text)) * 2
                old_stats = self.stats
                try:
                    # Use different stats for preheat quads
                    self.stats = Stats(self)
                    self.caster.sensor.check_if_machine_is_working()
                    cast_queue(reversed(heatup))
                finally:
                    self.stats = old_stats

        def cast_queue(sequence=None):
            """Casts the sequence of codes in given sequence.
            This function is executed until the sequence is exhausted
            or casting is stopped by machine or user."""
            # in punching mode, lack of row will trigger signal 15,
            # lack of column will trigger signal O
            # in punching and testing mode, signal O or 15 will be present
            # in the output combination as O15
            parsed = p.ParsedRecord
            for item in sequence or queue:
                record = parsed(item, row_16_addressing=mode.row_16_addressing,
                                default_o15=mode.punching,
                                signal_o15=mode.punching or mode.testing)
                try:
                    if not record.signals:
                        UI.display_header(record.comment)
                        continue
                    self.stats.parsed_record = record
                    UI.display_parameters({record.comment:
                                           self.stats.code_parameters})
                    self.caster.process(record.adjusted_signals)
                except (e.MachineStopped, KeyboardInterrupt, EOFError):
                    # Allow resume in punching mode, otherwise stop
                    if (mode.punching and not mode.testing and
                            UI.confirm('Resume punching?', default=True)):
                        self.caster.process(record.adjusted_signals)
                    else:
                        return False
            return True

        def after_casting(casting_success):
            """After the run is finished, decide whether to repeat or not
            (for casting, set number of repetitions; for other modes, just
            ask if user wants to do it again). If failed, offer to repeat
            the run with skipped lines."""
            self.stats.end_run()
            runs_left = self.stats.runs_remaining
            if casting_success:
                more_runs = -1 if not runs_left else 0
                # Add some runs more if necessary after finished
                prompt = 'Casting finished; add more runs - how many?'
                while more_runs < 0:
                    more_runs = (UI.enter(prompt, default=0, datatype=int)
                                 if mode.casting
                                 else 1 if UI.confirm('Repeat?', True) else 0)
                self.stats.runs += more_runs
            else:
                # Retry in casting and calibration modes
                # In case of retrying, set the run lines skipped
                # If not retrying, but there are still some more runs to go,
                # ask if user wishes to go on with casting or abort
                self.stats.reset_last_run_stats()
                caster = mode.casting or mode.calibration
                prompt = '%s runs remaining. Continue casting?' % runs_left
                if caster and UI.confirm('Retry the last run?', default=True):
                    # Casting aborted - ask if user wants to repeat
                    set_run_lines_skipped()
                    self.stats.runs += 1
                    # Start this run again
                elif runs_left and not UI.confirm(prompt, default=True):
                    raise e.ReturnToMenu

        # Helpful aliases
        mode = self.caster.mode
        queue = ribbon
        try:
            self.stats = Stats(self)
            # Ribbon pre-processing and casting parameters setup
            rewind_if_needed()
            self.stats.ribbon = ribbon
            UI.display_parameters({'Ribbon info':
                                   self.stats.ribbon_parameters})
            set_runs()
            set_session_lines_skipped()
            set_run_lines_skipped()
            UI.display_parameters({'Session info':
                                   self.stats.session_parameters})
            # Mould heatup
            preheat_if_needed()
            # Cast until there are no more runs left
            while self.stats.runs_remaining:
                # Prepare the ribbon ad hoc
                skip_lines()
                self.stats.queue = queue
                # Make sure the machine is turning
                self.caster.sensor.check_if_machine_is_working()
                # Cast the run
                outcome = cast_queue()
                after_casting(outcome)
        except e.ReturnToMenu:
            # Needed for proper cleanup and resetting the modes by decorators
            return False

    @dec.temp_wedge
    def cast_sorts(self):
        """Sorts casting routine, based on the position in diecase.
        Ask user about the diecase row & column, as well as number of sorts.
        """
        order = []
        while True:
            char = (UI.enter('Character?', blank_ok=True) if self.diecase
                    else '')
            matrix = self.find_matrix(char)
            self.specify_units(matrix)
            qty = UI.enter('How many sorts?', default=10, datatype=int)
            order.append((matrix, qty))
            prompt = 'More sorts? Otherwise, start casting'
            if not UI.confirm(prompt, default=True):
                break
        # Now let's calculate and cast it...
        self.cast_galley(order)

    @dec.temp_wedge
    def cast_typecases(self):
        """Casting typecases according to supplied font scheme."""
        freqs = letter_frequencies.CharFreqs()
        freqs.define_case_ratio()
        freqs.define_scale()
        style_mgr = self.diecase.styles
        style_mgr.choose()
        order = []
        for style in style_mgr:
            UI.display_header(style.name.capitalize())
            if len(style_mgr.list) == 1 or style is style_mgr.default:
                scale = 1.0
            else:
                scale = UI.enter('Scale for %s?' % style.name,
                                 default=100, datatype=float) / 100.0
            for char, chars_qty in freqs.type_bill:
                qty = int(scale * chars_qty)
                UI.display('%s: %s' % (char, chars_qty))
                matrix = self.find_matrix(char, style, manual_choice=True)
                order.append((matrix, qty))
        self.cast_galley(order)

    @dec.temp_wedge
    def cast_spaces(self):
        """Spaces casting routine, based on the position in diecase.
        Ask user about the space width and measurement unit.
        """
        order = []
        while True:
            matrix = self.get_space()
            self.specify_space_width(matrix)
            prompt = 'How many lines?'
            lines = UI.enter(prompt, default=1, datatype=int)
            order.extend([(matrix, 0)] * lines)
            prompt = 'More spaces? Otherwise, start casting'
            if not UI.confirm(prompt, default=True):
                break
        self.cast_galley(order)

    @dec.cast_or_punch_result
    @dec.temp_measure
    def cast_galley(self, order=()):
        """Cast a series of type, filling lines of given width to the brim.

        Each character is specified by a tuple: (matrix, qty)
            where matrix is a Matrix object,
            qty is quantity (0 for a filled line,
                             >0 for a given number of chars).

        If there is too many chars for a single line - will cast more lines.
        Last line will be quadded out.
        Characters other than low spaces will be separated by double G2 spaces
        to prevent matrices from overheating.
        """
        if not order:
            e.return_to_menu()
        # 1 quad before and after the line
        quad_padding = 1
        quad = self.get_space(units=18)
        # Leave some slack to adjust the line
        length = self.measure.ems - 2 * quad_padding * quad.ems
        # Build a sequence of matrices for casting
        # If n is 0, we fill the line to the brim
        queues = ([mat] * n if n else [mat] * int((length // mat.ems) - 1)
                  for (mat, n) in order)
        matrix_stream = (mat for batch in queues for mat in batch)
        # Initialize the galley-constructor
        builder = GalleyBuilder(self, matrix_stream)
        builder.quad_padding = quad_padding
        builder.cooldown_spaces = True
        job = 'punching' if self.caster.mode.punching else 'casting'
        UI.display('Generating a sequence for %s...' % job)
        queue = builder.build_galley()
        UI.display('\nReady for %s...\n\n' % job)
        UI.display('Each line will have two em-quads at the start '
                   'and at the end, to support the type.')
        return queue

    @dec.cast_or_punch_result
    def cast_composition(self):
        """Casts or punches the ribbon contents if there are any"""
        if not self.ribbon.contents:
            e.return_to_menu()
        return self.ribbon.contents

    @dec.cast_or_punch_result
    @dec.temp_measure
    @dec.temp_wedge
    def quick_typesetting(self, text=None):
        """Allows us to use caster for casting single lines.
        This means that the user enters a text to be cast,
        gives the line length, chooses alignment and diecase.
        Then, the program composes the line, justifies it, translates it
        to Monotype code combinations.

        This allows for quick typesetting of short texts, like names etc.
        """
        # Safeguard against trying to use this feature from commandline
        # without selecting a diecase
        if not self.diecase:
            e.return_to_menu()
        self.source = text or ''
        self.edit_text()
        matrix_stream = self.old_parse_input()
        builder = GalleyBuilder(self, matrix_stream)
        queue = builder.build_galley()
        UI.display('Each line will have two em-quads at the start '
                   'and at the end, to support the type.\n'
                   'Starting with two lines of quads to heat up the mould.\n')
        return queue

    @dec.cast_or_punch_result
    @dec.temp_wedge
    def diecase_proof(self):
        """Tests the whole diecase, casting from each matrix.
        Casts spaces between characters to be sure that the resulting
        type will be of equal width."""
        prompt = ('Matrix case size: 1 for 15x15, 2 for 15x17, 3 for 16x17? '
                  '(leave blank to cancel) : ')
        options = {'1': (15, 15), '2': (15, 17), '3': (16, 17), '': ()}
        rows, columns = 0, 0
        if (rows, columns) not in options.values():
            choice = UI.simple_menu(prompt, options)
            if not choice:
                return
            (rows, columns) = choice
        # Generate column numbers
        columns_list = c.COLUMNS_17 if columns == 17 else c.COLUMNS_15
        # Generate row numbers: 1...15 or 1...16
        rows_list = [num + 1 for num in range(rows)]
        # Sequence to cast starts with pump stop and galley trip
        # (will be cast in reversed order)
        queue = tsf.end_casting() + tsf.galley_trip()
        for row in rows_list:
            # Calculate the width for the GS1 space
            wedge_positions = (3, 8)
            queue.append('O15')
            if self.wedge[row] < 18:
                # How many units do we add or take away?
                delta = 18 - self.wedge[row] - self.wedge[1]
                # We have difference in units of a set:
                # translate to inches and make it 0.0005" steps, add 3/8
                delta *= self.wedge.unit_inch_width
                steps_0005 = int(delta * 2000) + 53
                # Safety limits: upper = 15/15; lower = 1/1
                steps_0005 = min(steps_0005, 240)
                steps_0005 = max(steps_0005, 16)
                steps_0075 = 0
                while steps_0005 > 15:
                    steps_0005 -= 15
                    steps_0075 += 1
                wedge_positions = (steps_0075, steps_0005)
            for column in columns_list:
                queue.append('%s%s' % (column, row))
                if self.wedge[row] < 18:
                    # Skip this for 18 unit rows
                    queue.append('GS1')
            # Quad out, put the row to the galley, set justification
            queue.append('O15')
            queue.extend(tsf.double_justification(wedge_positions))
        if UI.confirm('Proceed?', True):
            return queue

    def diagnostics_submenu(self):
        """Settings and alignment menu for servicing the caster"""
        @dec.testing_mode
        @dec.cast_or_punch_result
        def test_front_pinblock(*_):
            """Sends signals 1...14, one by one"""
            UI.pause('Testing the front pinblock - signals 1 towards 14.')
            return [str(n) for n in range(1, 15)]

        @dec.testing_mode
        @dec.cast_or_punch_result
        def test_rear_pinblock(*_):
            """Sends NI, NL, A...N"""
            UI.pause('This will test the rear pinblock - NI, NL, A...N. ')
            return [x for x in c.COLUMNS_17]

        @dec.testing_mode
        @dec.cast_or_punch_result
        def test_all(*_):
            """Tests all valves and composition caster's inputs in original
            Monotype order:
            NMLKJIHGFSED 0075 CBA 123456789 10 11 12 13 14 0005.
            """
            UI.pause('This will test all the air lines in the same order '
                     'as the holes on the paper tower: \n%s\n'
                     'MAKE SURE THE PUMP IS DISENGAGED.' % ' '.join(c.SIGNALS))
            return [x for x in c.SIGNALS]

        @dec.testing_mode
        @dec.cast_or_punch_result
        def test_justification(*_):
            """Tests the 0075-S-0005"""
            UI.pause('This will test the justification pinblock: '
                     '0075, S, 0005.')
            return ['0075', 'S', '0005']

        @dec.testing_mode
        @dec.choose_sensor_and_driver
        def test_any_code(*_):
            """Tests a user-specified combination of signals"""
            while True:
                UI.display('Enter the signals to send to the caster, '
                           'or leave empty to return to menu: ')
                prompt = 'Signals? (leave blank to exit)'
                string = UI.enter(prompt, blank_ok=True)
                record = p.ParsedRecord(string, signal_o15=True)
                self.caster.output.valves_off()
                if not record.signals:
                    break
                UI.display('Sending %s' % record.signals_string)
                self.caster.output.valves_on(record.signals)

        @dec.testing_mode
        @dec.choose_sensor_and_driver
        def blow_all(*_):
            """Blow all signals for a short time; add NI, NL also"""
            UI.pause('Blowing air through all air pins on both pinblocks...')
            queue = ['NI', 'NL', 'A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7',
                     'H8', 'I9', 'J10', 'K11', 'L12', 'M13', 'N14', 'O15',
                     '0075', '0005', 'S']
            duration = 0.3
            try:
                for sig in cycle(queue):
                    record = p.ParsedRecord(sig, signal_o15=True)
                    sleep(duration)
                    UI.display('Activating %s' % record.signals_string)
                    self.caster.output.valves_on(record.signals)
                    sleep(duration)
                    self.caster.output.valves_off()
                    if not UI.confirm('Repeat?', True):
                        break
            except (KeyboardInterrupt, EOFError):
                self.caster.output.valves_off()

        @dec.choose_sensor_and_driver
        def calibrate_draw_rods(*_):
            """Keeps the diecase at G8 so that the operator can adjust
            the diecase draw rods until the diecase stops moving sideways
            when the centering pin is descending."""
            UI.display('Draw rods calibration:\n'
                       'The diecase will be moved to the central position '
                       '(G8).\n Turn on the machine and adjust the diecase '
                       'draw rods until the diecase stops wobbling.')
            if not UI.confirm('\nProceed?', default=True):
                return None
            self.caster.output.valves_on(['G', '8'])
            UI.pause('Sending G8, waiting for you to stop...')

        @dec.calibration_mode
        @dec.cast_or_punch_result
        def calibrate_wedges(*_):
            """Allows to calibrate the justification wedges so that when you're
            casting a 9-unit character with the S-needle at 0075:3 and 0005:8
            (neutral position), the    width is the same.

            It works like this:
            1. 0075 - turn the pump on,
            2. cast 10 spaces from the specified matrix (default: G9),
            3. put the line to the galley & set 0005 to 8, 0075 to 3, pump on,
            4. cast 10 spaces with the S-needle from the same matrix,
            5. put the line to the galley, then 0005 to turn the pump off.
            """
            UI.display('Transfer wedge calibration:\n\n'
                       'This function will cast two lines of 5 spaces: '
                       'first: G5, second: GS5 with wedges at 3/8. \n'
                       'Adjust the 52D space transfer wedge '
                       'until the lengths are the same.')
            if not UI.confirm('\nProceed?', default=True):
                return None
            sequence = tsf.end_casting()
            sequence.extend(['GS5'] * 7)
            sequence.extend(tsf.double_justification())
            sequence.extend(['G5'] * 7)
            sequence.extend(tsf.double_justification())
            return sequence

        @dec.calibration_mode
        @dec.temp_wedge
        @dec.cast_or_punch_result
        def calibrate_mould_and_diecase(*_):
            """Casts the "en dash" characters for calibrating the character X-Y
            relative to type body."""
            UI.display('Mould blade opening and X-Y character calibration:\n'
                       'Cast G5, adjust the sort width to the value shown.\n'
                       '\nThen cast some lowercase "n" letters and n-dashes, '
                       'check the position of the character relative to the '
                       'type body and adjust the bridge X-Y. '
                       'Repeat if needed.\n')
            em_width = self.wedge.em_inch_width
            UI.display('9 units (1en) is %s" wide' % round(em_width / 2, 4))
            UI.display('18 units (1em) is %s" wide\n' % round(em_width, 4))
            if not UI.confirm('\nProceed?', default=True):
                return None
            # Build character list
            matrix_stream = []
            for char in ('  ', 'n', '--'):
                matrix = self.find_matrix(char, '', manual_choice=True)
                self.specify_units(matrix)
                matrix_stream.append(matrix)
                matrix_stream.append(matrix)
            builder = GalleyBuilder(self, matrix_stream)
            builder.fill_line = False
            queue = builder.build_galley()
            return queue

        @dec.calibration_mode
        @dec.cast_or_punch_result
        def test_row_16(*_):
            """Tests the 16th row with selected addressing mode
            (HMN, KMN, unit-shift). Casts from all matrices in 16th row."""
            UI.display('This will test the 16th row addressing.\n'
                       'If your caster has HMN, KMN or unit-shift attachment, '
                       'turn it on.\n')
            if not UI.confirm('\nProceed?', default=True):
                return None
            queue = tsf.end_casting() + ['%s16' % x for x in c.COLUMNS_17]
            queue.extend(tsf.double_justification(comment='Starting...'))
            return queue

        def finish(*_):
            """Sets the flag to True"""
            nonlocal finished
            finished = True

        def menu_options():
            """Build a list of options, adding an option if condition is met"""
            caster = not self.caster.mode.punching
            opts = [(finish, 'Back', 'Returns to main menu', True),
                    (test_all, 'Test outputs',
                     'Test all the air outputs N...O15, one by one', True),
                    (test_front_pinblock, 'Test the front pin block',
                     'Test the pins 1...14', caster),
                    (test_rear_pinblock, 'Test the rear pin block',
                     'Test the pins NI, NL, A...N, one by one', caster),
                    (blow_all, 'Blow all air pins',
                     'Blow air into every pin for a short time', True),
                    (test_justification, 'Test the justification block',
                     'Test the pins for 0075, S and 0005, one by one', caster),
                    (test_any_code, 'Send specified signal combination',
                     'Send the specified signals to the machine', True),
                    (calibrate_wedges, 'Calibrate the 52D wedge',
                     'Calibrate the space transfer wedge for correct width',
                     caster),
                    (calibrate_mould_and_diecase,
                     'Calibrate mould blade and diecase',
                     'Set the type body width and character-to-body position',
                     caster),
                    (calibrate_draw_rods, 'Calibrate diecase draw rods',
                     'Keep the matrix case at G8 and adjust the draw rods',
                     caster),
                    (test_row_16, 'Test HMN, KMN or unit-shift',
                     'Cast type from row 16 with chosen addressing mode',
                     caster)]
            return [(function, description, long_description) for
                    (function, description, long_description, condition)
                    in opts if condition]

        header = ('Diagnostics and machine calibration menu:\n\n')
        # Keep displaying the menu and go back here after any method ends
        finished = False
        while not finished:
            with suppress(Abort, e.ReturnToMenu):
                UI.menu(menu_options(), header=header)(self)

    def main_menu(self):
        """Main menu for the type casting utility."""
        def finish():
            """Sets the flag to True"""
            nonlocal finished
            finished = True

        def menu_options():
            """Build a list of options, adding an option if condition is met"""
            # Options are described with tuples:
            # (function, description, condition)
            diecase = bool(self.diecase)
            ribbon = bool(self.ribbon)
            diecase_info = ' (current: %s)' % self.diecase if diecase else ''
            opts = [(finish, 'Exit', 'Exits the program', True),
                    (self.cast_composition, 'Cast composition',
                     'Cast type from a selected ribbon', ribbon and casting),
                    (self.cast_composition, 'Punch ribbon',
                     'Punch a paper ribbon for casting without the interface',
                     ribbon and punching),
                    (self.choose_ribbon, 'Select ribbon',
                     'Select a ribbon from database or file', True),
                    (self.choose_diecase, 'Select diecase',
                     'Select a matrix case from database' + diecase_info,
                     casting),
                    (self.display_ribbon_contents, 'View codes',
                     'Display all codes in the selected ribbon', ribbon),
                    (self.display_diecase_layout, 'Show diecase layout',
                     'View the matrix case layout', diecase and casting),
                    (self.quick_typesetting, 'Quick typesetting',
                     'Compose and cast a line of text', diecase and casting),
                    (self.cast_sorts, 'Cast sorts for given characters',
                     'Cast from matrix based on a character',
                     casting and diecase),
                    (self.cast_sorts, 'Cast sorts from matrix coordinates',
                     'Cast from matrix at given position',
                     casting and not diecase),
                    (self.cast_spaces, 'Cast spaces',
                     'Cast spaces or quads of a specified width', casting),
                    (self.cast_typecases, 'Cast typecases',
                     'Cast a typecase based on a selected language',
                     casting and diecase),
                    (self._display_details, 'Show details...',
                     'Display ribbon, diecase, wedge and interface info',
                     casting),
                    (self._display_details, 'Show details...',
                     'Display ribbon and interface details', punching),
                    (self.diecase_manipulation, 'Matrix manipulation...',
                     'Work on matrix cases', True),
                    (self.diecase_proof, 'Diecase proof',
                     'Cast every character from the diecase', True),
                    (self.diagnostics_submenu, 'Service...',
                     'Interface and machine diagnostic functions', True)]
            # Built a list of menu options conditionally
            return [(function, description, long_description)
                    for (function, description, long_description, condition)
                    in opts if condition]

        # Keep displaying the menu and go back here after any method ends
        finished = False
        while not finished:
            punching = self.caster.mode.punching
            casting = not punching
            job = 'Casting' if casting else 'Punching'
            header = ('rpi2caster - CAT (Computer-Aided Typecasting) '
                      'for Monotype Composition or Type and Rule casters.\n\n'
                      'This program reads a ribbon (from file or database) '
                      'and casts the type on a composition caster.'
                      '\n\n%s Menu:' % job)
            # Catch any known exceptions here
            with suppress(e.ReturnToMenu, e.MenuLevelUp, Abort,
                          EOFError, KeyboardInterrupt):
                UI.menu(menu_options(), header=header, footer='')()

    def _display_details(self):
        """Collect ribbon, diecase and wedge data here"""
        display = UI.display_parameters
        punching = self.caster.mode.punching
        if self.ribbon:
            display({'Ribbon data': self.ribbon.parameters})
        if self.diecase and not punching:
            display({'Matrix case data': self.diecase.parameters})
        if self.wedge and not punching:
            display({'Wedge data': self.wedge.parameters})
        display({'Caster data': self.caster.parameters})
        UI.pause()
