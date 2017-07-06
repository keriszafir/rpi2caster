# -*- coding: utf-8 -*-
"""Caster object for either real or virtual Monotype composition caster"""
# Standard library imports
import time
from collections import OrderedDict
import requests

# Intra-package imports
from .rpi2caster import UI, CFG, option, Abort
from .parsing import parse_record
from .matrix_controller import MatrixEngine

# Constants for readability
ON, OFF = True, False


def choose_machine(interface_id=None, operation_mode=None):
    """Choose a machine from the available interfaces."""
    def make_caster(url):
        """caster factory method: make a real or simulation caster;
        if something bad happens, just return None"""
        if url:
            try:
                return MonotypeCaster(url, operation_mode)
            except (CommunicationError, UnsupportedMode):
                return None
        else:
            return SimulationCaster(url, operation_mode)

    def make_caster_menu_entry(caster):
        """make a menu entry for caster choice"""
        config = caster.config
        name = config.get('name', 'Unknown caster')
        modes = ', '.join(caster.supported_operation_modes)
        row16_modes = ', '.join(caster.supported_row16_modes) or 'none'
        description = ('{} - modes: {} - row 16 addressing modes: {}'
                       .format(name, modes, row16_modes))
        return option(value=caster, text=description)

    # get the interface URLs (first one is empty and corresponds to a
    # simulation interface)
    raw_urls = CFG['System']['interfaces']
    operation_mode = operation_mode or CFG['Runtime']['operation_mode']
    # make several default interfaces so the program will always
    # try to connect to these as a priority
    # the first interface is a simulation and it is available as interface 0
    urls = ['', 'http://localhost:23017',
            'http://localhost:23017/interfaces/0',
            *(x.strip() for x in raw_urls.split(','))]
    casters = [make_caster(url) for url in urls]
    try:
        caster = casters[interface_id]
        if not caster:
            raise ValueError
        return caster
    except (IndexError, TypeError, ValueError):
        # choose caster from menu
        options = [make_caster_menu_entry(caster)
                   for caster in casters if caster]
        return UI.simple_menu('Choose the caster:', options)


