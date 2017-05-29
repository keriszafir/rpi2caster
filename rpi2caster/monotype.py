# -*- coding: utf-8 -*-
"""Caster object for either real or virtual Monotype composition caster"""
# Standard library imports
import time
from collections import OrderedDict

# Intra-package imports
from .rpi2caster import UI, option, Abort
from .casting_models import Record
from .definitions import ROW16_ADDRESSING, SIGNALS
from .matrix_controller import MatrixEngine

# Constants for readability
AIR_ON = True
AIR_OFF = False


class MonotypeCaster(object):
    """Methods common for Caster classes, used for instantiating
    caster driver objects (whether real hardware or mockup for simulation)."""
    working, pump_working = False, False
    sensor, output = None, None
    # caster modes
    row_16_mode = ROW16_ADDRESSING.off

    def __init__(self, runtime_config):
        """Lock the resource so that only one object can use it
        with context manager"""
        self.runtime_config = runtime_config
        interface = runtime_config.interface
        self.sensor = interface.sensor()
        self.output = interface.output()

    def __enter__(self):
        # initialize hardware interface; check if machine is running
        self.output.__enter__()
        self.sensor.__enter__()
        if not self.working:
            self.sensor.check_if_machine_is_working()
            self.working = True
        return self

    def __exit__(self, *_):
        self.output.__exit__()
        self.sensor.__exit__()

    @property
    def parameters(self):
        """Gets a list of parameters"""
        # Collect data from I/O drivers
        parameters = OrderedDict({'': 'Caster parameters'})
        parameters.update(**self.sensor.parameters)
        parameters.update(**self.output.parameters)
        return parameters

    def check_row_16(self, is_required=False):
        """Choose the diecase row 16 addressing mode, if needed.

        Row 16 is needed and currently off:
        Ask which row 16 addressing system the user's machine has, if any.

        Row 16 is not needed and currently on:
        Tell the user to turn off the attachment.

        Row 16 is not needed and is off, or is needed and is on: do nothing.
        """
        is_active = self.row_16_mode is not ROW16_ADDRESSING.off

        # check and notify the user
        if is_required and not is_active:
            self.choose_row16_addressing()
        elif is_active and not is_required:
            UI.pause('\n\nTurn off the {} attachment.\n\n'
                     .format(self.row_16_mode))
            self.row_16_mode = ROW16_ADDRESSING.off
        elif is_required and is_active:
            UI.display('The {} attachment is turned on - OK.'
                       .format(self.row_16_mode))

    def choose_row16_addressing(self):
        """Let user decide which way to address row 16"""
        prompt = ('Your ribbon contains codes from the 16th row.\n'
                  'It is supported by special attachments for the machine.\n'
                  'Which mode does your caster use: HMN, KMN, Unit-Shift?\n\n'
                  'If off - characters from row 15 will be cast instead.')
        options = [option(key='h', value=ROW16_ADDRESSING.hmn,
                          seq=1, text=ROW16_ADDRESSING.hmn),
                   option(key='k', value=ROW16_ADDRESSING.kmn,
                          seq=2, text=ROW16_ADDRESSING.kmn),
                   option(key='u', value=ROW16_ADDRESSING.unitshift,
                          seq=3, text=ROW16_ADDRESSING.unitshift),
                   option(key='o', value=ROW16_ADDRESSING.off, seq=4,
                          text='Off - cast from row 15 instead')]
        mode = UI.simple_menu(prompt, options,
                              default_key='o', allow_abort=True)
        self.row_16_mode = mode

    def update_pump_state(self, record):
        """Read the record data and check if the pump is working"""
        state = (False if record.code.is_pump_stop
                 else self.pump_working or record.code.is_pump_start)
        self.pump_working = state

    def pump_off(self):
        """Ensure that the pump is turned off"""
        record = Record('NJS0005')
        while self.pump_working:
            UI.display('Stopping the pump: sending NJS 0005 twice')
            self.cast_one(record, timeout=60)
            self.cast_one(record, timeout=60)
            self.pump_working = False

    def cast_one(self, record, timeout=None):
        """Casting sequence: sensor on - valves on - sensor off - valves off"""
        stop1 = 'EMERGENCY STOP: Cleaning up and switching the pump off...'
        stop2 = 'If the machine is stopped, turn it by hand once or twice.'
        try:
            self.update_pump_state(record)
            self.output.valves_off()
            self.sensor.wait_for(AIR_ON, timeout=timeout)
            self.output.valves_on(record.adjusted_signals)
            self.sensor.wait_for(AIR_OFF, timeout=timeout)
            self.output.valves_off()
        except (KeyboardInterrupt, EOFError, MachineStopped):
            UI.display(stop1, stop2)
            self.pump_off()
            self.working = False
            raise MachineStopped

    def cast_many(self, sequence, ask=True, repetitions=1):
        """Cast a series of multiple records.
        This is a simplified routine for internal use;
        normally use Casting.cast_ribbon which provides more info"""
        stop_prompt = 'Machine stopped: continue casting?'
        # do we need to cast from row 16 and choose an attachment?
        r16_needed = any((record.code.uses_row_16 for record in sequence))
        self.check_row_16(r16_needed)
        # use caster context to check machine rotation and ensure
        # that no valves stay open after we're done
        with self:
            # cast as many as initially ordered and ask to continue
            while repetitions > 0:
                try:
                    for record in sequence:
                        UI.display(record)
                        self.cast_one(record)
                    # ensure that the pump is not working
                    self.pump_off()
                    # repetition successful
                    repetitions -= 1
                except MachineStopped:
                    # repetition failed
                    UI.confirm(stop_prompt, abort_answer=False)
                if ask and not repetitions and UI.confirm('Repeat?'):
                    repetitions += 1
        # reset the machine working flag
        # so sensor.check_if_machine_is_working() will run again when needed
        self.working = False

    def punch(self, signals_sequence):
        """Punching sequence: valves on - wait - valves off- wait"""
        def manual(signals):
            """Advance between combinations is controlled by keypress"""
            self.output.valves_off()
            self.output.valves_on(signals)
            UI.pause('Next combination?', allow_abort=True)

        def by_timer(signals):
            """Advance is dictated by timer"""
            self.output.valves_off()
            self.output.valves_on(signals)
            time.sleep(0.25)
            self.output.valves_off()
            time.sleep(0.4)

        info = '{r.adjusted_signals_string:<20}{r.comment}'
        punch_one = manual if UI.confirm('Manual advance?') else by_timer
        # do we need to use any row16 addressing attachment?
        r16_needed = any((record.code.uses_row_16
                          for record in signals_sequence))
        self.check_row_16(r16_needed)
        # we only need output for this action
        with self.output:
            for item in signals_sequence:
                record = Record(item, signal_o15=True, default_o15=True)
                UI.display(info.format(r=record))
                punch_one(record.adjusted_signals)

    def test(self, signals_sequence, duration=None):
        """Testing: advance manually"""
        # we only need output for this action
        with self.output:
            while True:
                for item in signals_sequence:
                    record = Record(item, signal_o15=True)
                    UI.display(record.signals_string)
                    self.output.valves_off()
                    self.output.valves_on(record.signals)
                    if duration:
                        time.sleep(duration)
                    else:
                        UI.pause('Next?', allow_abort=True)
                UI.confirm('Repeat?', abort_answer=False)

    def diagnostics(self):
        """Settings and alignment menu for servicing the caster"""
        def test_front_pinblock(*_):
            """Sends signals 1...14, one by one"""
            info = 'Testing the front pinblock - signals 1...14.'
            UI.pause(info, allow_abort=True)
            self.test([str(n) for n in range(1, 15)])

        def test_rear_pinblock(*_):
            """Sends NI, NL, A...N"""
            info = 'This will test the rear pinblock - NI, NL, A...N. '
            UI.pause(info, allow_abort=True)
            self.test(['NI', 'NL', *'ABCDEFGHIJKLMN'])

        def test_all(*_):
            """Tests all valves and composition caster's inputs in original
            Monotype order:
            NMLKJIHGFSED 0075 CBA 123456789 10 11 12 13 14 0005.
            """
            info = ('This will test all the air lines in the same order '
                    'as the holes on the paper tower: \n{}\n'
                    'MAKE SURE THE PUMP IS DISENGAGED.')
            UI.pause(info.format(' '.join(SIGNALS)), allow_abort=True)
            self.test(SIGNALS)

        def test_justification(*_):
            """Tests the 0075-S-0005"""
            info = 'This will test the justification pinblock: 0075, S, 0005.'
            UI.pause(info, allow_abort=True)
            self.test(['0075', 'S', '0005'])

        def test_any_code(*_):
            """Tests a user-specified combination of signals"""
            with self.output:
                while True:
                    UI.display('Enter the signals to send to the caster, '
                               'or leave empty to return to menu: ')
                    string = UI.enter('Signals?', default=Abort)
                    record = Record(string, signal_o15=True)
                    self.output.valves_off()
                    UI.display('Sending {}'.format(record.signals_string))
                    self.output.valves_on(record.signals)

        def blow_all(*_):
            """Blow all signals for a short time; add NI, NL also"""
            info = 'Blowing air through all air pins on both pinblocks...'
            UI.pause(info, allow_abort=True)
            queue = ['NI', 'NL', 'A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7',
                     'H8', 'I9', 'J10', 'K11', 'L12', 'M13', 'N14',
                     '0075 S', '0005 O15']
            self.test(queue, duration=0.3)

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
            with self.output:
                self.output.valves_on(['G', '8'])
                UI.pause('Sending G8, waiting for you to stop...')
                self.output.valves_off()

        def calibrate_wedges(*_):
            """Allows to calibrate the justification wedges so that when you're
            casting a 9-unit character with the S-needle at 0075:3 and 0005:8
            (neutral position), the    width is the same.

            It works like this:
            1. 0075 - turn the pump on,
            2. cast 7 spaces from the specified matrix (default: G5),
            3. put the line to the galley & set 0005 to 8, 0075 to 3, pump on,
            4. cast 7 spaces with the S-needle from the same matrix,
            5. put the line to the galley, then 0005 to turn the pump off.
            """
            UI.display('Transfer wedge calibration:\n\n'
                       'This function will cast two lines of 5 spaces: '
                       'first: G5, second: GS5 with wedges at 3/8. \n'
                       'Adjust the 52D space transfer wedge '
                       'until the lengths are the same.\n')
            UI.confirm('Proceed?', default=True, abort_answer=False)
            # prepare casting sequence
            record, justified_record = Record('G7'), Record('GS7')
            pump_start, pump_stop = Record('NKS 0075 3'), Record('NJS 0005 8')
            line_out = Record('NKJS 0005 0075 8')
            # start - 7 x G5 - line out - start - 7 x GS5 - line out - stop
            sequence = [pump_start, *[record] * 7, line_out, pump_start,
                        *[justified_record] * 7, line_out, pump_stop]
            self.cast_many(sequence)

        def calibrate_mould_and_diecase(*_):
            """Casts the "en dash" characters for calibrating the character X-Y
            relative to type body."""
            def get_codes(mat):
                """Gets two mats for a given char and adjusts its parameters"""
                positions = mat_engine.get_wedge_positions(mat)
                pos_0075, pos_0005 = positions.pos_0075, positions.pos_0005
                use_s_needle = (pos_0075, pos_0005) != (3, 8)
                codes = mat.get_ribbon_record(s_needle=use_s_needle)
                record = Record(codes)
                sjust = [Record('NJS 0005 {}'.format(pos_0005)),
                         Record('NKS 0075 {}'.format(pos_0075))]
                # use single justification to adjust character width, if needed
                return ([*sjust, record, record] if use_s_needle
                        else [record, record])

            UI.display('Mould blade opening and X-Y character calibration:\n'
                       'Cast G5, adjust the sort width to the value shown.\n'
                       '\nThen cast some lowercase "n" letters and n-dashes,\n'
                       'check the position of the character relative to the\n'
                       'type body and adjust the bridge X-Y.\n'
                       'Repeat if needed.\n')
            UI.confirm('Proceed?', default=True, abort_answer=False)

            # this method needs to know the diecase and wedge
            mat_engine = MatrixEngine()
            wedge = mat_engine.choose_wedge()
            # use half-quad, quad, "n" and en-dash
            mats = [mat_engine.find_space(units=9),
                    mat_engine.find_space(units=18),
                    mat_engine.find_matrix(char='n'),
                    mat_engine.find_matrix(char='--')]
            # operator needs to know how wide (in inches) the sorts should be
            template = '{u} units (1{n}) is {i}" wide'
            quad_width = mat_engine.wedge.set_width / 12 * wedge.pica
            UI.display(template.format(u=9, n='en', i=0.5 * quad_width))
            UI.display(template.format(u=18, n='em', i=quad_width))
            # build a casting queue and cast it repeatedly
            line_out, pump_stop = Record('NKJS 0005 0075'), Record('NJS 0005')
            codes = (code for mat in mats for code in get_codes(mat))
            sequence = [*codes, line_out, pump_stop]
            self.cast_many(sequence)

        def test_row_16(*_):
            """Tests the row 16 addressing attachment (HMN, KMN, unit-shift).
            Casts from all matrices in 16th row.
            """
            UI.display('This will test the 16th row addressing.\n'
                       'If your caster has HMN, KMN or unit-shift attachment, '
                       'turn it on.\n')
            # build casting queue
            pump_start, pump_stop = Record('NKS 0075'), Record('NJS 0005')
            line_out = Record('NKJS 0005 0075')
            row = [Record('{}16'.format(col))
                   for col in ('NI', 'NL', *'ABCDEFGHIJKLMNO')]
            # test with actual casting or not?
            if UI.confirm('Use the pump? Y = cast the row, N = test codes.'):
                sequence = [pump_start, *row, line_out, pump_stop]
                self.cast_many(sequence)
            else:
                self.test(row)

        is_a_caster = not self.runtime_config.punching
        options = [option(key='a', value=test_all, seq=1,
                          text='Test outputs',
                          desc='Test all the air outputs N...O15, one by one'),
                   option(key='f', value=test_front_pinblock, seq=2,
                          cond=is_a_caster,
                          text='Test the front pin block',
                          desc='Test the pins 1...14'),
                   option(key='r', value=test_rear_pinblock, seq=2,
                          cond=is_a_caster,
                          text='Test the rear pin block',
                          desc='Test the pins NI, NL, A...N, one by one'),
                   option(key='b', value=blow_all, seq=2,
                          text='Blow all air pins',
                          desc='Blow air into every pin for a short time'),
                   option(key='j', value=test_justification, seq=2,
                          cond=is_a_caster,
                          text='Test the justification block',
                          desc='Test the pins for 0075, S and 0005'),
                   option(key='c', value=test_any_code, seq=1,
                          text='Send specified signal combination',
                          desc='Send the specified signals to the machine'),
                   option(key='w', value=calibrate_wedges, seq=4,
                          cond=is_a_caster,
                          text='Calibrate the 52D wedge',
                          desc=('Calibrate the space transfer wedge '
                                'for correct width')),
                   option(key='d', value=calibrate_mould_and_diecase, seq=4,
                          cond=is_a_caster,
                          text='Calibrate mould blade and diecase',
                          desc=('Set the type body width and '
                                'character-to-body position')),
                   option(key='m', value=calibrate_draw_rods, seq=3,
                          cond=is_a_caster,
                          text='Calibrate matrix case draw rods',
                          desc=('Keep the matrix case at G8 '
                                'and adjust the draw rods')),
                   option(key='l', value=test_row_16, seq=5,
                          cond=is_a_caster,
                          text='Test large 16x17 diecase attachment',
                          desc=('Cast type from row 16 '
                                'with HMN, KMN or unit-shift'))]

        header = 'Diagnostics and machine calibration menu:'
        catch_exceptions = (Abort, KeyboardInterrupt, EOFError, MachineStopped)
        # Keep displaying the menu and go back here after any method ends
        UI.dynamic_menu(options=options, header=header, func_args=(self,),
                        catch_exceptions=catch_exceptions)


class MachineStopped(Exception):
    """Machine stopped exception"""
    def __str__(self):
        return ''
