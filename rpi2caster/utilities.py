# -*- coding: utf-8 -*-
"""Casting utility: cast or punch ribbon, cast material for hand typesetting,
make a diecase proof, quickly compose and cast text.
"""

from collections import deque
from contextlib import suppress
from functools import wraps

# QR code generating backend
try:
    import qrcode
except ImportError:
    qrcode = None

from . import basic_models as bm, basic_controllers as bc, definitions as d
from .casting_models import Stats, Record
from . import monotype
from .matrix_controller import get_diecase, temp_diecase, DiecaseMixin
from .typesetting import TypesettingContext
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

        def set_lines_skipped(run=True, session=True):
            """Set the number of lines skipped for run and session
            (in case of multi-session runs)."""
            # allow skipping only if ribbon is more than 2 lines long
            limit = max(0, stats.get_ribbon_lines() - 2)
            if not limit:
                return
            # how many can we skip?
            if run or session:
                UI.display('We can skip up to {} lines.'.format(limit))

            if run:
                # run lines skipping
                # how many lines were successfully cast?
                lines_ok = stats.get_lines_done()
                if lines_ok:
                    UI.display('{} lines were cast in the last run.'
                               .format(lines_ok))
                # Ask user how many to skip (default: all successfully cast)
                r_skip = UI.enter('How many lines to skip for THIS run?',
                                  default=lines_ok, minimum=0, maximum=limit)
                stats.update(run_line_skip=r_skip)

            if session:
                # Skip lines effective for ALL runs
                # session line skipping affects multi-run sessions only
                # don't do it for single-run sessions
                if stats.runs > 1:
                    s_skip = UI.enter('How many lines to skip for ALL runs?',
                                      default=0, minimum=0, maximum=limit)
                    stats.update(session_line_skip=s_skip)

        def preheat_if_needed():
            """Things to do only once during the whole casting session"""
            prompt = 'Cast two lines of quads to heat up the mould?'
            if not UI.confirm(prompt, default=False):
                return []
            quad_qty = int(self.measure.units // self.quad.units)
            text = 'Casting 2 lines of {} quads for mould heatup'
            galley_trip = 'NKJS 0005 0075 // {}'.format(text)
            quad = self.quad.get_ribbon_record()
            # casting queue
            queue = [galley_trip, *[quad] * quad_qty] * 2
            # make a generator object - it needs to be single-use only
            return (x for x in queue)

        def cast_queue(queue):
            """Casts the sequence of codes in given sequence.
            This function is executed until the sequence is exhausted
            or casting is stopped by machine or user."""
            # in punching mode, lack of row will trigger signal 15,
            # lack of column will trigger signal O
            # in punching and testing mode, signal O or 15 will be present
            # in the output combination as O15
            for item in queue:
                UI.clear()
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
        # set the number of casting runs
        stats.update(runs=UI.enter('How many times do you want to cast this?',
                                   default=1, minimum=0))
        # Initial line skipping
        set_lines_skipped(run=True, session=True)
        UI.display_parameters(stats.session_parameters)
        # Mould heatup to stabilize the temperature
        extra_quads = preheat_if_needed()
        # Cast until there are no more runs left
        while stats.get_runs_left():
            # Prepare the ribbon ad hoc
            casting_queue = skip_lines(queue)
            stats.update(queue=casting_queue)
            # Cast the run and check if it was successful
            try:
                # use caster context i.e. check if machine is running first
                with machine:
                    # this part will be cast only once
                    cast_queue(extra_quads)
                    # proper queue with characters
                    cast_queue(casting_queue)
                stats.update(casting_success=True)
                if not stats.get_runs_left():
                    # make sure the machine will check
                    # whether it's running next time
                    machine.working = False
                    # user might want to re-run this
                    prm = 'Casting successfully finished. Any more runs?'
                    stats.update(runs=UI.enter(prm, default=0, minimum=0))

            except monotype.MachineStopped:
                stats.update(casting_success=False)
                # aborted - ask if user wants to continue
                runs_left = stats.get_runs_left()
                if runs_left:
                    UI.confirm('{} runs left, continue?'.format(runs_left),
                               default=True, abort_answer=False)
                else:
                    UI.confirm('Retry casting?', default=True,
                               abort_answer=False)
                # offer to skip lines for re-casting the failed run
                skip_successful = stats.get_lines_done() >= 2
                set_lines_skipped(run=skip_successful, session=False)

    @cast_this
    @temp_diecase
    @bc.temp_wedge
    @bc.temp_measure
    def cast_material(self):
        """Cast typesetting material: typecases, specified sorts, spaces"""
        def matrix_lookup(character=''):
            """finds a matrix in the layout or defines a new one if failed"""
            if self.diecase and character is not None:
                # try to look the mat up by character
                # available if we have a diecase layout
                prompt = 'Character to look for?'
                char = character or UI.enter(prompt, default='')
            else:
                char = ''
            return self.find_matrix(char=char)

        def spaces():
            """generates a sequence of spaces"""
            found = self.diecase.layout.spaces
            options = [option(value=sp, text=str(sp), seq=1) for sp in found]
            options.append(option(key='c', value=None, text='custom', seq=2))
            options.append(option(key='Enter', value=StopIteration, seq=3,
                                  text='done defining spaces'))
            msg = 'Next space?'
            while True:
                # choose from menu or enter coordinates
                space = (UI.simple_menu(msg, options, allow_abort=False) or
                         matrix_lookup(None))
                units = space.get_units_from_row(wedge_used=self.wedge)
                # how wide should it be?
                width = bc.set_measure(input_value=units, unit='u',
                                       what='space width',
                                       set_width=self.wedge.set_width).units
                # how many?
                UI.display('By default cast a line filled with spaces.')
                galley_units = self.measure.units - 2 * self.quad.units
                qty = UI.enter('How many spaces?', int(galley_units // width))
                yield d.QueueItem(space, round(width, 2), qty)

        def typecases():
            """generates a sequence of items for characters in a language"""
            lookup_table = self.diecase.layout.get_lookup_table()
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
                    qty = int(scale * chars_qty)
                    UI.display('{}: {}'.format(char, qty))
                    try:
                        # find a mat
                        matrix = lookup_table[(char, style)]
                    except KeyError:
                        # not found; allow defining it manually
                        UI.display('Matrix lookup failed for {} {}'
                                   .format(style.name, char))
                        matrix = matrix_lookup(char)
                    # at this point we have a matrix
                    mat_units = self.get_units(matrix)
                    units = round(mat_units, 2)
                    yield d.QueueItem(matrix, units, qty)

        def sorts():
            """define sorts (character, width) manually
            or semi-automatically (look them up in the layout)"""
            while True:
                matrix = matrix_lookup()
                char_width = round(self.get_units(matrix))
                units = bc.set_measure(char_width, 'u', what='character width',
                                       set_width=self.wedge.set_width).units
                qty = UI.enter('How many sorts?', default=10, minimum=0)
                # ready to deliver
                yield d.QueueItem(matrix, round(units, 2), qty)

        def choose_source():
            """choose a character generator"""
            options = (option(key='s', value=spaces, text='spaces', seq=1),
                       option(key='c', value=sorts, text='characters', seq=2),
                       option(key='f', value=typecases, cond=self.diecase,
                              text='typecases - based on language', seq=3),
                       option(key='Enter', value=Abort, seq=10, text='done'),
                       option(key='Esc', value=Finish, seq=11,
                              text='abort and go back to menu'))

            UI.display_header('Cast material for hand typesetting')
            UI.display('You can abort any time when defining your order.')
            UI.display('When ready, choose "Finish and start casting".')
            return UI.simple_menu('What to cast?', options, allow_abort=False)

        def make_queue():
            """generate a sequence of items for casting"""
            while True:
                # display menu
                try:
                    source_routine = choose_source()
                    generator = source_routine()
                    for item in generator:
                        yield item
                except (StopIteration, bm.MatrixNotFound):
                    continue
                except Abort:
                    # finish and fill the last line
                    raise StopIteration

        def make_ribbon(queue):
            """Take items from queue and adds them as long as there is
            space left in the galley. When space runs out, end a line.

            queue: [(code, quantity, units, pos_0075, pos_0005)]"""
            def new_mat():
                """matrix, width --> ribbon code, wedge positions"""
                # if the generator yields None first, try again
                queue_item = next(queue) or next(queue)
                sorts_left = queue_item.qty
                matrix, units = queue_item.matrix, queue_item.units
                # some info for the user
                UI.display('{} × {} at {} units'
                           .format(sorts_left, matrix, units))
                # get code and wedge positions for the item
                positions = self.get_wedge_positions(matrix, units)
                record = matrix.get_ribbon_record(s_needle=positions != (3, 8))
                return record, units, positions, sorts_left

            def newline():
                """fill the line with quads, then spaces"""
                nonlocal units_left
                # single justification for the characters
                coarse, fine = wedges
                char_justification = ['NKS 0075 {}'.format(coarse),
                                      'NJS 0005 {}'.format(fine)]

                # add quads (one extra - last quad in the row)
                n_quads = 1 + int(units_left // self.quad.units)
                units_left %= self.quad.units
                # add spaces
                n_spaces = int(units_left // self.space.units)
                units_left %= self.space.units
                # variable space to adjust the width
                mat = self.find_space(units=units_left)
                var_space = mat.get_ribbon_record(s_needle=wedges != (3, 8))
                coarse, fine = self.get_wedge_positions(mat, units_left)
                # double justification sets the initial space width
                if coarse == fine:
                    # single code is enough
                    space_justification = ['NKJS 0005 0075 {}'.format(fine)]
                else:
                    space_justification = ['NKS 0075 {}'.format(coarse),
                                           'NKJS 0005 0075 {}'.format(fine)]

                units_left = self.measure.units - 2 * self.quad.units
                # single justification (for type), fillup spaces & quads,
                # double justification (for space), initial quad on new line
                return [*char_justification,
                        *[space] * n_spaces, var_space, *[quad] * n_quads,
                        *space_justification, quad]

            def changeover():
                """use single-justification (0005+0075) to adjust wedges"""
                # add a quad between different series
                nonlocal units_left
                units_left -= self.quad.units * 2
                coarse, fine = wedges
                quads = [quad, quad]
                # single justification
                sjust = ([] if (coarse, fine) == (3, 8)
                         else ['NKS 0075 {}'.format(fine)] if fine == coarse
                         else ['NKS 0075 {}'.format(coarse),
                               'NJS 0005 {}'.format(fine)])
                return [*quads, *sjust]

            def add_code():
                """add codes to a ribbon, updating the number in the process"""
                nonlocal units_left, sorts_left
                # how many can we fit in the line? (until we've cast all)
                number = int(min(units_left // units, sorts_left))
                # update counters
                sorts_left -= number
                units_left -= number * units
                return [record] * number

            # em-quad and space for filling the line
            quad = self.quad.get_ribbon_record()
            space = self.space.get_ribbon_record()
            # initialize the units
            units_left = self.measure.units - 2 * self.quad.units
            # get the first matrix
            # (if StopIteration is raised, no casting)
            record, units, wedges, sorts_left = new_mat()
            # first to set / last to cast last line out
            yield ['NJS 0005', 'NKJS 0005 0075', quad]
            # keep adding these characters
            while True:
                yield add_code()
                if sorts_left:
                    # still more to go...
                    yield newline()
                else:
                    # we're out of sorts... next character
                    try:
                        yield changeover()
                        record, units, wedges, sorts_left = new_mat()
                    except StopIteration:
                        # no more characters => fill the line and finish
                        # those are the first characters to cast
                        yield newline()
                        break
                    except (bm.TypesettingError, bm.MatrixNotFound) as exc:
                        UI.display('{}, omitting'.format(exc))
                        continue

        source = make_queue()
        ribbon = [code for chunk in make_ribbon(source) for code in chunk]
        if ribbon and UI.confirm('Review ribbon?'):
            self.display_ribbon_contents(ribbon)
        return ribbon

    @cast_this
    @temp_diecase
    @bc.temp_wedge
    def cast_qr_code(self):
        """Set up and cast a QR code which can be printed and then scanned
        with a mobile device."""
        def define_space(low):
            """find and set up a high or low space"""
            try:
                space = self.find_space(units, low=low)
            except bm.MatrixNotFound as exc:
                UI.display(str(exc))
                what = 'Low' if low else 'High'
                code = UI.enter('{} space coordinates?'.format(what), '')
                space = bm.Matrix(code=code, diecase=self.diecase)
            wedges = self.get_wedge_positions(space, units)
            return space.get_ribbon_record(s_needle=wedges != (3, 8)), wedges

        def make_qr(data):
            """make a QR code matrix from data"""
            # QR rendering parameters
            border = UI.enter('QR code border width (squares)?', default=4,
                              minimum=1, maximum=10)
            ec_option = UI.enter('Error correction: 0 = lowest, 3 = highest?',
                                 default=1, minimum=0, maximum=3)
            # set up a QR code and generate a matrix
            modes = (qrcode.constants.ERROR_CORRECT_L,
                     qrcode.constants.ERROR_CORRECT_M,
                     qrcode.constants.ERROR_CORRECT_H,
                     qrcode.constants.ERROR_CORRECT_Q)
            engine = qrcode.QRCode(error_correction=modes[ec_option],
                                   border=border)
            engine.add_data(data)
            qr_matrix = engine.get_matrix()
            return qr_matrix

        def render(pattern):
            """translate a pattern into Monotype control codes,
            applying single justification if space widths differ,
            making spaces square in shape"""
            characters = {False: (low_space, ls_wedges),
                          True: (high_space, hs_wedges)}
            ribbon = ['NJS 0005', 'NKJS 0075 0005']
            for line in pattern:
                pairs = zip(line, [*line[1:], None])
                # newline (border is always low space)
                # double justification with low space wedges
                for current_item, next_item in pairs:
                    # add all spaces in a row
                    space, wedges = characters.get(current_item)
                    try:
                        _, next_wedges = characters.get(next_item)
                    except TypeError:
                        next_wedges = ls_wedges
                    ribbon.append(space)
                    if wedges != (3, 8) and wedges != next_wedges:
                        # set the wedges only if we need to
                        # use single justification in this case
                        ribbon.append('NKS 0075 {}'.format(wedges.pos_0075))
                        ribbon.append('NJS 0005 {}'.format(wedges.pos_0005))
                ribbon.append('NKS 0075 {}'.format(ls_wedges.pos_0075))
                ribbon.append('NKJS 0005 0075 {}'.format(ls_wedges.pos_0005))
            return ribbon

        # set the pixel size; smaler is preferred; depends on mould
        # (allow using different typesetting measures)
        px_size = bc.set_measure('6pt', what='pixel size (the same as mould)',
                                 set_width=self.wedge.set_width)
        units = px_size.units
        # determine the low and high space first
        try:
            low_space, ls_wedges = define_space(True)
            high_space, hs_wedges = define_space(False)
        except bm.TypesettingError as exc:
            UI.display(str(exc))
            UI.pause('Try again with a different wedge')
        # enter text and encode it
        text = UI.enter('Enter data to encode', '')
        qr_matrix = make_qr(text)
        # let the operator know how large the code is
        size = len(qr_matrix)
        prompt = ('The resulting QR code is {0} × {0} squares '
                  'or {1} × {1} inches.')
        UI.display(prompt.format(size, round(size * px_size.inches, 1)))
        UI.pause('Set your galley accordingly or abort.', allow_abort=True)
        # make a sequence of low and high spaces to cast
        return render(qr_matrix)

    @cast_this
    def cast_composition(self):
        """Casts or punches the ribbon contents if there are any"""
        if not self.ribbon.contents:
            raise Abort
        return self.ribbon.contents

    @cast_this
    @temp_diecase
    @bc.temp_wedge
    @bc.temp_measure
    def quick_typesetting(self):
        """Allows us to use caster for casting single lines.
        This means that the user enters a text to be cast,
        gives the line length, chooses alignment and diecase.
        Then, the program composes the line, justifies it, translates it
        to Monotype code combinations.

        This allows for quick typesetting of short texts, like names etc.
        """
        # Safeguard against trying to use this feature from commandline
        # without selecting a diecase
        # TODO: not implemented!
        if not self.diecase:
            raise Abort
        # use manual composition engine
        self.manual_mode = True
        text = self.edit_text()
        ribbon = self.compose(text)
        return ribbon

    @cast_this
    @temp_diecase
    @bc.temp_wedge
    def diecase_proof(self):
        """Tests the whole diecase, casting from each matrix.
        Casts spaces between characters to be sure that the resulting
        type will be of equal width."""
        def get_codes(matrix, wedges):
            """add codes with single justification if necessary"""
            combinations = []
            wedges_needed = wedges != (3, 8)
            code = matrix.get_ribbon_record(s_needle=wedges_needed)
            combinations.append(code)
            if wedges_needed:
                combinations.append('NKS 0075 {}'.format(wedges.pos_0075))
                combinations.append('NJS 0005 {}'.format(wedges.pos_0005))
            return combinations

        def add_matrix(matrix):
            """a matrix and a space"""
            # keep track of spaces too narrow to cast
            nonlocal leftover_units
            mat_units = self.get_units(matrix)
            space_units = 22 + leftover_units - mat_units
            leftover_units = 0
            try:
                mat_wedges = self.get_wedge_positions(matrix, mat_units)
            except bm.TypesettingError:
                # adjust char width as far as possible,
                # take away or add the rest to the space instead
                limits = self.wedge.get_adjustment_limits()
                row_units = matrix.get_units_from_row(wedge_used=self.wedge)
                if mat_units < row_units - limits.shrink:
                    # character too narrow for its row
                    space_units -= (row_units - mat_units - limits.shrink)
                    mat_units = row_units - limits.shrink
                elif mat_units > row_units + limits.stretch:
                    # character too wide for its row
                    space_units += (mat_units - row_units - limits.stretch)
                    mat_units = row_units + limits.stretch
                mat_wedges = self.get_wedge_positions(matrix, mat_units)
            # get these signals
            mat_codes = get_codes(matrix, mat_wedges)
            # omit spaces not wide enough
            if space_units >= 3:
                try:
                    # high spaces are preferred
                    space = self.find_space(space_units, low=False)
                except bm.MatrixNotFound:
                    # then we have to do with a low one...
                    space = self.find_space(space_units, low=True)
                sp_wedges = self.get_wedge_positions(space, space_units)
                space_codes = get_codes(space, sp_wedges)
            else:
                space_codes = []
                leftover_units += space_units
            # characters should be separated by at least one space
            return space_codes + mat_codes

        if self.diecase:
            self.display_diecase_layout()
        else:
            # select size
            sizes = [(15, 15), (15, 17), (16, 17)]
            options = [option(key=n, value=size, text='{} x {}'.format(*size))
                       for n, size in enumerate(sizes, start=1)]
            selected_size = UI.simple_menu(message='Matrix case size:',
                                           options=options,
                                           default_key=2, allow_abort=True)
            self.diecase.layout.resize(*selected_size)

        if not UI.confirm('Proceed?', default=True, abort_answer=False):
            return

        queue = ['NJS 0005', 'NKJS 0075 0005']
        quad = self.quad.get_ribbon_record()
        pos_0075, pos_0005 = 3, 8
        leftover_units = 0
        # build the layout one by one
        for number, row in enumerate(self.diecase.layout.by_rows(), start=1):
            UI.display('Processing row {}'.format(number))
            queue.append(quad)
            for mat in row:
                queue.extend(add_matrix(mat))
            leftover_units = 0
            # single justification for line start
            queue.append(quad)
            queue.append('NKS 0075 {}'.format(pos_0075))
            queue.append('NKJS 0075 0005 {}'.format(pos_0005))

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
                          text='Select diecase',
                          desc='Select a matrix case from database'),

                   option(key='v', value=self.display_ribbon_contents, seq=80,
                          cond=lambda: bool(self.ribbon),
                          text='View codes',
                          desc='Display all codes in the selected ribbon'),

                   option(key='l', value=self.display_diecase_layout, seq=80,
                          cond=lambda: bool(self.diecase),
                          text='Show diecase layout{}',
                          desc='View the matrix case layout',
                          lazy=lambda: ('( current diecase ID: {})'
                                        .format(self.diecase.diecase_id)
                                        if bool(self.diecase) else '')),

                   option(key='t', value=self.quick_typesetting, seq=20,
                          text='Quick typesetting',
                          desc='Compose and cast a line of text'),

                   option(key='h', value=self.cast_material, seq=60,
                          cond=lambda: not machine.punching,
                          text='Cast handsetting material',
                          desc='Cast sorts, spaces and typecases'),

                   option(key='q', value=self.cast_qr_code, seq=70,
                          cond=qrcode, text='Cast QR codes',
                          desc='Cast QR codes from high and low spaces'),

                   option(key='F5', value=self.display_details, seq=85,
                          cond=lambda: not machine.punching,
                          text='Show details...',
                          desc='Display ribbon, diecase and wedge info'),
                   option(key='F5', value=self.display_details, seq=85,
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

        exceptions = (Finish, Abort, KeyboardInterrupt, EOFError)
        UI.dynamic_menu(options, header, default_key='c',
                        abort_suffix='Press [{keys}] to exit.\n',
                        catch_exceptions=exceptions)

    def display_details(self):
        """Collect ribbon, diecase and wedge data here"""
        ribbon, casting = self.ribbon, not self.caster.punching
        diecase, wedge = self.diecase, self.wedge
        data = [ribbon.parameters if ribbon else {},
                diecase.parameters if diecase and casting else {},
                wedge.parameters if wedge and casting else {},
                self.caster.parameters]
        UI.display_parameters(*data)
        UI.pause()


class Typesetting(TypesettingContext):
    """Typesetting session - choose and translate text with control codes
    into a sequence of Monotype control codes, which can be sent to
    the machine to cast composed and justified type.
    """
    def main_menu(self):
        """Main menu for the typesetting utility."""
        header = ('rpi2caster - CAT (Computer-Aided Typecasting) '
                  'for Monotype Composition or Type and Rule casters.\n\n'
                  'Composition Menu:')
        options = [option(key='e', value=self.edit_text, seq=1,
                          text='Edit source text'),
                   option(key='c', value=self.compose, seq=2,
                          text='Compose the text',
                          cond=(self.diecase and self.source and
                                self.manual_mode),
                          desc='User makes end-of-line decisions'),

                   option(key='c', value=self.compose, seq=2,
                          text='Compose the text',
                          cond=(self.diecase and self.source and not
                                self.manual_mode),
                          desc='Automatic typesetting'),

                   option(key='m', value=self.change_measure, seq=5,
                          text='Change measure', lazy=self.measure,
                          desc='Set new line length (current: {})'),

                   option(key='d', value=self.choose_diecase, seq=30,
                          text='Select diecase',
                          desc='Select a matrix case from database'),

                   option(key='w', value=self.choose_wedge, seq=35,
                          text='Select alternative wedge', cond=self.diecase),

                   option(key='a', value=self.change_alignment, seq=40,
                          text='Change default alignment (current: {})',
                          lazy=self.default_alignment),

                   option(key='t', value=self.toggle_manual_mode,
                          text='Switch to automatic typesetting mode',
                          cond=self.manual_mode),

                   option(key='t', value=self.toggle_manual_mode,
                          text='Switch to manual typesetting mode',
                          cond=not self.manual_mode),

                   option(key='v', value=self.display_ribbon_contents, seq=80,
                          cond=lambda: bool(self.ribbon),
                          text='View codes',
                          desc='Display all codes in the selected ribbon'),

                   option(key='l', value=self.display_diecase_layout, seq=80,
                          cond=self.diecase,
                          text='Show diecase layout{}',
                          desc='View the matrix case layout',
                          lazy=lambda: ('( current diecase ID: {})'
                                        .format(self.diecase.diecase_id))),
                   option(key='F7', value=self.diecase_manipulation, seq=90,
                          text='Matrix manipulation...')]

        exceptions = (Finish, Abort, KeyboardInterrupt, EOFError)
        UI.dynamic_menu(options, header, default_key='c',
                        abort_suffix='Press [{keys}] to exit.\n',
                        catch_exceptions=exceptions)


class InventoryManagement(DiecaseMixin):
    """Entry point for editing matrices and matrix cases."""
    def __init__(self, diecase_id=None):
        with suppress(Abort, Finish):
            while True:
                self.diecase = get_diecase(diecase_id)
                with suppress(Abort):
                    self.diecase_manipulation()
                diecase_id = None
