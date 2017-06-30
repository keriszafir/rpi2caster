# -*- coding: utf-8 -*-
"""Caster object for either real or virtual Monotype composition caster"""
# Standard library imports
import time
from collections import OrderedDict
import requests

# Intra-package imports
from .rpi2caster import UI, option, Abort
from .casting_models import Record
from .matrix_controller import MatrixEngine
from .definitions import WedgePositions

# Constants for readability
ON = True
OFF = True
AIR_ON = True
AIR_OFF = False

# Error codes in rpi2caster interface API
MACHINE_STOPPED = 0
UNSUPPORTED_MODE = 1
UNSUPPORTED_ROW16_MODE = 2
INTERFACE_BUSY = 3
INTERFACE_NOT_STARTED = 4
HARDWARE_CONFIG_ERROR = 5

# Operation modes
TESTING = 'testing'
CASTING = 'casting'
PUNCHING = 'punching'
MANUAL_PUNCHING = 'manual_punching'

# Row 16 adressing modes
ROW16_OFF = 'off'
ROW16_HMN = 'HMN'
ROW16_KMN = 'KMN'
ROW16_SHIFT = 'unit shift'


class Interface:
    """A class for controlling the remote or local interfaces
    via JSON-over-HTTP.

    Interfaces need following parameters:
        * interface URL (HTTP non-typical port 23017 - for MCP23017)
        * mode (casting / punching / testing)
    """
    def __init__(self, url='http://localhost:23017/interfaces/0',
                 operation_mode=CASTING, row16_mode=ROW16_OFF):
        self.url = url
        interface_config = self._request(timeout=(3.2, 5)).get('settings')
        self.config = interface_config
        # set the modes
        self.modes(operation_mode, row16_mode)

    def __call__(self, operation_mode=None, row16_mode=None):
        # call interface with modes in entering the context manager
        self.modes(operation_mode, row16_mode)
        return self

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()

    def _request(self, path='', timeout=None, method=requests.get, **kwargs):
        """Encode data with JSON and send it to self.url in a request."""
        url = '{}/{}'.format(self.url, path)
        data = kwargs or {}
        try:
            # get the info from the server
            response = method(url, json=data, timeout=timeout)
            # raise any HTTP errors ASAP
            response.raise_for_status()
            # we're sure we have a proper 200 OK status code
            reply = response.json()
            if not reply.get('success'):
                # shit happened in the driver
                exception = DriverError
                exception.code = reply.get('error_code', 666)
                exception.message = reply.get('error_name', 'unknown error')
                exception.offending_value = reply.get('offending_value')
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

    def modes(self, operation_mode=None, row16_mode=None):
        """Mode manager: get or set interface operation
        and row 16 addressing modes"""
        cached = self.__dict__.get('_modes')
        if operation_mode is None and row16_mode is None and cached:
            return cached
        # no cached modes or not setting new ones - then send a request
        try:
            modes = self._request('modes', method=requests.post,
                                  operation_mode=operation_mode,
                                  row16_mode=row16_mode)
            self.__dict__['_modes'] = modes
            return modes
        except DriverError as error:
            if error.code == UNSUPPORTED_MODE:
                UI.pause('Cannot set the operation mode to {}.'
                         .format(operation_mode))
            if error.code == UNSUPPORTED_ROW16_MODE:
                UI.pause('Cannot set the row 16 addressing mode to {}.'
                         .format(row16_mode))
            return cached

    def send(self, signals=''):
        """Send signals to the interface. Wait for an OK response."""
        try:
            self._request('signals', method=requests.post, signals=signals)
        except DriverError as error:
            if error.code == MACHINE_STOPPED:
                raise MachineStopped
            elif error.code == INTERFACE_NOT_STARTED:
                self.machine(ON)
                return self.send(signals)

    def justification(self, pos_0075=None, pos_0005=None, galley_trip=False):
        """Get or set the justification wedge positions"""
        reply = self._request('wedges', method=requests.post,
                              wedge_0005=pos_0005, wedge_0075=pos_0075)
        new_0075 = reply.get('wedge_0075')
        new_0005 = reply.get('wedge_0005')
        return WedgePositions(new_0075, new_0005)

    def pump(self, state=None):
        """Pump control:
            None - get status,
            True or False - turn on or off.
        """
        reply = self._request('pump', method=requests.post, pump=state)
        return reply.get('state')

    def air(self, state=None):
        """Air supply control:
            None - get status,
            True or False - turn on or off.
        """
        reply = self._request('air', method=requests.post, air=state)
        return reply.get('state')

    def water(self, state=None):
        """Cooling water supply control:
            None - get status,
            True or False - turn on or off.
        """
        reply = self._request('water', method=requests.post, water=state)
        return reply.get('state')

    def motor(self, state=None):
        """Motor control:
            None - get status,
            True or False - turn on or off.
        """
        reply = self._request('motor', method=requests.post, motor=state)
        return reply.get('state')

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
        mode = self.modes()['current_operation_mode']
        if mode == CASTING:
            info = ('Starting the composition caster...\n'
                    'Turn on the motor if necessary, and engage the clutch.\n'
                    'Casting will begin after detecting the machine rotation.')
            UI.display(info)
        elif mode in (PUNCHING, MANUAL_PUNCHING):
            UI.pause('Waiting for you to start punching...')
        # send the request and handle any exceptions
        try:
            self._request('machine', method=requests.post, machine=True)
        except DriverError as error:
            if error.code == MACHINE_STOPPED:
                raise MachineStopped
            elif error.code == INTERFACE_BUSY:
                UI.pause('This interface is already working. Aborting...')
                raise Abort
        if mode == CASTING:
            UI.display('OK, the machine is running...')

    def stop(self):
        """Machine stop sequence.
        The interface driver checks if the pump is active
        and turns it off if necessary.

        In the casting mode, the driver will turn off the motor
        and cut off the cooling water supply.
        Then, the air supply is cut off.
        """
        mode = self.modes()['current_operation_mode']
        if mode == CASTING:
            UI.display('Turning the machine off...')
        elif mode in (PUNCHING, MANUAL_PUNCHING):
            UI.display('Punching finished. Take the ribbon off the tower.')
        self._request('machine', method=requests.post, machine=True)

    @property
    def status(self):
        """Get the interface status"""
        return self._request().get('status')

    @property
    def speed(self):
        """Get the speed in revolutions-per-minute speed."""
        return self.status.get('speed')

    @property
    def signals(self):
        """Get the signals from the machine"""
        return self._request('signals')

    def valves_on(self, signals=''):
        """Low-level valve control on the interface: ON"""
        return self._request('valves', method=requests.post, valves=signals)

    def valves_off(self):
        """Low-level valve control on the interface: OFF"""
        return self._request('valves', method=requests.delete)


