# -*- coding: utf-8 -*-
"""Caster object for either real or virtual Monotype composition caster"""
# Standard library imports
from collections import OrderedDict
from functools import wraps
from json.decoder import JSONDecodeError
import time

import requests
import librpi2caster
from librpi2caster import ON, OFF, CASTING, PUNCHING, HMN, KMN, UNITSHIFT

# Intra-package imports
from .rpi2caster import UI, Abort, option
from .parsing import parse_record
from .basic_controllers import choose_wedge
from .basic_models import Matrix
from .matrix_controller import get_wedge_positions


def handle_communication_error(routine):
    """If something goes wrong with a connection, ask what to do."""
    @wraps(routine)
    def wrapper(*args, **kwargs):
        """wrapper function"""
        try:
            return routine(*args, **kwargs)
        except librpi2caster.CommunicationError as error:
            message = ('Connection to the interface lost. Check your link.\n'
                       'Original error message:\n{}\n'
                       'Do you want to try again, or abort?')
            if UI.confirm(message.format(error), abort_answer=False):
                return routine(*args, **kwargs)
    return wrapper


class SimulationCaster:
    """Common methods for a caster class."""
    def __init__(self, url=None, operation_mode=None):
        self.url = url
        self.config, self.status = dict(), dict()
        self._setup()
        self.operation_mode = operation_mode

    def _setup(self):
        """Setup a simulation caster"""
        self.config = dict(supported_operation_modes=[CASTING, PUNCHING],
                           supported_row16_modes=[HMN, KMN, UNITSHIFT],
                           default_operation_mode=CASTING,
                           punching_on_time=0.2, punching_off_time=0.3,
                           sensor_timeout=5, pump_stop_timeout=20,
                           startup_timeout=20, name='Simulation interface')
        self.status = dict(water=OFF, air=OFF, motor=OFF, pump=OFF,
                           wedge_0005=15, wedge_0075=15, speed='0rpm',
                           working=OFF, testing_mode=OFF, signals=[],
                           current_operation_mode=CASTING,
                           current_row16_mode=OFF)

    def __str__(self):
        return self.config['name']

    def __call__(self, operation_mode=None, testing_mode=None):
        if operation_mode is not None:
            self.operation_mode = operation_mode
        if testing_mode is not None:
            self.testing_mode = testing_mode
        return self

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()

    def is_casting(self):
        """Determines if this caster is set to casting"""
        return self.operation_mode == CASTING

    @property
    def operation_mode(self):
        """Get the current operation mode:
            None = testing; casting; punching"""
        return self.status['current_operation_mode']

    @operation_mode.setter
    def operation_mode(self, mode):
        """Set the operation mode"""
        if self.status['working']:
            raise librpi2caster.InterfaceBusy
        elif not mode:
            default_operation_mode = self.config['default_operation_mode']
            self.status['current_operation_mode'] = default_operation_mode
        elif mode in self.supported_operation_modes:
            self.status['current_operation_mode'] = mode
        else:
            raise librpi2caster.UnsupportedMode

    @property
    def row16_mode(self):
        """Get the row 16 addressing mode:
            None = off, HMN, KMN, unit shift"""
        return self.status['current_row16_mode']

    @row16_mode.setter
    def row16_mode(self, mode):
        """Change the row 16 addressing mode:
            None (row 16 addressing is off = cast from row 15 instead)
            is available in all operation modes;

            HMN, KMN, unit shift are always available in the punching
            or testing modes, and conditionally available in the casting
            mode: they need to be supported in the interface configuration.
        """
        if self.status['working']:
            raise librpi2caster.InterfaceBusy
        elif not mode:
            self.status['current_row16_mode'] = OFF
        if mode not in [HMN, KMN, UNITSHIFT]:
            raise librpi2caster.UnsupportedRow16Mode
        elif self.is_casting() and mode not in self.supported_row16_modes:
            raise librpi2caster.UnsupportedRow16Mode
        else:
            self.status['current_row16_mode'] = mode

    @property
    def testing_mode(self):
        """Check whether the interface is in the testing mode"""
        return self.status['testing_mode']

    @testing_mode.setter
    def testing_mode(self, state):
        """Set the testing mode"""
        self.status['testing_mode'] = True if state else False

    @property
    def supported_operation_modes(self):
        """Get a list of supported operation modes"""
        return self.config['supported_operation_modes']

    @property
    def supported_row16_modes(self):
        """Get a list of supported row 16 addressing modes"""
        return self.config['supported_row16_modes']

    @property
    def parameters(self):
        """Gets a list of parameters"""
        parameters = OrderedDict({'': 'Caster parameters'})
        parameters.update(**self.config)
        return parameters

    def switch_operation_mode(self):
        """Switch between casting and punching"""
        new_mode = PUNCHING if self.is_casting() else CASTING
        try:
            self.operation_mode = new_mode
        except librpi2caster.UnsupportedMode:
            UI.pause('This caster does not support the {} mode'
                     .format(new_mode))
        except librpi2caster.InterfaceBusy:
            UI.pause('Cannot change the mode while the machine is working.')

    def choose_row16_mode(self, row16_needed=False):
        """Choose the addressing system for the diecase row 16."""
        if row16_needed and not self.row16_mode:
            # choose the row 16 addressing mode
            prompt = 'Choose the row 16 addressing mode'
            options = [option(key=name[0], value=name, text=name)
                       for name in self.supported_row16_modes]
            options.append(option(key='o', value=OFF,
                                  text='Off - cast from row 15 instead'))
            if len(options) > 1:
                self.row16_mode = UI.simple_menu(prompt, options,
                                                 default_key='o',
                                                 allow_abort=True)
            else:
                self.row16_mode = OFF

        elif self.row16_mode and not row16_needed:
            # turn off the unneeded row 16 adddressing attachment
            UI.display('The {} attachment is not needed - turn it off.'
                       .format(self.row16_mode))
            self.row16_mode = OFF

        else:
            if not self.row16_mode:
                UI.display('No row 16 addressing attachment is needed.')
            else:
                UI.display('Keep the {} attachment ON.'
                           .format(self.row16_mode))

    @property
    def signals(self):
        """Get the signals from the machine"""
        return self.status.get('signals', [])

    def start(self):
        """Simulates the machine start"""
        self.status.update(air=ON)
        if self.is_casting() and not self.testing_mode:
            self.status.update(water=ON, motor=ON)
        self.status.update(working=ON)

    def stop(self):
        """Simulates the machine stop"""
        if self.is_casting() and not self.testing_mode:
            self.status.update(pump=OFF, water=OFF, motor=OFF)
        self.status.update(air=OFF, working=OFF)
        self.testing_mode = False

    def send(self, signals, repeat=1, timeout=None, request_timeout=None):
        """Simulates sending the signals to the caster."""
        def update_wedges_and_pump():
            """Check the pump state and wedge positions;
            update the current status if neeeded."""
            def found(code):
                """check if code was found in a combination"""
                return set(code).issubset(signals)
            # check 0075 wedge position and determine the pump status:
            # find the earliest row number or default to 15
            if found(['0075']) or found('NK'):
                # 0075 always turns the pump on
                self.status['pump'] = ON
                for pos in range(1, 15):
                    if str(pos) in signals:
                        self.status['wedge_0075'] = pos
                        break
                else:
                    self.status['wedge_0075'] = 15

            elif found(['0005']) or found('NJ'):
                # 0005 without 0075 turns the pump off
                self.status['pump'] = OFF

            # check 0005 wedge position:
            # find the earliest row number or default to 15
            if found(['0005']) or found('NJ'):
                for pos in range(1, 15):
                    if str(pos) in signals:
                        self.status['wedge_0005'] = pos
                        break
                else:
                    self.status['wedge_0005'] = 15

        if not self.status['working']:
            raise librpi2caster.InterfaceNotStarted

        start_time = time.time()
        max_wait_time = max(timeout or 0, request_timeout or 0) or 10
        # convert signals based on modes
        parse = librpi2caster.parse_signals
        codes = parse(signals, self.operation_mode,
                      self.row16_mode, self.testing_mode)
        self.status['signals'] = codes
        try:
            for _ in range(repeat):
                update_wedges_and_pump()
                if self.testing_mode:
                    UI.display('Testing signals: {}'.format(''.join(codes)))
                elif self.is_casting():
                    UI.display('photocell ON')
                    time.sleep(0.5)
                    UI.display('photocell OFF')
                    time.sleep(0.5)
                else:
                    UI.display('punches going up')
                    time.sleep(self.config['punching_on_time'])
                    UI.display('punches going down')
                    time.sleep(self.config['punching_off_time'])
                if (time.time() - start_time) > max_wait_time:
                    raise librpi2caster.MachineStopped
        except (KeyboardInterrupt, EOFError):
            raise librpi2caster.MachineStopped
        return self.status

    def cast_one(self, record, timeout=None):
        """Casting sequence: sensor on - valves on - sensor off - valves off"""
        try:
            signals = record.signals
        except AttributeError:
            signals = record
        # calculate the timeout to prevent the request
        # from hanging indefinitely
        if timeout:
            request_timeout = 2 * timeout + 5
        else:
            request_timeout = 2 * self.config['sensor_timeout'] + 2
        return self.send(signals, timeout=timeout,
                         request_timeout=request_timeout)

    def punch_one(self, signals):
        """Punch a single signals combination"""
        off_time = self.config['punching_off_time']
        on_time = self.config['punching_on_time']
        timeout = on_time + off_time + 5
        return self.send(signals, request_timeout=timeout)

    def test_one(self, signals):
        """Test a single signals combination"""
        return self.send(signals, request_timeout=5)

    def cast(self, input_sequence, ask=True, repetitions=1):
        """Cast a series of multiple records.
        This is a simplified routine for internal use;
        normally use Casting.cast_ribbon which provides more info"""
        source = [parse_record(item) for item in input_sequence]
        # do we need to cast from row 16 and choose an attachment?
        row16_in_use = any(record.uses_row_16 for record in source)
        self.choose_row16_mode(row16_in_use)
        # use caster context to check machine rotation and ensure
        # that no valves stay open after we're done
        with self(operation_mode=CASTING):
            # cast as many as initially ordered and ask to continue
            while repetitions > 0:
                try:
                    for record in source:
                        UI.display('{r.signals:<20}{r.comment}'
                                   .format(r=record))
                        codes = self.cast_one(record).get('signals', [])
                        UI.display('casting: {}'.format(' '.join(codes)))
                    # repetition successful
                    repetitions -= 1
                except librpi2caster.MachineStopped:
                    # repetition failed
                    UI.confirm('Machine stopped: continue casting?',
                               abort_answer=False)
                if ask and not repetitions and UI.confirm('Repeat?'):
                    repetitions += 1

    def punch(self, signals_sequence):
        """Punching sequence: valves on - wait - valves off- wait"""
        # do we need to use any row16 addressing attachment?
        source = [parse_record(item) for item in signals_sequence]
        row16_in_use = any(record.uses_row_16 for record in source)
        self.choose_row16_mode(row16_in_use)
        # start punching
        with self(operation_mode=PUNCHING):
            for record in source:
                try:
                    UI.display('{r.signals:<20}{r.comment}'.format(r=record))
                    signals = self.punch_one(record.signals).get('signals', [])
                    UI.display('punching: {}'.format(' '.join(signals)))
                except librpi2caster.MachineStopped:
                    if UI.confirm('Machine stopped - continue?'):
                        signals = (self.punch_one(record.signals)
                                   .get('signals', []))
                        UI.display('punching: {}'.format(' '.join(signals)))
                    else:
                        break
            else:
                UI.display('All codes successfully punched.')
            UI.pause('Punching finished. Take the ribbon off the tower.')

    def test(self, signals_sequence, duration=None):
        """Testing: advance manually or automatically"""
        source = [parse_record(item) for item in signals_sequence]
        with self(testing_mode=ON):
            while True:
                try:
                    for record in source:
                        signals = (self.test_one(record.signals)
                                   .get('signals', []))
                        UI.display('testing: {}'.format(' '.join(signals)))
                        if duration:
                            time.sleep(duration)
                        else:
                            UI.pause('Next?', allow_abort=True)
                except librpi2caster.MachineStopped:
                    UI.display('Testing stopped.')
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
            signals = [*'ONMLKJIHGFSED', '0075', *'CBA',
                       *(str(x) for x in range(1, 15)), '0005', '15']
            UI.pause(info.format(' '.join(signals)), allow_abort=True)
            self.test(signals)

        def test_justification(*_):
            """Tests the 0075-S-0005"""
            info = 'This will test the justification pinblock: 0075, S, 0005.'
            UI.pause(info, allow_abort=True)
            self.test(['0075', 'S', '0005'])

        def test_any_code(*_):
            """Tests a user-specified combination of signals"""
            with self(testing_mode=ON):
                while True:
                    UI.display('Enter the signals to send to the caster, '
                               'or leave empty to return to menu: ')
                    signals = UI.enter('Signals?', default=Abort)
                    output_signals = self.test_one(signals).get('signals', [])
                    UI.display('Sending {}'.format(' '.join(output_signals)))

        def blow_all(*_):
            """Blow all signals for a short time; add NI, NL also"""
            info = 'Blowing air through all air pins on both pinblocks...'
            UI.pause(info, allow_abort=True)
            queue = ['NI', 'NL', 'A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7',
                     'H8', 'I9', 'J10', 'K11', 'L12', 'M13', 'N14',
                     '0075 S', '0005 O 15']
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
            with self(testing_mode=ON):
                self.test_one('G8')
                UI.pause('Sending G8, waiting for you to stop...')

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
            record, justified_record = 'G7', 'GS7'
            pump_start, pump_stop = 'NKS 0075 3', 'NJS 0005 8'
            line_out = 'NKJS 0005 0075 8'
            # start - 7 x G5 - line out - start - 7 x GS5 - line out - stop
            sequence = [pump_start, *[record] * 7, line_out, pump_start,
                        *[justified_record] * 7, line_out, pump_stop]
            self.cast(sequence)

        def calibrate_mould_and_diecase(*_):
            """Casts the "en dash" characters for calibrating the character X-Y
            relative to type body."""
            def get_codes(char, default_position):
                """Gets two mats for a given char and adjusts its parameters"""
                code = UI.enter('Where is the {}?'.format(char),
                                default=default_position)
                matrix = Matrix(' ', code=code.upper())
                # try again recursively if wrong value
                if not matrix.position.row or not matrix.position.column:
                    return get_codes(char, default_position)
                # ask for unit width
                row_units = wedge[matrix.position.row]
                units = UI.enter('Unit width?', default=row_units)
                matrix.units = units
                # calculate justifying wedge positions
                positions = get_wedge_positions(matrix, wedge, units)
                pos_0075, pos_0005 = positions.pos_0075, positions.pos_0005
                use_s_needle = (pos_0075, pos_0005) != (3, 8)
                codes = matrix.get_ribbon_record(s_needle=use_s_needle)
                sjust = ['NJS 0005 {}'.format(pos_0005),
                         'NKS 0075 {}'.format(pos_0075)]
                # use single justification to adjust character width, if needed
                return ([*sjust, codes, codes] if use_s_needle
                        else [codes, codes])

            UI.display('Mould blade opening and X-Y character calibration:\n'
                       'Cast G5, adjust the sort width to the value shown.\n'
                       '\nThen cast some lowercase "n" letters and n-dashes,\n'
                       'check the position of the character relative to the\n'
                       'type body and adjust the bridge X-Y.\n'
                       'Repeat if needed.\n')

            wedge = choose_wedge()
            # operator needs to know how wide (in inches) the sorts should be
            template = '{u} units (1{n}) is {i}" wide'
            quad_width = wedge.set_width / 12 * wedge.pica
            UI.display(template.format(u=9, n='en', i=0.5 * quad_width))
            UI.display(template.format(u=18, n='em', i=quad_width))
            # build a casting queue and cast it repeatedly
            line_out = 'NKJS 0005 0075'
            pump_stop = 'NJS 0005'
            # use half-quad, quad, "n" and en-dash
            chars = [('en quad', 'G5'), ('em quad', 'O15'),
                     ('n/h', None), ('dash', None)]
            codes = (code for what in chars for code in get_codes(*what))
            sequence = [line_out, *codes, line_out, pump_stop]
            self.cast(sequence)

        def test_row_16(*_):
            """Tests the row 16 addressing attachment (HMN, KMN, unit-shift).
            Casts from all matrices in 16th row.
            """
            UI.display('This will test the 16th row addressing.\n'
                       'If your caster has HMN, KMN or unit-shift attachment, '
                       'turn it on.\n')
            # build casting queue
            pump_start, pump_stop = 'NKS 0075', 'NJS 0005'
            line_out = 'NKJS 0005 0075'
            row = ['{}16'.format(col)
                   for col in ('NI', 'NL', *'ABCDEFGHIJKLMNO')]
            # test with actual casting or not?
            if UI.confirm('Use the pump? Y = cast the row, N = test codes.'):
                sequence = [pump_start, *row, line_out, pump_stop]
                self.cast(sequence)
            else:
                self.choose_row16_mode(row16_needed=True)
                self.test(row)

        def options():
            """Generate the menu options"""
            ret = [option(key='a', value=test_all, seq=1,
                          text='Test outputs',
                          desc='Test all the air outputs N...O15, one by one'),
                   option(key='f', value=test_front_pinblock, seq=2,
                          text='Test the front pin block',
                          desc='Test the pins 1...14'),
                   option(key='r', value=test_rear_pinblock, seq=2,
                          text='Test the rear pin block',
                          desc='Test the pins NI, NL, A...N, one by one'),
                   option(key='b', value=blow_all, seq=2,
                          text='Blow all air pins',
                          desc='Blow air into every pin for a short time'),
                   option(key='j', value=test_justification, seq=2,
                          text='Test the justification block',
                          desc='Test the pins for 0075, S and 0005'),
                   option(key='c', value=test_any_code, seq=1,
                          text='Send specified signal combination',
                          desc='Send the specified signals to the machine'),
                   option(key='w', value=calibrate_wedges, seq=4,
                          cond=self.is_casting,
                          text='Calibrate the 52D wedge',
                          desc=('Calibrate the space transfer wedge '
                                'for correct width')),
                   option(key='d', value=calibrate_mould_and_diecase, seq=4,
                          cond=self.is_casting,
                          text='Calibrate mould blade and diecase',
                          desc=('Set the type body width and '
                                'character-to-body position')),
                   option(key='m', value=calibrate_draw_rods, seq=3,
                          cond=self.is_casting,
                          text='Calibrate matrix case draw rods',
                          desc=('Keep the matrix case at G8 '
                                'and adjust the draw rods')),
                   option(key='l', value=test_row_16, seq=5,
                          cond=self.is_casting,
                          text='Test the extended 16x17 diecase system',
                          desc=('Cast type from row 16 '
                                'with HMN, KMN or unit-shift'))]
            return ret

        header = 'Diagnostics and machine calibration menu:'
        catch_exceptions = (Abort, KeyboardInterrupt, EOFError,
                            librpi2caster.MachineStopped)
        # Keep displaying the menu and go back here after any method ends
        UI.dynamic_menu(options=options, header=header, func_args=(self,),
                        catch_exceptions=catch_exceptions)


