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
from time import sleep
from functools import wraps
from . import basic_models as bm, basic_controllers as bc, definitions as d
from .casting_model import Stats, Record
from . import monotype, parsing as p, typesetting_funcs as tsf
from .typesetting import TypesettingContext, GalleyBuilder
from .ui import UI, Abort, Finish, option


def cast_this(ribbon_source):
    """Get the ribbon from decorated routine and cast it"""
    @wraps(ribbon_source)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        ribbon = ribbon_source(self, *args, **kwargs)
        return self.cast_ribbon(ribbon) if ribbon else None
    return wrapper


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
        self.caster = monotype.MonotypeCaster()

    @monotype.caster_context
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
            if machine.punching or machine.testing:
                # no need to rewind
                return
            if p.stop_comes_first(ribbon):
                ribbon = [x for x in reversed(ribbon)]

        def skip_lines():
            """Skip a definite number of lines"""
            nonlocal queue
            # Apply constraints: 0 <= lines_skipped < lines in ribbon
            lines_skipped = stats.get_run_lines_skipped()
            if lines_skipped:
                UI.display('Skipping {} lines'.format(lines_skipped))
            # Take away combinations until we skip the desired number of lines
            # BEWARE: ribbon starts with galley trip!
            # We must give it back after lines are taken away
            code = ''
            queue = deque(ribbon)
            while lines_skipped > 0:
                record = Record(queue.popleft())
                lines_skipped -= 1 * record.code.is_newline
            # give the last code back
            queue.appendleft(code)

        def set_lines_skipped():
            """Set the number of lines skipped for run and session
            (in case of multi-session runs)."""
            stats.set_session_lines_skipped(0)
            stats.set_run_lines_skipped(0)
            # offer this for casting only...
            if not machine.casting:
                return

            # if ribbon is more than 2 lines long...
            limit = max(0, stats.get_ribbon_lines() - 2)
            if limit < 1:
                return
            # how many can we skip?
            UI.display('We can skip up to {} lines.'.format(limit))

            # run lines skipping
            # how many lines were successfully cast?
            lines_ok = stats.get_lines_done()
            if lines_ok:
                UI.display('{} lines were cast in the last run.'
                           .format(lines_ok))
            # Ask user how many to skip (default: all successfully cast)
            run_skip = UI.enter('How many lines to skip for THIS run?',
                                default=lines_ok, minimum=0, maximum=limit)
            stats.set_run_lines_skipped(run_skip)

            # session line skipping affects multi-run sessions only
            # don't do it for single-run sessions
            if stats.runs < 2:
                return

            # Skip lines effective for ALL runs
            session_skip = UI.enter('How many lines to skip for ALL runs?',
                                    default=0, minimum=0, maximum=limit)
            stats.set_session_lines_skipped(session_skip)

        def preheat_if_needed():
            """Things to do only once during the whole casting session"""
            # Use this only in casting or calibration, otherwise don't ask
            nonlocal stats
            proper_mode = machine.casting or machine.calibration
            if not proper_mode:
                return
            prompt = 'Cast two lines of quads to heat up the mould?'
            if not UI.confirm(prompt, default=False):
                return
            quad = self.quad
            quad_qty = int(self.measure.units // quad.units)
            text = 'Casting quads for mould heatup'
            quad_signals = ('{code} // {comment} preheat'
                            .format(code=quad.code, comment=quad.comment))
            heatup = ([quad_signals] * quad_qty +
                      tsf.double_justification(comment=text)) * 2
            try:
                # Use different stats for preheat quads
                old_stats, stats = stats, Stats(machine)
                machine.sensor.check_if_machine_is_working()
                cast_queue(reversed(heatup))
            finally:
                stats = old_stats

        def cast_queue(sequence=None):
            """Casts the sequence of codes in given sequence.
            This function is executed until the sequence is exhausted
            or casting is stopped by machine or user."""
            # in punching mode, lack of row will trigger signal 15,
            # lack of column will trigger signal O
            # in punching and testing mode, signal O or 15 will be present
            # in the output combination as O15
            for item in sequence or queue:
                record = Record(item,
                                row_16_mode=machine.row_16_mode,
                                default_o15=machine.punching,
                                signal_o15=machine.punching or machine.testing)
                # check if signal will be cast at all
                if not record.code.has_signals:
                    UI.display_header(record.comment)
                    continue
                # display some info
                stats.process_record(record)
                UI.display_parameters(stats.code_parameters)
                # cast / punch it!
                try:
                    machine.process(record.adjusted_signals)

                except (monotype.MachineStopped, KeyboardInterrupt, EOFError):
                    # stop the pump in case it's working
                    # (do nothing in punching mode)
                    # keep doing it until the pump is effectively off
                    pump_stop()
                    # offer resume only in punching mode, not for testing
                    if not machine.punching or machine.testing:
                        return False
                    if not UI.confirm('Resume punching?', default=True):
                        return False
                    # re-punch the same signals
                    machine.process(record.adjusted_signals)
            # all queue successfully processed
            return True

        def pump_stop():
            """Forces pump stop - won't end until it is turned off"""
            # applicable only to casting mode
            if machine.punching:
                return

            pr1 = 'EMERGENCY STOP: Cleaning up and switching the pump off...'
            pr2 = 'If the machine is stopped, turn it by hand once or twice.'
            UI.display(pr1)
            UI.display(pr2)
            # turn off any valves that may still be on
            machine.output.valves_off()

            while machine.pump_working:
                with suppress(monotype.MachineStopped,
                              KeyboardInterrupt, EOFError):
                    # Run two full sequences to be sure
                    machine.process(['N', 'J', 'S', '0005'])
                    machine.process(['N', 'J', 'S', '0005'])
                    UI.display('Pump is now off.')
                    machine.pump_working = False

        def finish_successful_run():
            """Add more runs to the casting session"""
            if stats.get_remaining_runs():
                # still more to do...
                return
            # offer to add some more runs
            if machine.casting:
                prompt = 'Casting finished; add more runs - how many?'
                stats.runs += UI.enter(prompt, default=0, minimum=0)
            elif UI.confirm('Repeat?', default=True):
                stats.runs += 1

        def finish_failed_run():
            """Reset last run stats and ask whether to retry the last run."""
            runs_left = stats.get_remaining_runs()
            stats.reset_last_run_stats()

            if runs_left:
                prm = '{} runs remaining, continue casting?'.format(runs_left)
                UI.confirm(prm, default=True, abort_answer=False)

            if machine.casting or machine.calibration:
                if not UI.confirm('Retry the last run?', default=True):
                    return
                stats.runs += 1
                lines_ok = stats.get_lines_done()
                if lines_ok < 2:
                    return
                if UI.confirm('Skip the {} lines successfully cast?'
                              .format(lines_ok), default=True):
                    stats.set_run_lines_skipped(lines_ok)

        # Helpful aliases
        machine = self.caster
        queue = ribbon
        stats = Stats(machine)
        # Ribbon pre-processing and casting parameters setup
        rewind_if_needed()
        stats.process_ribbon(ribbon)
        UI.display_parameters(stats.ribbon_parameters)
        stats.runs = UI.enter('How many times do you want to cast this?',
                              default=1, minimum=0)
        set_lines_skipped()
        UI.display_parameters(stats.session_parameters)
        # Mould heatup
        preheat_if_needed()
        # Cast until there are no more runs left
        while stats.get_remaining_runs():
            # Prepare the ribbon ad hoc
            skip_lines()
            stats.process_queue(queue)
            # Make sure the machine is turning
            machine.sensor.check_if_machine_is_working()
            # Cast the run and check if it was successful
            casting_success = cast_queue()
            stats.end_run()
            if casting_success:
                finish_successful_run()
            else:
                finish_failed_run()

    @bc.temp_wedge
    def cast_sorts(self):
        """Sorts casting routine, based on the position in diecase.
        Ask user about the diecase row & column, as well as number of sorts.
        """
        order = []
        while True:
            char = UI.enter('Character to look for?',
                            default=False) if self.diecase else ''
            mat = self.find_matrix(char, temporary=True)
            # change its parameters
            matrix = self.edit_matrix(mat, edit_char=False, edit_styles=False)
            qty = UI.enter('How many sorts?', default=10, minimum=0)
            order.append((matrix, qty))
            prompt = 'More sorts? Otherwise, start casting'
            if not UI.confirm(prompt, default=True):
                break
        # Now let's calculate and cast it...
        self.cast_galley(order)

    @bc.temp_wedge
    def cast_typecases(self):
        """Casting typecases according to supplied font scheme."""
        freqs = bc.get_letter_frequencies()
        bc.define_case_ratio(freqs)
        bc.define_scale(freqs)
        style_mgr = bc.choose_styles(self.diecase.styles)
        order = []
        for style in style_mgr:
            UI.display_header(style.name.capitalize())
            if style_mgr.is_single or style_mgr.is_default:
                scale = 1.0
            else:
                scale = UI.enter('Scale for {}?'.format(style.name),
                                 default=100, minimum=1) / 100.0
            for char, chars_qty in freqs.type_bill:
                qty = int(scale * chars_qty)
                UI.display('{}: {}'.format(char, chars_qty))
                matrix = self.find_matrix(char, style, choose=True)
                order.append((matrix, qty))
        self.cast_galley(order)

    @bc.temp_wedge
    def cast_spaces(self):
        """Spaces casting routine, based on the position in diecase.
        Ask user about the space width and measurement unit.
        """
        order = []
        while True:
            matrix = self.get_space(temporary=True)
            self.edit_matrix(matrix, edit_char=False, edit_styles=False)
            prompt = 'How many lines?'
            lines = UI.enter(prompt, default=1, minimum=0)
            order.extend([(matrix, 0)] * lines)
            prompt = 'More spaces? Otherwise, start casting'
            if not UI.confirm(prompt, default=True):
                break
        self.cast_galley(order)

    @cast_this
    @bc.temp_measure
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
            raise Abort
        # 1 quad before and after the line
        quad_padding = 1
        quad = self.get_space(units=18)
        # Leave some slack to adjust the line
        length = (self.measure.ems(self.wedge.set_width) -
                  2 * quad_padding * quad.ems)
        # Build a sequence of matrices for casting
        # If n is 0, we fill the line to the brim
        queues = ([mat] * n if n else [mat] * int((length // mat.ems) - 1)
                  for (mat, n) in order)
        matrix_stream = (mat for batch in queues for mat in batch)
        # Initialize the galley-constructor
        builder = GalleyBuilder(self, matrix_stream)
        builder.quad_padding = quad_padding
        builder.cooldown_spaces = True
        UI.display('Generating a sequence...')
        queue = builder.build_galley()
        UI.display('Each line will have two em-quads at the start '
                   'and at the end, to support the type.')
        return queue

    @cast_this
    def cast_composition(self):
        """Casts or punches the ribbon contents if there are any"""
        if not self.ribbon.contents:
            raise Abort
        return self.ribbon.contents

    @cast_this
    @bc.temp_measure
    @bc.temp_wedge
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
            raise Abort
        self.source = text or ''
        self.edit_text()
        matrix_stream = self.old_parse_input()
        builder = GalleyBuilder(self, matrix_stream)
        queue = builder.build_galley()
        UI.display('Each line will have two em-quads at the start '
                   'and at the end, to support the type.\n'
                   'Starting with two lines of quads to heat up the mould.\n')
        return queue

    @cast_this
    @bc.temp_wedge
    def diecase_proof(self):
        """Tests the whole diecase, casting from each matrix.
        Casts spaces between characters to be sure that the resulting
        type will be of equal width."""
        layouts = (bm.LayoutSize(x, y)
                   for x, y in [(15, 15), (15, 17), (16, 17)])
        options = [option(key=n, value=layout, text=str(layout), seq=n)
                   for n, layout in enumerate(layouts, start=1)]
        layout_size = UI.simple_menu(message='Matrix case size:',
                                     options=options,
                                     default_key=2, allow_abort=True)
        if not UI.confirm('Proceed?', default=True, abort_answer=False):
            return
        # Sequence to cast starts with pump stop and galley trip
        # (will be cast in reversed order)
        queue = tsf.end_casting() + tsf.galley_trip()
        for row in layout_size.row_numbers:
            # Calculate the width for the GS1 space
            wedge_positions = (3, 8)
            queue.append('O15')
            delta = 23 - self.wedge[row] - self.wedge[1]
            if not delta:
                num_gs1, gs1_unit_diff = 0, 0
            elif -2 < delta < 10:
                num_gs1, gs1_unit_diff = 1, delta
            elif delta <= -2 or delta >= 10:
                num_gs1, gs1_unit_diff = 2, delta/2
            if gs1_unit_diff:
                # We have difference in units of a set:
                # translate to inches and make it 0.0005" steps, add 3/8
                gs1_unit_diff *= self.wedge.unit_inch_width
                steps_0005 = int(gs1_unit_diff * 2000) + 53
                # Safety limits: upper = 15/15; lower = 1/1
                steps_0005 = min(steps_0005, 240)
                steps_0005 = max(steps_0005, 16)
                steps_0075 = 0
                while steps_0005 > 15:
                    steps_0005 -= 15
                    steps_0075 += 1
                wedge_positions = (steps_0075, steps_0005)
            for column in layout_size.column_numbers:
                queue.append('{}{}'.format(column, row))
                queue.extend(['GS1'] * num_gs1)
            # Quad out, put the row to the galley, set justification
            queue.append('O15')
            queue.extend(tsf.double_justification(wedge_positions))
        return queue

    def diagnostics_submenu(self):
        """Settings and alignment menu for servicing the caster"""
        @monotype.testing_mode
        @cast_this
        def test_front_pinblock(*_):
            """Sends signals 1...14, one by one"""
            UI.pause('Testing the front pinblock - signals 1...14.')
            return [str(n) for n in range(1, 15)]

        @monotype.testing_mode
        @cast_this
        def test_rear_pinblock(*_):
            """Sends NI, NL, A...N"""
            UI.pause('This will test the rear pinblock - NI, NL, A...N. ')
            return ['NI', 'NL', *'ABCDEFGHIJKLMN']

        @monotype.testing_mode
        @cast_this
        def test_all(*_):
            """Tests all valves and composition caster's inputs in original
            Monotype order:
            NMLKJIHGFSED 0075 CBA 123456789 10 11 12 13 14 0005.
            """
            UI.pause('This will test all the air lines in the same order '
                     'as the holes on the paper tower: \n{}\n'
                     'MAKE SURE THE PUMP IS DISENGAGED.'
                     .format(' '.join(d.SIGNALS)))
            return [x for x in d.SIGNALS]

        @monotype.testing_mode
        @cast_this
        def test_justification(*_):
            """Tests the 0075-S-0005"""
            UI.pause('This will test the justification pinblock: '
                     '0075, S, 0005.')
            return ['0075', 'S', '0005']

        @monotype.testing_mode
        @monotype.caster_context
        def test_any_code(*_):
            """Tests a user-specified combination of signals"""
            while True:
                UI.display('Enter the signals to send to the caster, '
                           'or leave empty to return to menu: ')
                prompt = 'Signals? (leave blank to exit)'
                string = UI.enter(prompt, default=Abort)
                record = Record(string, signal_o15=True)
                self.caster.output.valves_off()
                UI.display('Sending {}'.format(record.signals_string))
                self.caster.output.valves_on(record.signals)

        @monotype.testing_mode
        @monotype.caster_context
        def blow_all(*_):
            """Blow all signals for a short time; add NI, NL also"""
            UI.pause('Blowing air through all air pins on both pinblocks...')
            queue = ['NI', 'NL', 'A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7',
                     'H8', 'I9', 'J10', 'K11', 'L12', 'M13', 'N14', 'O15',
                     '0075', '0005', 'S']
            duration = 0.3
            while True:
                for sig in queue:
                    record = Record(sig, signal_o15=True)
                    sleep(duration)
                    UI.display('Activating {}'.format(record.signals_string))
                    self.caster.output.valves_on(record.signals)
                    sleep(duration)
                    self.caster.output.valves_off()
                if UI.confirm('Repeat?', default=True, abort_answer=False):
                    continue

        @monotype.calibration_mode
        @monotype.caster_context
        def calibrate_draw_rods(*_):
            """Keeps the diecase at G8 so that the operator can adjust
            the diecase draw rods until the diecase stops moving sideways
            when the centering pin is descending."""
            UI.display('Draw rods calibration:\n'
                       'The diecase will be moved to the central position '
                       '(G8).\n Turn on the machine and adjust the diecase '
                       'draw rods until the diecase stops wobbling.\n')
            if not UI.confirm('Proceed?', default=True, abort_answer=False):
                return
            self.caster.output.valves_on(['G', '8'])
            UI.pause('Sending G8, waiting for you to stop...')
            self.caster.output.valves_off()

        @monotype.calibration_mode
        @cast_this
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
                       'until the lengths are the same.\n')
            if not UI.confirm('Proceed?', default=True, abort_answer=False):
                return
            return [*tsf.end_casting(), *['GS5'] * 7,
                    *tsf.double_justification(),
                    *['G5'] * 7, *tsf.double_justification()]

        @monotype.calibration_mode
        @bc.temp_wedge
        @cast_this
        def calibrate_mould_and_diecase(*_):
            """Casts the "en dash" characters for calibrating the character X-Y
            relative to type body."""
            def get_mat(char):
                """Gets a mat for a given char and adjusts its parameters"""
                mat = self.find_matrix(char, choose=True, temporary=True)
                ret = self.edit_matrix(mat, edit_char=False, edit_styles=False)
                return [ret]

            UI.display('Mould blade opening and X-Y character calibration:\n'
                       'Cast G5, adjust the sort width to the value shown.\n'
                       '\nThen cast some lowercase "n" letters and n-dashes, '
                       'check the position of the character relative to the '
                       'type body and adjust the bridge X-Y. '
                       'Repeat if needed.\n')
            template = '{u} units (1{n}) is {i}" wide'
            em_inches = self.wedge.em_inch_width
            UI.display(template.format(u=9, n='en', i=round(em_inches / 2, 4)))
            UI.display(template.format(u=18, n='em', i=round(em_inches, 4)))
            if not UI.confirm('Proceed?', default=True, abort_answer=False):
                return
            # Cast two en-quads, "n" characters and en-dashes
            matrix_stream = [get_mat(char) * 2 for char in ('  ', 'n', '--')]
            builder = GalleyBuilder(self, matrix_stream)
            builder.fill_line = False
            queue = builder.build_galley()
            return queue

        @monotype.calibration_mode
        @cast_this
        def test_row_16(*_):
            """Tests the 16th row with selected addressing mode
            (HMN, KMN, unit-shift). Casts from all matrices in 16th row."""
            UI.display('This will test the 16th row addressing.\n'
                       'If your caster has HMN, KMN or unit-shift attachment, '
                       'turn it on.\n')
            if not UI.confirm('Proceed?', default=True, abort_answer=False):
                return
            mats = ('{}16'.format(x) for x in ('NI', 'NL', *'ABCDEFGHIJKLMNO'))
            return [*tsf.end_casting(), *mats, *tsf.double_justification()]

        def casting_only():
            """Helper function to include casting-only features in menu
            only in casting mode."""
            return not self.caster.punching

        options = [option(key='a', value=test_all, seq=1,
                          text='Test outputs',
                          desc='Test all the air outputs N...O15, one by one'),
                   option(key='f', value=test_front_pinblock, seq=2,
                          cond=casting_only,
                          text='Test the front pin block',
                          desc='Test the pins 1...14'),
                   option(key='r', value=test_rear_pinblock, seq=2,
                          cond=casting_only,
                          text='Test the rear pin block',
                          desc='Test the pins NI, NL, A...N, one by one'),
                   option(key='b', value=blow_all, seq=2,
                          text='Blow all air pins',
                          desc='Blow air into every pin for a short time'),
                   option(key='j', value=test_justification, seq=2,
                          cond=casting_only,
                          text='Test the justification block',
                          desc='Test the pins for 0075, S and 0005'),
                   option(key='c', value=test_any_code, seq=1,
                          text='Send specified signal combination',
                          desc='Send the specified signals to the machine'),
                   option(key='w', value=calibrate_wedges, seq=4,
                          cond=casting_only,
                          text='Calibrate the 52D wedge',
                          desc=('Calibrate the space transfer wedge '
                                'for correct width')),
                   option(key='d', value=calibrate_mould_and_diecase, seq=4,
                          cond=casting_only,
                          text='Calibrate mould blade and diecase',
                          desc=('Set the type body width and '
                                'character-to-body position')),
                   option(key='m', value=calibrate_draw_rods, seq=3,
                          cond=casting_only,
                          text='Calibrate matrix case draw rods',
                          desc=('Keep the matrix case at G8 '
                                'and adjust the draw rods')),
                   option(key='l', value=test_row_16, seq=5,
                          cond=casting_only,
                          text='Test large 16x17 diecase attachment',
                          desc=('Cast type from row 16 '
                                'with HMN, KMN or unit-shift'))]

        header = 'Diagnostics and machine calibration menu:'
        # Keep displaying the menu and go back here after any method ends
        UI.dynamic_menu(options=options, header=header, func_args=(self,),
                        catch_exceptions=(Abort, KeyboardInterrupt, EOFError,
                                          monotype.MachineStopped))

    def main_menu(self):
        """Main menu for the type casting utility."""

        machine, diecase, ribbon = self.caster, self.diecase, self.ribbon
        hdr = ('rpi2caster - CAT (Computer-Aided Typecasting) '
               'for Monotype Composition or Type and Rule casters.\n\n'
               'This program reads a ribbon (from file or database) '
               'and casts the type on a composition caster.'
               '\n\n{} Menu:')
        header = hdr.format('Punching' if machine.punching else 'Casting')

        options = [option(key='c', value=self.cast_composition, seq=10,
                          cond=lambda: (bool(ribbon) and not machine.punching),
                          text='Cast composition',
                          desc='Cast type from a selected ribbon'),

                   option(key='p', value=self.cast_composition, seq=10,
                          cond=lambda: (bool(ribbon) and machine.punching),
                          text='Punch ribbon',
                          desc='Punch a paper ribbon for casting'),

                   option(key='r', value=self.choose_ribbon, seq=30,
                          text='Select ribbon',
                          desc='Select a ribbon from database or file'),

                   option(key='d', value=self.choose_diecase, seq=30,
                          cond=lambda: not machine.punching,
                          text='Select diecase',
                          desc='Select a matrix case from database'),

                   option(key='v', value=self.display_ribbon_contents, seq=80,
                          cond=lambda: bool(ribbon),
                          text='View codes',
                          desc='Display all codes in the selected ribbon'),

                   option(key='l', value=self.display_diecase_layout, seq=80,
                          cond=lambda: (machine.casting and bool(diecase)),
                          text='Show diecase layout{}',
                          desc='View the matrix case layout',
                          lazy=lambda: ('( current diecase ID: {})'
                                        .format(diecase.diecase_id)
                                        if diecase.diecase_id else '')),

                   option(key='t', value=self.quick_typesetting, seq=20,
                          cond=lambda: (machine.casting and bool(diecase)),
                          text='Quick typesetting',
                          desc='Compose and cast a line of text'),

                   option(key='s', value=self.cast_sorts, seq=60,
                          cond=lambda: (machine.casting and bool(diecase)),
                          text='Cast sorts for given characters',
                          desc='Cast from matrix based on a character'),
                   option(key='s', value=self.cast_sorts, seq=60,
                          cond=lambda: (machine.casting and not bool(diecase)),
                          text='Cast sorts from matrix coordinates',
                          desc='Cast from matrix at given position'),

                   option(key='space', value=self.cast_spaces, seq=60,
                          cond=lambda: machine.casting,
                          text='Cast spaces',
                          desc='Cast spaces / quads of a specified width'),

                   option(key='f', value=self.cast_typecases, seq=60,
                          cond=lambda: (machine.casting and bool(diecase)),
                          text='Cast fonts',
                          desc='Cast a typecase based on a selected language'),

                   option(key='F5', value=self._display_details, seq=80,
                          cond=lambda: not machine.punching,
                          text='Show details...',
                          desc='Display ribbon, diecase and wedge info'),
                   option(key='F5', value=self._display_details, seq=80,
                          cond=lambda: machine.punching,
                          text='Show details...',
                          desc='Display ribbon and interface details'),

                   option(key='F7', value=self.diecase_manipulation, seq=90,
                          text='Matrix manipulation...'),

                   option(key='F6', value=self.diecase_proof, seq=85,
                          text='Diecase proof',
                          desc='Cast every character from the diecase'),

                   option(key='F8', value=self.diagnostics_submenu, seq=95,
                          text='Diagnostics menu...',
                          desc='Interface and machine diagnostic functions')]

        UI.dynamic_menu(options, header, default_key='c',
                        abort_suffix='Press [{keys}] to exit.\n',
                        catch_exceptions=(Finish, Abort,
                                          KeyboardInterrupt, EOFError))

    def _display_details(self):
        """Collect ribbon, diecase and wedge data here"""
        ribbon, punching = self.ribbon, self.caster.punching
        diecase, wedge = self.diecase, self.wedge
        data = [ribbon.parameters if ribbon else {},
                diecase.parameters if diecase and not punching else {},
                wedge.parameters if wedge and not punching else {},
                self.caster.parameters]
        UI.display_parameters(*data)
        UI.pause()