class SimulationCaster:
    """Common methods for a caster class."""
    def __init__(self, url=None, operation_mode=None):
        self.url = url
        self.config, self.status = dict(), dict()
        self._setup()
        default_operation_mode = self.config['default_operation_mode']
        self.operation_mode = operation_mode or default_operation_mode
        self.row16_mode = None

    def _setup(self):
        """Setup a simulation caster"""
        self.config = dict(supported_operation_modes=['casting', 'punching'],
                           supported_row16_modes=['HMN', 'KMN', 'unit shift'],
                           default_operation_mode='casting',
                           default_row16_mode=None,
                           punching_on_time=0.2, punching_off_time=0.3,
                           name='Simulation interface')
        self.status = dict(water=OFF, air=OFF, motor=OFF, pump=OFF,
                           wedge_0005=15, wedge_0075=15, speed='0rpm',
                           working=OFF, testing_mode=OFF, signals=[])

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

    def is_punching(self):
        """Determines if this caster is set to punching """
        return self.operation_mode == 'punching'

    def is_casting(self):
        """Determines if this caster is set to casting"""
        return self.operation_mode == 'casting'

    @property
    def testing_mode(self):
        """Check whether the interface is in the testing mode"""
        return self.status['testing_mode']

    @testing_mode.setter
    def testing_mode(self, state):
        """Set the testing mode"""
        if state is not None:
            self.status['testing_mode'] = True if state else False

    @property
    def supported_operation_modes(self):
        """Get a list of supported operation modes"""
        return self.config['supported_operation_modes']

    @property
    def supported_row16_modes(self):
        """Get a list of supported row 16 addressing modes"""
        return self.config['supported_row16_modes']

    def switch_operation_mode(self):
        """Switch between casting and punching"""
        new_mode = 'casting' if self.is_punching() else 'punching'
        try:
            self.operation_mode = new_mode
        except UnsupportedMode:
            UI.pause('This caster does not support the {} mode'
                     .format(new_mode))
        except InterfaceBusy:
            UI.pause('Cannot change the mode while the machine is working.')

    @property
    def parameters(self):
        """Gets a list of parameters"""
        parameters = OrderedDict({'': 'Caster parameters'})
        parameters.update(**self.config)
        return parameters

    def choose_row16_mode(self, row16_needed=False):
        """Choose the addressing system for the diecase row 16."""
        if row16_needed and not self.row16_mode:
            # choose the row 16 addressing mode
            prompt = 'Choose the row 16 addressing mode'
            options = [option(key=name[0], value=name, text=name)
                       for name in self.supported_row16_modes]
            options.append(option(key='o', value=None,
                                  text='Off - cast from row 15 instead'))
            if len(options) > 1:
                new_mode = UI.simple_menu(prompt, options,
                                          default_key='o', allow_abort=True)
            else:
                new_mode = None
            self.row16_mode = new_mode

        elif self.row16_mode and not row16_needed:
            # turn off the unneeded row 16 adddressing attachment
            UI.display('The {} attachment is not needed - turn it off.'
                       .format(self.row16_mode))
            self.row16_mode = None

        else:
            if not self.row16_mode:
                UI.display('No row 16 addressing attachment is needed.')
            else:
                UI.display('Keep the {} attachment ON.'
                           .format(self.row16_mode))

    @property
    def speed(self):
        """Simulate getting the current speed"""
        return self.status.get('speed', '0rpm')

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

    def send(self, signals, timeout=None, request_timeout=None):
        """Simulates sending the signals to the caster."""
        if not self.status['working']:
            raise InterfaceNotStarted

        start_time = time.time()
        max_wait_time = max(timeout or 0, request_timeout or 0) or 10
        # placeholder for mode-dependent signal conversions
        converted_signals = signals
        self.status['signals'] = converted_signals
        try:
            if self.testing_mode:
                UI.display('Testing signals: {}'
                           .format(''.join(converted_signals)))
            elif self.is_casting():
                UI.display('photocell ON')
                time.sleep(0.5)
                UI.display('photocell OFF')
                time.sleep(0.5)
            elif self.is_punching():
                UI.display('punches going up')
                time.sleep(self.config['punching_on_time'])
                UI.display('punches going down')
                time.sleep(self.config['punching_off_time'])
            if (time.time() - start_time) > max_wait_time:
                raise MachineStopped
        except (KeyboardInterrupt, EOFError):
            raise MachineStopped
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
        return self.send(signals, timeout, request_timeout)

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
        row16_in_use = any((record.code.uses_row_16 for record in source))
        self.choose_row16_mode(row16_in_use)
        # use caster context to check machine rotation and ensure
        # that no valves stay open after we're done
        with self(operation_mode='casting'):
            # cast as many as initially ordered and ask to continue
            while repetitions > 0:
                try:
                    for record in source:
                        UI.display('{r.signals:<20}{r.comment}'
                                   .format(r=record))
                        codes = self.cast_one(record).get('signals', [])
                        UI.display('signals cast: {}'.format(' '.join(codes)))
                    # repetition successful
                    repetitions -= 1
                except MachineStopped:
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
        with self(operation_mode='punching'):
            for record in source:
                UI.display('{r.signals:<20}{r.comment}'.format(r=record))
                signals = self.punch_one(record.signals).get('signals', [])
                UI.display('signals punched: {}'.format(' '.join(signals)))

    def test(self, signals_sequence, duration=None):
        """Testing: advance manually or automatically"""
        source = [parse_record(item) for item in signals_sequence]
        with self(testing_mode=True):
            while True:
                for record in source:
                    signals = self.test_one(record.signals).get('signals', [])
                    UI.display('Sending: {}'.format(' '.join(signals)))
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
            with self(operation_mode=None):
                while True:
                    UI.display('Enter the signals to send to the caster, '
                               'or leave empty to return to menu: ')
                    signals = UI.enter('Signals?', default=Abort)
                    output_signals = self.test_one(signals)
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
            with self(testing_mode=True):
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
            def get_codes(mat):
                """Gets two mats for a given char and adjusts its parameters"""
                positions = mat_engine.get_wedge_positions(mat)
                pos_0075, pos_0005 = positions.pos_0075, positions.pos_0005
                use_s_needle = (pos_0075, pos_0005) != (3, 8)
                codes = mat.get_ribbon_record(s_needle=use_s_needle)
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
            line_out = 'NKJS 0005 0075'
            pump_stop = 'NJS 0005'
            codes = (code for mat in mats for code in get_codes(mat))
            sequence = [*codes, line_out, pump_stop]
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

        options = [option(key='a', value=test_all, seq=1,
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

        header = 'Diagnostics and machine calibration menu:'
        catch_exceptions = (Abort, KeyboardInterrupt, EOFError, MachineStopped)
        # Keep displaying the menu and go back here after any method ends
        UI.dynamic_menu(options=options, header=header, func_args=(self,),
                        catch_exceptions=catch_exceptions)


class MonotypeCaster(SimulationCaster):
    """Methods common for Caster classes, used for instantiating
    caster driver objects (whether real hardware or mockup for simulation)."""
    def _setup(self):
        """Initialize the caster"""
        if not self.url:
            raise WrongConfiguration('Interface URL not specified!')
        self.config = self._request(request_timeout=(3.05, 5)).get('settings')

    def _request(self, path='', request_timeout=None,
                 method=requests.get, **kwargs):
        """Encode data with JSON and send it to self.url in a request."""
        errors = {exc.code: exc
                  for exc in (MachineStopped,
                              UnsupportedMode, UnsupportedRow16Mode,
                              InterfaceBusy, InterfaceNotStarted)}
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
            raise WrongConfiguration(msg.format(self.url))
        except requests.HTTPError as error:
            if response.status_code == 501:
                raise NotImplementedError('{}: not supported by server'
                                          .format(url))
            # 400, 404, 503 etc.
            raise CommunicationError(str(error))
        except (requests.ConnectionError, requests.Timeout):
            # address not on the network; no network on client or server;
            # DNS failure; blocked by firewall etc.
            msg = 'Cannot connect to {}. Check the network configuration.'
            raise CommunicationError(msg.format(self.url))

    @property
    def operation_mode(self):
        """Get the current operation mode:
            None = testing; casting; punching"""
        # use False as a fallback value because None is a valid option here
        if self.__dict__.get('_operation_mode', False) is False:
            mode = self._request('operation_mode')
            self.__dict__['_operation_mode'] = mode
        # we're sure that we have a value by now (and it's cached for future)
        return self.__dict__['_operation_mode']

    @operation_mode.setter
    def operation_mode(self, mode):
        """Set the operation mode"""
        data = self._request('operation_mode', method=requests.post, mode=mode)
        self.__dict__['_operation_mode'] = data.get('mode')

    @property
    def row16_mode(self):
        """Get the row 16 addressing mode:
            None = off, HMN, KMN, unit shift"""
        # use False as a fallback value because None is a valid option here
        if self.__dict__.get('_row16_mode', False) is False:
            mode = self._request('row16_mode')
            self.__dict__['_row16_mode'] = mode
        # we're sure that we have a value by now (and it's cached for future)
        return self.__dict__['_row16_mode']

    @row16_mode.setter
    def row16_mode(self, mode):
        """Change the row 16 addressing mode:
            None (row 16 addressing is off = cast from row 15 instead)
            is available in all operation modes;

            HMN, KMN, unit shift are always available in the punching
            or testing modes, and conditionally available in the casting
            mode: they need to be supported in the interface configuration.
        """
        data = self._request('row16_mode', method=requests.post, mode=mode)
        self.__dict__['_row16_mode'] = data.get('mode')

    @property
    def testing_mode(self):
        """Get the current testing mode state"""
        return self.status['testing_mode']

    @testing_mode.setter
    def testing_mode(self, state):
        """Set the temporary testing mode on the interface"""
        if state is not None:
            self._request(method=requests.post,
                          testing_mode=True if state else False)

    def send(self, signals='', timeout=None, request_timeout=None):
        """Send signals to the interface. Wait for an OK response."""
        try:
            return self._request('signals', method=requests.post,
                                 signals=signals, timeout=timeout,
                                 request_timeout=request_timeout)
        except InterfaceNotStarted:
            self.start()
            return self.send(signals, timeout)
        except (KeyboardInterrupt, EOFError):
            self.stop()
            raise MachineStopped
        except UnsupportedMode:
            UI.pause('This interface does not support casting.')

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
                    'Casting will begin after detecting the machine rotation.')
            UI.display(info)
            request_timeout = 3 * self.config['startup_timeout'] + 2
        elif self.is_punching():
            UI.pause('Waiting for you to start punching...')
            request_timeout = 5
        # send the request and handle any exceptions
        try:
            self._request('machine', method=requests.post,
                          request_timeout=request_timeout, machine=True)
        except InterfaceBusy:
            UI.pause('This interface is already working. Aborting...')
            raise Abort
        if self.is_casting():
            UI.display('OK, the machine is running...')

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
        elif self.is_punching():
            UI.display('Punching finished. Take the ribbon off the tower.')
            request_timeout = 2
        self._request('machine', method=requests.delete,
                      request_timeout=request_timeout)

    @property
    def status(self):
        """Get the interface status"""
        return self._request().get('status')

    @status.setter
    def status(self, _):
        """Prevents raising AttributeError when assigning to status"""


class InterfaceException(Exception):
    """Base class for interface-related exceptions"""
    message = 'General interface error.'
    offending_value = ''

    def __str__(self):
        return self.message


class MachineStopped(Exception):
    """machine not turning exception"""
    code = 0
    message = 'The machine has been stopped.'


class UnsupportedMode(Exception):
    """The operation mode is not supported by this interface."""
    code = 1
    message = ("This operation mode is not supported "
               "in the interface's configuration")


class UnsupportedRow16Mode(Exception):
    """The row 16 addressing mode is not supported by this interface."""
    code = 2
    message = ("This row 16 addressing mode is not supported "
               "in the interface's configuration")


class InterfaceBusy(Exception):
    """the interface was claimed by another client and cannot be used
    until it is released"""
    code = 3
    message = ('This interface has been claimed by another client. '
               'If this is not the case, restart it.')


class InterfaceNotStarted(Exception):
    """the interface was not started and cannot accept signals"""
    code = 4
    message = 'The interface needs to be started first to be operated.'


class WrongConfiguration(Exception):
    """Interface improperly configured"""
    code = 5
    message = 'Wrong value encountered in the configuration file.'


class CommunicationError(Exception):
    """Error communicating with the interface."""
    code = 6
    message = ('Cannot communicate with the interface. '
               'Check the network connection and/or configuration.')
