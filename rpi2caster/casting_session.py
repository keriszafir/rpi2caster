# -*- coding: utf-8 -*-
"""
casting_session:

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
from copy import copy
# Signals parsing methods for rpi2caster
from . import parsing as p
# Custom exceptions
from . import exceptions as e
# Constants shared between modules
from . import constants as c
# Typesetting functions module
from . import typesetting_funcs as tsf
# Style manager
from .styles import Styles
# Measure manager
from .measure import Measure
# Caster backend
from .monotype import MonotypeCaster
# Casting stats
from .casting_stats import Stats
# Globally selected UI
from .global_settings import UI
# Typecase casting needs this
from . import letter_frequencies
# Matrix, wedge and typesetting data models
from .typesetting_data import Ribbon
from .matrix_data import Diecase, diecase_operations
from .wedge_data import Wedge


def choose_sensor_and_driver(casting_routine):
    """Checks current modes (simulation, perforation, testing)"""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        mode = self.caster.mode
        UI.debug_pause('About to %s...' %
                       (mode.casting and 'cast composition' or
                        mode.testing and 'test the outputs' or
                        mode.calibration and 'calibrate the machine' or
                        mode.punching and 'punch the ribbon'))
        # Instantiate and enter context
        with mode.sensor() as self.caster.sensor:
            with mode.output() as self.caster.output:
                with self.caster:
                    return casting_routine(self, *args, **kwargs)
    return wrapper


def cast_or_punch_result(ribbon_source):
    """Get the ribbon from decorated routine and cast it"""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        mode = self.caster.mode
        try:
            ribbon = ribbon_source(self, *args, **kwargs)
            if ribbon:
                self.cast_codes(ribbon)
        except e.CastingAborted:
            pass
        finally:
            # Reset diagnostics and row 16 addressing modes
            for mode in (mode.kmn, mode.hmn, mode.unitshift,
                         mode.testing, mode.calibration):
                mode = False
    return wrapper


class Casting(object):
    """Casting:

    Methods related to operating the composition caster.
    Requires configured caster.

    All methods related to operating a composition caster are here:
    -casting composition and sorts, punching composition,
    -calibrating the caster,
    -testing the interface,
    -sending an arbitrary combination of signals,
    -casting spaces to heat up the mould."""

    def __init__(self, ribbon_file='', ribbon_id='', diecase_id='',
                 wedge_name=''):
        # Caster for this job
        self.caster = MonotypeCaster()
        self.stats = Stats(self)
        self.measure = Measure(manual=False)
        self.diecase = Diecase(diecase_id)
        self.ribbon = Ribbon(filename=ribbon_file, ribbon_id=ribbon_id)
        if wedge_name:
            self.diecase.alt_wedge = Wedge(wedge_name)

    @choose_sensor_and_driver
    def cast_codes(self, ribbon):
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
        mode = self.caster.mode
        # Rewind the ribbon if 0005 is found before 0005+0075
        if not (mode.testing or mode.punching) and p.stop_comes_first(ribbon):
            ribbon = [x for x in reversed(ribbon)]
        # New stats for the resulting ribbon
        self.stats.ribbon = ribbon
        UI.display_parameters({'Ribbon info': self.stats.ribbon_parameters})
        # Always 1 run for calibrating and punching
        if mode.diagnostics or mode.punching:
            self.stats.runs = 1
            l_skipped = 0
        else:
            prompt = 'How many times do you want to cast it?'
            self.stats.runs = abs(UI.enter_data_or_default(prompt, 1, int))
            # Line skipping - ask user if they want to skip any initial line(s)
            prompt = 'How many initial lines do you want to skip?'
            l_skipped = (self.stats.get_ribbon_lines() > 2 and
                         abs(UI.enter_data_or_default(prompt, 0, int)) or 0)
        UI.display_parameters({'Session info': self.stats.session_parameters})
        # For each casting run repeat
        while self.stats.get_runs_left():
            queue = deque(ribbon)
            # Apply constraints: 0 <= lines_skipped < lines in ribbon
            l_skipped = min(l_skipped, self.stats.get_ribbon_lines() - 1)
            l_skipped = max(0, l_skipped)
            if l_skipped:
                UI.display('Skipping %s lines' % l_skipped)
            # Take away combinations until we skip the desired number of lines
            # BEWARE: ribbon starts with galley trip!
            # We must give it back after lines are taken away
            code = ''
            while l_skipped + 1 > 0 and not mode.diagnostics:
                code = queue.popleft()
                l_skipped -= 1 * p.check_newline(code)
            queue.appendleft(code)
            # The ribbon is ready for casting / punching
            self.stats.queue = queue
            exit_prompt = '[Y] to start next run or [N] to exit?'
            if self.process_casting_run(queue):
                # Casting successful - ready to cast next run - ask to repeat
                # after the last run is completed (because user may want to
                # cast / punch once more?)
                if (self.stats.all_done() and
                        UI.confirm('One more run?', default=mode.diagnostics)):
                    self.stats.add_one_more_run()
            elif mode.casting and UI.confirm('Retry this run?', default=True):
                # Casting aborted - ask if user wants to repeat
                self.stats.undo_last_run()
                self.stats.add_one_more_run()
                lines_ok = self.stats.get_lines_done()
                prompt = 'Skip %s lines successfully cast?' % lines_ok
                if lines_ok > 0 and UI.confirm(prompt, default=True):
                    l_skipped = lines_ok
                # Start this run again
            elif (not self.stats.all_done() and
                  UI.confirm(exit_prompt, default=True)):
                # There are some more runs to do - go on?
                self.stats.undo_last_run()
            else:
                return

    def process_casting_run(self, casting_queue):
        """Casts the sequence of codes in given sequence"""
        mode = self.caster.mode
        generator = (p.parse_record(record) for record in casting_queue)
        if not mode.testing:
            self.caster.sensor.check_if_machine_is_working()
        while True:
            try:
                signals, comment = next(generator)
                if comment and not signals:
                    UI.display('\n\n' + comment + '\n' + '-' * len(comment))
                    continue
                self.stats.signals = signals
                UI.display_parameters({comment: self.stats.code_parameters})
                # Let the caster do the job
                self.caster.process(signals)
            except StopIteration:
                self.stats.end_run()
                return True
            except (e.MachineStopped, KeyboardInterrupt, EOFError):
                # Allow resume in punching mode
                if (mode.punching and not mode.diagnostics and
                        UI.confirm('Continue?', default=True)):
                    self.caster.process(signals)
                else:
                    self.stats.end_run()
                    return False

    @cast_or_punch_result
    def _test_front_pinblock(self):
        """Sends signals 1...14, one by one"""
        UI.pause('Testing the front pinblock - signals 1 towards 14.')
        self.caster.mode.testing = True
        return [str(n) for n in range(1, 15)]

    @cast_or_punch_result
    def _test_rear_pinblock(self):
        """Sends NI, NL, A...N"""
        UI.pause('This will test the front pinblock - signals NI, NL, A...N. ')
        self.caster.mode.testing = True
        return [x for x in c.COLUMNS_17]

    @cast_or_punch_result
    def _test_all(self):
        """Tests all valves and composition caster's inputs in original
        Monotype order: NMLKJIHGFSED 0075 CBA 123456789 10 11 12 13 14 0005.
        """
        UI.pause('This will test all the air lines in the same order '
                 'as the holes on the paper tower: \n%s\n'
                 'MAKE SURE THE PUMP IS DISENGAGED.' % ' '.join(c.SIGNALS))
        self.caster.mode.testing = True
        return [x for x in c.SIGNALS]

    @cast_or_punch_result
    def _test_justification(self):
        """Tests the 0075-S-0005"""
        UI.pause('This will test the justification pin block (0075, S, 0005).')
        self.caster.mode.testing = True
        return ['0075', 'S', '0005']

    @choose_sensor_and_driver
    def _test_any_code(self):
        """Tests a user-specified combination of signals"""
        self.caster.mode.testing = True
        while True:
            UI.display('Enter the signals to send to the caster, '
                       'or leave empty to return to menu: ')
            prompt = 'Signals? (leave blank to exit)'
            signals = p.parse_signals(UI.enter_data_or_blank(prompt))
            if signals:
                self.caster.output.valves_off()
                UI.display('Activating ' + ' '.join(signals))
                self.caster.output.valves_on(signals)
            else:
                break
        self.caster.mode.testing = False

    @cast_or_punch_result
    def cast_composition(self):
        """Casts or punches the ribbon contents if there are any"""
        if not self.ribbon.contents:
            e.return_to_menu()
        return self.ribbon.contents

    def cast_sorts(self):
        """Sorts casting routine, based on the position in diecase.
        Ask user about the diecase row & column, as well as number of sorts.
        """
        order = []
        while True:
            if self.diecase:
                char = UI.enter_data_or_blank('Character?')
                matrix = self.diecase.lookup_matrix(char)
                prompt = ('Width correction? (%.2f...%.2f points)'
                          % (matrix.get_min_points() - matrix.points,
                             matrix.get_max_points() - matrix.points))
                delta = UI.enter_data_or_default(prompt, 0, float)
                matrix.points += delta
            else:
                matrix = self.diecase.lookup_matrix()
                matrix.specify_units()
            qty = UI.enter_data_or_default('How many sorts?', 10, int)
            order.append((matrix, qty))
            prompt = 'More sorts? Otherwise, start casting'
            if not UI.confirm(prompt, default=True):
                break
        # Now let's calculate and cast it...
        self.cast_galley(order)

    def cast_typecases(self):
        """Casting typecases according to supplied font scheme."""
        enter = UI.enter_data_or_default
        freqs = letter_frequencies.CharFreqs()
        freqs.define_case_ratio()
        freqs.define_scale()
        supported_styles = self.diecase.styles
        UI.display('Styles to cast?')
        # Order specified numbers of sorts from desired matrices
        order = []
        style_manager = Styles(supported_styles)
        style_manager.choose()
        styles = style_manager.keys()
        for style, name in style_manager.items():
            # Display style name
            UI.display_header(name)
            if len(styles) == 1 or style == 'r':
                scale = 1.0
            else:
                scale = enter('Scale for %s?' % name, 100, float) / 100.0
            for char, chars_qty in freqs.type_bill:
                qty = int(scale * chars_qty)
                UI.display('%s: %s' % (char, chars_qty))
                matrix = self.diecase.lookup_matrix(char, style)
                order.append((matrix, qty))
        self.cast_galley(order)

    def cast_spaces(self):
        """Spaces casting routine, based on the position in diecase.
        Ask user about the space width and measurement unit.
        """
        order = []
        if self.diecase:
            master = self.diecase.lookup_matrix(tsf.high_or_low_space())
            UI.display('Casting from %s' % master.code)
        else:
            master = self.diecase.lookup_matrix()
        while True:
            matrix = copy(master)
            UI.display('Enter the space width...')
            UI.display('\nWidth limits for this matrix: %spt min - %spt max\n'
                       % (matrix.get_min_points(), matrix.get_max_points()))
            width = Measure(6, 'pt').points
            matrix.points = width
            prompt = 'How many lines?'
            lines = UI.enter_data_or_default(prompt, 1, int)
            order.extend([(matrix, 0)] * lines)
            prompt = 'More spaces? Otherwise, start casting'
            if not UI.confirm(prompt, default=True):
                break
        self.cast_galley(order)

    @cast_or_punch_result
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
        quad = self.diecase.decode_matrix('O15')
        # Leave some slack to adjust the line
        length = self.measure.points - 2 * quad_padding * quad.points
        # Build a sequence of matrices for casting
        # If n is 0, we fill the line to the brim
        queues = ([mat] * n if n else [mat] * int((length // mat.points) - 1)
                  for (mat, n) in order)
        matrix_stream = (mat for batch in queues for mat in batch)
        # Initialize the galley-constructor
        builder = tsf.GalleyBuilder(matrix_stream, self.diecase, self.measure)
        builder.quad_padding = quad_padding
        builder.cooldown = True
        builder.mould_heatup = UI.confirm('Pre-heat the mould?', True)
        job = self.caster.mode.punching and 'punching' or 'casting'
        UI.display('Generating a sequence for %s...' % job)
        queue = builder.build_galley()
        UI.display('\nReady for %s...\n\n' % job)
        UI.display('Each line will have two em-quads at the start '
                   'and at the end, to support the type.\n'
                   'Starting with two lines of quads to heat up the mould.\n')
        return queue

    @cast_or_punch_result
    def quick_typesetting(self):
        """Allows us to use caster for casting single lines.
        This means that the user enters a text to be cast,
        gives the line length, chooses alignment and diecase.
        Then, the program composes the line, justifies it, translates it
        to Monotype code combinations.

        This allows for quick typesetting of short texts, like names etc.
        """
        supported_styles = self.diecase.styles
        style = Styles(supported_styles, allow_multiple=False,
                       manual_choice=True)()
        text = UI.enter_data('Text to compose?')
        if not self.diecase.test_characters(text, style):
            UI.display('WARNING: Some characters are missing!')
            if not UI.confirm('Continue?', default=False):
                return
        space = self.diecase.decode_matrix('G2')
        matrix_stream = (self.diecase.lookup_matrix(char, style) if char != ' '
                         else space for char in text)
        builder = tsf.GalleyBuilder(matrix_stream, self.diecase, self.measure)
        builder.mould_heatup = False
        queue = builder.build_galley()
        UI.display('Each line will have two em-quads at the start '
                   'and at the end, to support the type.\n'
                   'Starting with two lines of quads to heat up the mould.\n')
        return queue

    @cast_or_punch_result
    def _calibrate_wedges(self):
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
        mat = self.diecase.decode_matrix('G5')
        self.caster.mode.calibration = True
        sequence = tsf.end_casting()
        sequence.extend(['S %s with S-needle' % mat] * 7)
        sequence.extend(['%s' % mat] * 7)
        sequence.extend(tsf.double_justification())
        return sequence

    @cast_or_punch_result
    def _calibrate_mould_and_diecase(self):
        """Casts the "en dash" characters for calibrating the character X-Y
        relative to type body."""
        UI.display('Mould blade opening and X-Y character calibration:\n'
                   'First cast G5, adjust the sort width to the value shown.\n'
                   '\nThen cast some lowercase "n" letters and n-dashes, '
                   'check the position of the character relative to the '
                   'type body and adjust the bridge X-Y. Repeat if needed.')
        wedge = Wedge(manual_choice=True)
        UI.display_parameters({'Wedge data': wedge.parameters})
        UI.display('\n')
        UI.display('9 units (1en) is %s" wide' % round(wedge.em_width / 2, 4))
        UI.display('18 units (1em) is %s" wide\n' % round(wedge.em_width, 4))
        if not UI.confirm('\nProceed?', default=True):
            return None
        # Set temporary alternative wedge for the procedure
        old_wedge, self.diecase.alt_wedge = self.diecase.alt_wedge, wedge
        self.caster.mode.calibration = True
        # Build character list
        queue = tsf.end_casting()
        wedge_positions = (3, 8)
        for char in ('', 'n', '--'):
            if not char:
                mat = self.diecase.decode_matrix('G5')
            else:
                mat = self.diecase.lookup_matrix(char)
            if not self.diecase:
                # Use custom value if no diecase given
                mat.specify_units()
            # Change justification wedge positions if they are different
            # (only if the type was cast with corrections)
            prev_wedge_positions = wedge_positions
            wedge_positions = mat.wedge_positions()
            wedges_change = wedge_positions != prev_wedge_positions
            if prev_wedge_positions != (3, 8) and wedges_change:
                queue.extend(tsf.single_justification(prev_wedge_positions))
            # Add the characters to the queue
            queue.extend(['%s' % mat] * 3)
        # Set the initial wedge positions
        queue.extend(tsf.double_justification(wedge_positions))
        # Reset the wedge
        self.diecase.alt_wedge = old_wedge
        return queue

    @choose_sensor_and_driver
    def _calibrate_draw_rods(self):
        """Keeps the diecase at G8 so that the operator can adjust
        the diecase draw rods until the diecase stops moving sideways
        when the centering pin is descending."""
        UI.display('Draw rods calibration:\n'
                   'The diecase will be moved to the central position (G-8), '
                   'turn on the machine\nand adjust the diecase draw rods '
                   'until the diecase stops moving sideways as the\n'
                   'centering pin is descending into the hole in the matrix.')
        if not UI.confirm('\nProceed?', default=True):
            return None
        self.caster.output.valves_on(['G', '8'])
        UI.pause('Sending G8, waiting for you to stop...')

    @cast_or_punch_result
    def _test_row_16(self):
        """Tests the 16th row with selected addressing mode
        (HMN, KMN, unit-shift). Casts from all matrices in 16th row."""
        UI.display('This will test the 16th row addressing.\n'
                   'If your caster has HMN, KMN or unit-shift attachment, '
                   'turn it on.\n')
        if not UI.confirm('\nProceed?', default=True):
            return None
        self.caster.mode.calibration = True
        queue = tsf.end_casting() + ['%s16' % x for x in c.COLUMNS_17]
        queue.extend(tsf.double_justification(comment='Starting...'))
        return queue

    def diagnostics_submenu(self):
        """Settings and alignment menu for servicing the caster"""
        def finish():
            """Sets the flag to True"""
            nonlocal finished
            finished = True

        def menu_options():
            """Build a list of options, adding an option if condition is met"""
            caster = not self.caster.mode.punching
            opts = [(finish, 'Back', 'Returns to main menu', True),
                    (self._test_all, 'Test outputs',
                     'Test all the air outputs N...O15, one by one', True),
                    (self._test_front_pinblock, 'Test the front pin block',
                     'Test the pins 1...14', caster),
                    (self._test_rear_pinblock, 'Test the rear pin block',
                     'Test the pins NI, NL, A...N, one by one', caster),
                    (self._test_justification, 'Test the justification block',
                     'Test the pins for 0075, S and 0005, one by one', caster),
                    (self._test_any_code, 'Send specified signal combination',
                     'Send the specified signals to the machine', True),
                    (self._calibrate_wedges, 'Calibrate the 52D wedge',
                     'Calibrate the space transfer wedge for correct width',
                     caster),
                    (self._calibrate_mould_and_diecase,
                     'Calibrate mould blade and diecase',
                     'Set the type body width and character-to-body position',
                     caster),
                    (self._calibrate_draw_rods, 'Calibrate diecase draw rods',
                     'Keep the matrix case at G8 and adjust the draw rods',
                     caster),
                    (self._test_row_16, 'Test HMN, KMN or unit-shift',
                     'Cast type from row 16 with chosen addressing mode',
                     caster)]
            return [(function, description, long_description) for
                    (function, description, long_description, condition)
                    in opts if condition]

        header = ('Diagnostics and machine calibration menu:\n\n')
        # Keep displaying the menu and go back here after any method ends
        finished = False
        while not finished:
            try:
                # Catch "return to menu" and "exit program" exceptions here
                UI.menu(menu_options(), header=header)()
            except e.ReturnToMenu:
                # Stay in the menu
                pass

    def main_menu(self):
        """Main menu for the type casting utility."""
        def finish():
            """Sets the flag to True"""
            nonlocal finished
            finished = True

        def choose_ribbon():
            """Chooses a ribbon from database or file"""
            self.ribbon = Ribbon(manual_choice=True)

        def choose_diecase():
            """Chooses a diecase from database"""
            self.diecase = Diecase(manual_choice=True)

        def choose_wedge():
            """Chooses a wedge from registered ones"""
            self.diecase.alt_wedge = Wedge(manual_choice=True)

        def choose_measure():
            """Chooses a galley width"""
            self.measure = Measure()

        def menu_options():
            """Build a list of options, adding an option if condition is met"""
            # Options are described with tuples:
            # (function, description, condition)
            caster = not self.caster.mode.punching
            diecase = bool(self.diecase)
            ribbon = bool(self.ribbon)
            diecase_info = diecase and ' (current: %s)' % diecase or ''
            opts = [(finish, 'Exit', 'Exits the program', True),
                    (self.cast_composition, 'Cast composition',
                     'Cast type from a selected ribbon', ribbon and caster),
                    (self.cast_composition, 'Punch ribbon',
                     'Punch a paper ribbon for casting without the interface',
                     ribbon and not caster),
                    (choose_ribbon, 'Select ribbon',
                     'Select a ribbon from database or file', True),
                    (choose_diecase, 'Select diecase',
                     'Select a matrix case from database' + diecase_info,
                     caster),
                    (choose_wedge, 'Select wedge',
                     'Enter a wedge designation (current: %s)'
                     % self.diecase.alt_wedge, caster),
                    (choose_measure, 'Change galley width',
                     'Set a new galley width for casting type (current: %s)'
                     % self.measure, caster),
                    (self.ribbon.display_contents, 'View codes',
                     'Display all codes in the selected ribbon', ribbon),
                    (self.diecase.show_layout, 'Show diecase layout',
                     'View the matrix case layout', diecase and caster),
                    (self.quick_typesetting, 'Quick typesetting',
                     'Compose and cast a line of text', self.diecase),
                    (self.cast_sorts, 'Cast sorts for given characters',
                     'Cast from matrix based on a character',
                     caster and diecase),
                    (self.cast_sorts, 'Cast sorts from matrix coordinates',
                     'Cast from matrix at given position',
                     caster and not diecase),
                    (self.cast_spaces, 'Cast spaces or quads',
                     'Cast spaces or quads of a specified width', caster),
                    (self.cast_typecases, 'Cast typecases',
                     'Cast a typecase based on a selected language',
                     caster and diecase),
                    (self._display_details, 'Show details...',
                     'Display ribbon, diecase, wedge and interface info',
                     caster),
                    (self._display_details, 'Show details...',
                     'Display ribbon and interface details', not caster),
                    (diecase_operations, 'Matrix manipulation...',
                     'Work on matrix cases', True),
                    (self.diagnostics_submenu, 'Service...',
                     'Interface and machine diagnostic functions', True)]
            # Built a list of menu options conditionally
            return [(function, description, long_description)
                    for (function, description, long_description, condition)
                    in opts if condition]

        header = ('rpi2caster - CAT (Computer-Aided Typecasting) '
                  'for Monotype Composition or Type and Rule casters.\n\n'
                  'This program reads a ribbon (from file or database) '
                  'and casts the type on a composition caster.'
                  '\n\nCasting / Punching Menu:')
        # Keep displaying the menu and go back here after any method ends
        finished = False
        while not finished:
            # Catch any known exceptions here
            try:
                UI.menu(menu_options(), header=header, footer='')()
            except (e.ReturnToMenu, e.MenuLevelUp, KeyboardInterrupt):
                # Will skip to the end of the loop, and start all over
                pass

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
            self.diecase.alt_wedge = Wedge(ribbon.wedge_name)

    def _display_details(self):
        """Collect ribbon, diecase and wedge data here"""
        display = UI.display_parameters
        punching = self.caster.mode.punching
        if self.ribbon:
            display({'Ribbon data': self.ribbon.parameters})
        if self.diecase and not punching:
            display({'Matrix case data': self.diecase.parameters})
        if self.diecase.alt_wedge and not punching:
            display({'Wedge data': self.diecase.alt_wedge.parameters})
        display({'Caster data': self.caster.parameters})
        UI.pause()