class SimulationInterface(Interface):
    """Simulates the interface without sending/receiving any requests."""
    def __init__(self, url='simulation'):
        self.url = url
        self.mode = 'casting'
        self.row16_mode = 'off'

    def __enter__(self):
        UI.display('Now turning the machine on...')
        return self

    @staticmethod
    def __exit__(*_):
        UI.display('Now turning the machine off...')

    def send(self, signals):
        """Simulates sending the signals to the caster."""
        converted_signals = signals
        if self.mode == CASTING:
            UI.display('photocell ON')
            UI.display('sending {}'.format(converted_signals))
            time.sleep(0.2)
            UI.display('photocell OFF')
            time.sleep(0.2)

    @staticmethod
    def valves_on(signals):
        """Simulates sending signals to the valves directly."""
        UI.display('Sending {}'.format(''.join(signals)))

    @staticmethod
    def valves_off():
        """Simulates turning the valves off."""
        UI.display('Valves off.')

    def modes(self, operation_mode=None, row16_mode=None):
        """This interface supports all modes."""
        modes = self.__dict__.get('_modes')
        if not modes:
            modes = dict(current_operation_mode=CASTING,
                         current_row16_mode=ROW16_OFF,
                         default_operation_mode=CASTING,
                         default_row16_mode=OFF,
                         supported_modes=[TESTING, CASTING,
                                          PUNCHING, MANUAL_PUNCHING],
                         supported_row16_modes=[ROW16_OFF, ROW16_HMN,
                                                ROW16_KMN, ROW16_SHIFT])
            self.__dict__['_modes'] = modes
        if operation_mode in self.__dict__['_modes']['supported_modes']:
            self.__dict__['_modes']['current_operation_mode'] = operation_mode
        elif operation_mode is not None:
            UI.pause('Cannot set the operation mode to {}'
                     .format(operation_mode))
        if row16_mode in self.__dict__['_modes']['supported_row16_modes']:
            self.__dict__['_modes']['current_row16_mode'] = row16_mode
        elif row16_mode is not None:
            UI.pause('Cannot set the row 16 addressing mode to {}'
                     .format(row16_mode))
        return self.__dict__['_modes']


