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
from functools import wraps
from . import basic_models as bm, basic_controllers as bc
from .casting_models import Stats, Record
from . import monotype, typesetting_funcs as tsf
from .typesetting import TypesettingContext, GalleyBuilder
from .ui import UI, Abort, Finish, option


def cast_this(ribbon_source):
    """Get the ribbon from decorated routine and cast it"""
    @wraps(ribbon_source)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        ribbon = ribbon_source(self, *args, **kwargs)
        if not ribbon:
            return
        proc = self.punch_ribbon if self.caster.punching else self.cast_ribbon
        return proc(ribbon)
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

    def punch_ribbon(self, ribbon):
        """Punch the ribbon from start to end"""
        self.caster.punch(ribbon)

    def cast_ribbon(self, ribbon):
        """Main casting routine.

        First check if ribbon needs rewinding (when it starts with pump stop).

        Ask user about number of repetitions (useful for e.g. business cards
        or souvenir lines), number of initial lines skipped for all runs
        and the upcoming run only.

        Ask user whether to pre-heat the mould
        to stabilize the temperature and cast good quality type.

        Cast the ribbon single or multiple times, displaying the statistics
        about current record and casting progress.

        If casting multiple runs, repeat until all are done,
        offer adding some more.
        """
        def rewind_if_needed(source):
            """Decide whether to rewind the ribbon or not.
            If casting and stop comes first, rewind. Otherwise not."""
            for item in source:
                code = Record(item).code
                if code.is_pump_stop:
                    return [x for x in reversed(source)]
                elif code.is_pump_start:
                    return [x for x in source]

        def skip_lines(source):
            """Skip a definite number of lines"""
            # Apply constraints: 0 <= lines_skipped < lines in ribbon
            lines_skipped = stats.get_run_lines_skipped()
            if lines_skipped:
                UI.display('Skipping {} lines'.format(lines_skipped))
            # Take away combinations until we skip the desired number of lines
            # BEWARE: ribbon starts with galley trip!
            # We must give it back after lines are taken away
            code = ''
            sequence = deque(source)
            while lines_skipped > 0:
                record = Record(sequence.popleft())
                code = record.original_entry
                lines_skipped -= 1 * record.code.is_newline
            # give the last code back
            sequence.appendleft(code)
            return sequence

        def set_lines_skipped():
            """Set the number of lines skipped for run and session
            (in case of multi-session runs)."""
            stats.update(session_line_skip=0, run_line_skip=0)

            # allow skipping if ribbon is more than 2 lines long
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
            r_skip = UI.enter('How many lines to skip for THIS run?',
                              default=lines_ok, minimum=0, maximum=limit)

            # Skip lines effective for ALL runs
            # session line skipping affects multi-run sessions only
            # don't do it for single-run sessions
            s_skip = 0
            if stats.runs > 1:
                s_skip = UI.enter('How many lines to skip for ALL runs?',
                                  default=0, minimum=0, maximum=limit)
            stats.update(session_line_skip=s_skip, run_line_skip=r_skip)

        def preheat_if_needed():
            """Things to do only once during the whole casting session"""
            prompt = 'Cast two lines of quads to heat up the mould?'
            if not UI.confirm(prompt, default=False):
                return
            quad_mat = self.quad
            quad_qty = int(self.measure.units // quad_mat.units)
            text = 'Casting 2 lines of {} quads for mould heatup'
            double_justification = Record('NKJS 0005 0075 // {}'.format(text))
            quad = Record(str(quad_mat))
            # casting queue
            quadline = [double_justification, *[quad] * quad_qty]
            machine.cast_many(quadline, repetitions=2, ask=False)

        def cast_queue(queue):
            """Casts the sequence of codes in given sequence.
            This function is executed until the sequence is exhausted
            or casting is stopped by machine or user."""
            # in punching mode, lack of row will trigger signal 15,
            # lack of column will trigger signal O
            # in punching and testing mode, signal O or 15 will be present
            # in the output combination as O15
            for item in queue:
                record = Record(item, row_16_mode=machine.row_16_mode)
                # check if signal will be cast at all
                if not record.code.has_signals:
                    UI.display_header(record.comment)
                    continue
                # display some info and cast the signals
                stats.update(record=record)
                UI.display_parameters(stats.code_parameters)
                machine.cast_one(record)

        # Helpful aliases
        machine = self.caster
        stats = Stats(machine)
        # Ribbon pre-processing and casting parameters setup
        queue = rewind_if_needed(ribbon)
        stats.update(ribbon=ribbon)
        UI.display_parameters(stats.ribbon_parameters)
        stats.update(runs=UI.enter('How many times do you want to cast this?',
                                   default=1, minimum=0))
        # Initial line skipping
        set_lines_skipped()
        UI.display_parameters(stats.session_parameters)
        # Mould heatup to stabilize the temperature
        preheat_if_needed()
        # Cast until there are no more runs left
        with machine:
            while stats.get_runs_left():
                # Prepare the ribbon ad hoc
                casting_queue = skip_lines(queue)
                stats.update(queue=casting_queue)
                # Cast the run and check if it was successful
                try:
                    cast_queue(casting_queue)
                    stats.update(casting_success=True)
                    if not stats.get_runs_left():
                        # last run finished - repeat? how many tumes?
                        prm = 'Casting finished; add more runs - how many?'
                        stats.update(runs=UI.enter(prm, default=0, minimum=0))

                except monotype.MachineStopped:
                    # aborted - ask if user wants to continue
                    stats.update(casting_success=False)
                    runs_left = stats.get_runs_left()
                    if runs_left:
                        prm = ('{} runs remaining, continue casting?'
                               .format(runs_left))
                        UI.confirm(prm, default=True, abort_answer=False)

                    # offer to cast it again, if so - skipping successful lines
                    if not UI.confirm('Retry the last run?', default=True):
                        continue
                    stats.update(runs=1)
                    lines_ok = stats.get_lines_done()
                    if lines_ok < 2:
                        continue
                    if UI.confirm('Skip the {} lines successfully cast?'
                                  .format(lines_ok), default=True):
                        stats.update(run_line_skip=lines_ok)

    @cast_this
    @bc.temp_wedge
    @bc.temp_measure
    def cast_material(self):
        """Cast typesetting material: typecases, specified sorts, spaces"""
        def spaces_generator():
            """generates a sequence of spaces"""
            msg = 'Next space?'
            options = (option(key='h', value=False, text='high space', seq=1),
                       option(key='l', value=True, text='low space', seq=2),
                       option(key='Enter', value=StopIteration, seq=3,
                              text='done defining spaces'))
            while True:
                hi_or_low = UI.simple_menu(msg, options, allow_abort=False)
                width = bc.set_measure(input_value='9u', unit='u',
                                       what='space width',
                                       set_width=self.wedge.set_width)
                units = width.units
                matrix = self.find_space(low=hi_or_low, units=units)
                UI.display('By default cast a line filled with spaces.')
                qty = UI.enter('How many spaces?', int(galley_units / units))
                yield matrix, units, qty

        def typecases_generator():
            """generates a sequence of items for characters in a language"""
            lookup_table = self.diecase.layout.lookup_table
            # which styles interest us
            styles = bc.choose_styles(self.diecase.styles)
            # what to cast?
            freqs = bc.get_letter_frequencies()
            bc.define_scale(freqs)
            # a not-so-endless stream of mats...
            for style in styles:
                UI.display_header(style.name.capitalize())
                prompt = 'Scale for {}?'.format(style.name)
                scale = (1.0 if styles.is_single or styles.is_default
                         else UI.enter(prompt, default=100, minimum=1) / 100.0)
                for char, chars_qty in freqs.get_type_bill():
                    scaled_qty = int(scale * chars_qty)
                    UI.display('{}: {}'.format(char, scaled_qty))
                    try:
                        matrix = lookup_table[(char, style)]
                        units = self.get_units(matrix)
                        yield matrix, units, scaled_qty
                    except KeyError:
                        msg = 'Cannot cast {} {} - no matrix found; omitting.'
                        UI.pause(msg)
                        continue

        def sorts_generator():
            """define sorts (character, width) manually
            or semi-automatically (look them up in the layout)"""
            while True:
                if self.diecase:
                    char = UI.enter('Character to look for?', default='')
                    matrix = self.find_matrix(char=char)
                else:
                    position = UI.enter('Coordinates?')
                    matrix = bm.Matrix(pos=position, diecase=self.diecase)
                # got mat, now enter width...
                char_width = self.get_units(matrix)
                units = bc.set_measure(char_width, 'u', what='character width',
                                       set_width=self.wedge.set_width).units
                qty = UI.enter('How many sorts?', default=10, minimum=0)
                # ready to deliver
                yield matrix, units, qty
                # next step?
                if not UI.confirm('More?'):
                    raise StopIteration

        def choose_source():
            """choose a character generator"""
            options = (option(key='s', value=spaces_generator,
                              text='spaces', seq=1),
                       option(key='f', value=typecases_generator,
                              text='fonts (typecases)', seq=2),
                       option(key='t', value=sorts_generator,
                              text='type (sorts)', seq=3),
                       option(key='Enter', value=Abort, seq=10,
                              text='finish and start casting', cond=queue),
                       option(key='Esc', value=Finish, seq=11,
                              text='abort and go back to menu'))
            header = 'What to cast?'
            return UI.simple_menu(header, options, allow_abort=False,
                                  default_key='esc')

        def make_ribbon(queue):
            """Take items from queue and adds them as long as there is
            space left in the galley. When space runs out, end a line.

            queue: [(code, quantity, units, pos_0075, pos_0005)]"""
            def fill_line():
                """fill the line with quads, then spaces"""
                nonlocal units_left
                while units_left >= quad_width:
                    ribbon.append(quad)
                    units_left -= quad_width
                while units_left >= space.units:
                    ribbon.append(space)
                    units_left -= space.units
                ribbon.append(quad)

            # nothing to do? end right away
            if not queue:
                return []
            # initialize the ribbon
            ribbon = [tsf.pump_stop(comment='Finished'),
                      tsf.galley_trip(comment='Putting the last line out')]
            units_left = galley_units
            # keep adding these characters
            for matrix, units, quantity in queue:
                # calculate wedge positions for the item
                var_wedges = self.get_wedge_positions(matrix, units)
                use_s_needle = var_wedges != (3, 8)
                code = matrix.get_ribbon_record(s_needle=use_s_needle)
                # add it as many times as needed
                for _ in range(quantity):
                    if units_left < units:
                        fill_line()
                        # new line and quad
                        ribbon.append(tsf.double_justification(var_wedges))
                        ribbon.append(quad)
                        # reset the line width
                        units_left = galley_units
                    ribbon.append(code)
                    units_left -= units
                # finished added the order; set wedges now
                ribbon.append(tsf.single_justification(var_wedges))
            fill_line()
            ribbon.append(quad)
            ribbon.append(tsf.galley_trip())
            return ribbon

        # em-quad and space for filling the line
        quad, quad_width = self.quad.get_ribbon_record(), self.quad.units
        space = self.find_space(units=5)
        # how wide is the galley? (with an em-quad before and after)
        galley_units = self.measure.units - 2 * quad_width
        queue = []
        while True:
            try:
                source_routine = choose_source()
                generator = source_routine()
                for item in generator:
                    queue.append(item)
            except Abort:
                break

        ribbon = make_ribbon(queue)
        return ribbon

    @cast_this
    def cast_composition(self):
        """Casts or punches the ribbon contents if there are any"""
        if not self.ribbon.contents:
            raise Abort
        return self.ribbon.contents

    @cast_this
    @bc.temp_wedge
    @bc.temp_measure
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
                gs1_unit_diff *= self.wedge.units_to_inches(1)
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

    def main_menu(self):
        """Main menu for the type casting utility."""

        machine = self.caster
        hdr = ('rpi2caster - CAT (Computer-Aided Typecasting) '
               'for Monotype Composition or Type and Rule casters.\n\n'
               'This program reads a ribbon (from file or database) '
               'and casts the type on a composition caster.'
               '\n\n{} Menu:')
        header = hdr.format('Punching' if machine.punching else 'Casting')

        options = [option(key='c', value=self.cast_composition, seq=10,
                          cond=lambda: (not machine.punching and
                                        bool(self.ribbon)),
                          text='Cast composition',
                          desc='Cast type from a selected ribbon'),

                   option(key='p', value=self.cast_composition, seq=10,
                          cond=lambda: (machine.punching and
                                        bool(self.ribbon)),
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
                          cond=lambda: bool(self.ribbon),
                          text='View codes',
                          desc='Display all codes in the selected ribbon'),

                   option(key='l', value=self.display_diecase_layout, seq=80,
                          cond=lambda: (not machine.punching and
                                        bool(self.diecase)),
                          text='Show diecase layout{}',
                          desc='View the matrix case layout',
                          lazy=lambda: ('( current diecase ID: {})'
                                        .format(self.diecase.diecase_id)
                                        if bool(self.diecase) else '')),

                   option(key='t', value=self.quick_typesetting, seq=20,
                          cond=lambda: (not machine.punching and
                                        bool(self.diecase)),
                          text='Quick typesetting',
                          desc='Compose and cast a line of text'),

                   option(key='h', value=self.cast_material, seq=60,
                          cond=lambda: not machine.punching,
                          text='Cast handsetting material',
                          desc='Cast sorts, spaces and typecases'),

                   option(key='F5', value=self._display_details, seq=85,
                          cond=lambda: not machine.punching,
                          text='Show details...',
                          desc='Display ribbon, diecase and wedge info'),
                   option(key='F5', value=self._display_details, seq=85,
                          cond=lambda: machine.punching,
                          text='Show details...',
                          desc='Display ribbon and interface details'),

                   option(key='F7', value=self.diecase_manipulation, seq=90,
                          text='Matrix manipulation...'),

                   option(key='F6', value=self.diecase_proof, seq=85,
                          text='Diecase proof',
                          desc='Cast every character from the diecase'),

                   option(key='F8', value=self.caster.diagnostics, seq=95,
                          text='Diagnostics menu...',
                          desc='Interface and machine diagnostic functions')]

        UI.dynamic_menu(options, header, default_key='c',
                        abort_suffix='Press [{keys}] to exit.\n',
                        catch_exceptions=(Finish, Abort,
                                          KeyboardInterrupt, EOFError))

    def _display_details(self):
        """Collect ribbon, diecase and wedge data here"""
        ribbon, casting = self.ribbon, not self.caster.punching
        diecase, wedge = self.diecase, self.wedge
        data = [ribbon.parameters if ribbon else {},
                diecase.parameters if diecase and casting else {},
                wedge.parameters if wedge and casting else {},
                self.caster.parameters]
        UI.display_parameters(*data)
        UI.pause()