class MonotypeCaster(SimulationCaster):
    """Methods common for Caster classes, used for instantiating
    caster driver objects (whether real hardware or mockup for simulation)."""
    def _setup(self):
        """Initialize the caster"""
        if not self.url:
            message = 'Interface URL not specified!'
            raise librpi2caster.ConfigurationError(message)
        self.config = self._request(request_timeout=(1, 1)).get('settings')

    def _request(self, path='', request_timeout=None,
                 method=requests.get, **kwargs):
        """Encode data with JSON and send it to self.url in a request."""
        errors = {exc.code: exc
                  for exc in (librpi2caster.MachineStopped,
                              librpi2caster.UnsupportedMode,
                              librpi2caster.UnsupportedRow16Mode,
                              librpi2caster.InterfaceBusy,
                              librpi2caster.InterfaceNotStarted)}
        url = '{}/{}'.format(self.url, path).strip('/')
        data = kwargs or {}
        try:
            # get the info from the server
            response = method(url, json=data, timeout=request_timeout)
            # raise any HTTP errors ASAP
            response.raise_for_status()
            # we're sure we have a proper 200 OK status code
            reply = response.json()
            if not reply.get('success'):
                # shit happened in the driver
                error_code = reply.get('error_code', 666)
                exception = errors.get(error_code)
                if exception:
                    raise exception
            # return the content without the success value
            reply.pop('success')
            return reply
        except requests.exceptions.InvalidSchema:
            # wrong URL
            msg = 'The URL: {} must be a http://... or https://... address.'
            raise librpi2caster.ConfigurationError(msg.format(self.url))
        except requests.HTTPError as error:
            if response.status_code == 501:
                raise NotImplementedError('{}: feature not supported by server'
                                          .format(url))
            # 400, 404, 503 etc.
            raise librpi2caster.CommunicationError(str(error))
        except requests.Timeout:
            msg = 'Connection to {} timed out.'
            raise librpi2caster.CommunicationError(msg.format(self.url))
        except JSONDecodeError:
            msg = 'Connection to {} returned incorrect data (expected: JSON).'
            raise librpi2caster.CommunicationError(msg.format(self.url))
        except requests.ConnectionError:
            msg = 'Error connecting to {}.'
            raise librpi2caster.CommunicationError(msg.format(self.url))

    @property
    def operation_mode(self):
        """Get the current operation mode:
            None = testing; casting; punching"""
        return self.status['current_operation_mode']

    @operation_mode.setter
    @handle_communication_error
    def operation_mode(self, mode):
        """Set the operation mode"""
        self._request('operation_mode', method=requests.post, mode=mode)

    @property
    def row16_mode(self):
        """Get the row 16 addressing mode:
            None = off, HMN, KMN, unit shift"""
        return self.status['current_row16_mode']

    @row16_mode.setter
    @handle_communication_error
    def row16_mode(self, mode):
        """Change the row 16 addressing mode:
            None (row 16 addressing is off = cast from row 15 instead)
            is available in all operation modes;

            HMN, KMN, unit shift are always available in the punching
            or testing modes, and conditionally available in the casting
            mode: they need to be supported in the interface configuration.
        """
        self._request('row16_mode', method=requests.post, mode=mode)

    @property
    def testing_mode(self):
        """Get the current testing mode state"""
        return self.status['testing_mode']

    @testing_mode.setter
    @handle_communication_error
    def testing_mode(self, state):
        """Set the temporary testing mode on the interface"""
        value = True if state else False
        self._request(method=requests.post, testing_mode=value)

    @handle_communication_error
    def send(self, signals='', repeat=1, timeout=None, request_timeout=None):
        """Send signals to the interface. Wait for an OK response."""
        try:
            data = dict(signals=signals, repeat=repeat, timeout=timeout)
            return self._request('signals', method=requests.post,
                                 request_timeout=request_timeout, **data)
        except librpi2caster.InterfaceNotStarted:
            self.start()
            return self._request('signals', method=requests.post,
                                 request_timeout=request_timeout, **data)
        except (KeyboardInterrupt, EOFError, librpi2caster.CommunicationError):
            self.stop()
            raise librpi2caster.MachineStopped

    @handle_communication_error
    def start(self):
        """Machine startup sequence.
        In the casting mode:
            The interface will start the subsystems, if possible:
                compressed air supply, cooling water supply and motor.
            The operator has to turn the machine's shaft clutch on.
            The interface driver will detect rotation, and if the machine
            is stalling, a MachineStopped exception is raised.

        In other modes (testing, punching, manual punching):
            The interface will just turn on the compressed air supply.
        """
        if self.testing_mode:
            request_timeout = 5
        elif self.is_casting():
            info = ('Starting the composition caster...\n'
                    'Turn on the motor if necessary, and engage the clutch.\n'
                    'Casting will begin after detecting the machine rotation.\n'
                    '\nCommence casting? (N = abort)')
            if not UI.confirm(info):
                raise Abort
            request_timeout = 3 * self.config['startup_timeout'] + 2
        else:
            UI.pause('Waiting for you to start punching...')
            request_timeout = 5
        # send the request and handle any exceptions
        try:
            self._request('machine', method=requests.post,
                          request_timeout=request_timeout, machine=ON)
        except librpi2caster.InterfaceBusy:
            UI.pause('This interface is already working. Aborting...')
            raise Abort
        if self.is_casting():
            UI.display('OK, the machine is running...')

    @handle_communication_error
    def stop(self):
        """Machine stop sequence.
        The interface driver checks if the pump is active
        and turns it off if necessary.

        In the casting mode, the driver will turn off the motor
        and cut off the cooling water supply.
        Then, the air supply is cut off.
        """
        if self.testing_mode:
            request_timeout = 3
        elif self.is_casting():
            UI.display('Turning the machine off...')
            request_timeout = self.config['pump_stop_timeout'] * 2 + 2
        else:
            request_timeout = 3
        self._request('machine', method=requests.delete,
                      request_timeout=request_timeout)

    @property
    @handle_communication_error
    def status(self):
        """Get the interface status"""
        return self._request().get('status')

    @status.setter
    def status(self, _):
        """Prevents raising AttributeError when assigning to status"""