class MonotypeCaster:
    """Methods common for Caster classes, used for instantiating
    caster driver objects (whether real hardware or mockup for simulation)."""
    working, pump_working = False, False
    sensor, output = None, None
    row_16_mode = 'off'

    def __init__(self, runtime_config):
        """Lock the resource so that only one object can use it
        with context manager"""
        self.runtime_config = runtime_config
        self.interface = Interface(runtime_config.interface_url,
                                   operation_mode=runtime_config.mode)

    def __enter__(self):
        # initialize hardware interface; check if machine is running
        self.interface.__enter__()
        return self

    def __exit__(self, *_):
        self.interface.__exit__()

    @property
    def parameters(self):
        """Gets a list of parameters"""
        # Collect data from I/O drivers
        parameters = OrderedDict({'': 'Caster parameters'})
        parameters.update(**self.interface.config)
        return parameters

    def check_row_16(self, is_required=False):
        """Choose the diecase row 16 addressing mode, if needed.

        Row 16 is needed and currently off:
        Ask which row 16 addressing system the user's machine has, if any.

        Row 16 is not needed and currently on:
        Tell the user to turn off the attachment.

        Row 16 is not needed and is off, or is needed and is on: do nothing.
        """
        is_active = self.row_16_mode != 'off'

        # check and notify the user
        if is_required and not is_active:
            self.choose_row16_addressing()
        elif is_active and not is_required:
            UI.pause('\n\nTurn off the {} attachment.\n\n'
                     .format(self.row_16_mode))
            self.row_16_mode = 'off'
        elif is_required and is_active:
            UI.display('The {} attachment is turned on - OK.'
                       .format(self.row_16_mode))

    def choose_row16_addressing(self):
        """Let user decide which way to address row 16"""
        prompt = ('Your ribbon contains codes from the 16th row.\n'
                  'It is supported by special attachments for the machine.\n'
                  'Which mode does your caster use: HMN, KMN, Unit-Shift?\n\n'
                  'If off - characters from row 15 will be cast instead.')
        options = [option(key='h', value='HMN', seq=1, text='HMN'),
                   option(key='k', value='KMN', seq=2, text='KMN'),
                   option(key='u', value='unit shift', seq=3,
                          text='Unit shift'),
                   option(key='o', value='off', seq=4,
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
        source = [Record(item, signal_o15=True, default_o15=True)
                  for item in signals_sequence]
        r16_needed = any(record.code.uses_row_16 for record in source)
        self.check_row_16(r16_needed)
        # we only need output and not sensor for this action
        with self.output:
            for record in source:
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

        supported_modes = self.interface.modes['supported_operation_modes']
        is_a_caster = CASTING in supported_modes
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
        return 'Machine stopped: no rotation detected'


class WrongConfiguration(Exception):
    """Interface improperly configured"""


class DriverError(Exception):
    """The interface API replied with a proper 200 status code,
    but the driver failed to perform the action."""


class CommunicationError(Exception):
    """Error communicating with the interface."""
