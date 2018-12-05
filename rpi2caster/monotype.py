# -*- coding: utf-8 -*-
"""Caster object for either real or virtual Monotype composition caster"""
# Standard library imports
from collections import deque, OrderedDict
from functools import wraps
from json.decoder import JSONDecodeError
import time

import requests
import librpi2caster

# Intra-package imports
from . import ui, stats
from .functions import parse_record, parse_signals

ON, OFF, HMN, KMN, UNITSHIFT = True, False, 'HMN', 'KMN', 'unit shift'


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
            if ui.confirm(message.format(error), abort_answer=False):
                return routine(*args, **kwargs)
    return wrapper


class SimulationCaster:
    """Common methods for a caster class."""
    def __init__(self, address='127.0.0.1', port=23017):
        self.url = 'http://{}:{}'.format(address, port)
        self.row16_mode = OFF
        self.config = dict(punching_on_time=0.2, punching_off_time=0.3,
                           sensor_timeout=5, pump_stop_timeout=20,
                           startup_timeout=20, name='Simulation interface',
                           punch_mode=False)
        self.status = dict(water=OFF, air=OFF, motor=OFF, pump=OFF,
                           wedge_0005=15, wedge_0075=15, speed='0rpm',
                           machine=OFF, signals=[])
        self.update_config()
        self.update_status()

    def __str__(self):
        return self.config['name']

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()

    @property
    def punch_mode(self):
        """Checks if the interface is in ribbon punching mode."""
        return self.config.get('punch_mode')

    @punch_mode.setter
    def punch_mode(self, state):
        """Sets the ribbon punching mode."""
        self.update_config(punch_mode=bool(state))

    @property
    def testing_mode(self):
        """Checks the testing mode where signals are advanced manually."""
        return self.status.get('testing_mode')

    @testing_mode.setter
    def testing_mode(self, state):
        """Sets the testing mode"""
        self.update_status(testing_mode=bool(state))

    @property
    def parameters(self):
        """Gets a list of parameters"""
        parameters = OrderedDict({'': 'Caster parameters'})
        parameters.update(**self.config)
        return parameters

    @property
    def emergency_stop(self):
        """Check the emergency stop state"""
        return self.status.get('emergency_stop')

    @emergency_stop.setter
    def emergency_stop(self, state):
        """Activate or reset the machine emergency stop"""
        if state:
            self.stop()
        self.status.update(emergency_stop=state)

    def update_status(self, **kwargs):
        """Update the machine status."""
        self.status.update(**kwargs)

    def update_config(self, **kwargs):
        """Update the configuration."""
        self.config.update(**kwargs)

    def choose_row16_mode(self, row16_needed=False):
        """Choose the addressing system for the diecase row 16."""
        if row16_needed and not self.row16_mode:
            # choose the row 16 addressing mode
            prompt = 'Choose the row 16 addressing mode'
            options = [ui.option(key=name[0], value=name, text=name)
                       for name in [HMN, KMN, UNITSHIFT]]
            options.append(ui.option(key='o', value=OFF,
                                     text='Off - cast from row 15 instead'))
            if len(options) > 1:
                self.row16_mode = ui.simple_menu(prompt, options,
                                                 default_key='o',
                                                 allow_abort=True)
            else:
                self.row16_mode = OFF

        elif self.row16_mode and not row16_needed:
            # turn off the unneeded row 16 adddressing attachment
            ui.display('The {} attachment is not needed - turn it off.'
                       .format(self.row16_mode))
            self.row16_mode = OFF

        else:
            if not self.row16_mode:
                ui.display('No row 16 addressing attachment is needed.')
            else:
                ui.display('Keep the {} attachment ON.'
                           .format(self.row16_mode))

    @property
    def signals(self):
        """Get the signals from the machine"""
        return self.status.get('signals', [])

    def start(self):
        """Simulates the machine start"""
        if self.emergency_stop:
            if ui.confirm('\n**********\nWARNING!!!\n**********\n'
                          '\nEmergency stop is engaged!\n'
                          'It is necessary to clear it before starting.\n'
                          'Answering "no" will abort casting.',
                          default=None, abort_answer=False, allow_abort=False):
                self.emergency_stop = OFF
        # normal starting sequence
        self.update_status(air=ON)
        if not any((self.punch_mode, self.testing_mode)):
            self.update_status(water=ON, motor=ON)
        self.update_status(machine=ON)

    def stop(self):
        """Simulates the machine stop"""
        if not any((self.punch_mode, self.testing_mode)):
            self.update_status(pump=OFF, water=OFF, motor=OFF)
        self.update_status(air=OFF, machine=OFF, testing_mode=OFF)

    def send(self, signals, timeout=None, request_timeout=None):
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
                self.update_status(pump=ON)
                for pos in range(1, 15):
                    if str(pos) in signals:
                        self.update_status(wedge_0075=pos)
                        break
                else:
                    self.update_status(wedge_0075=15)

            elif found(['0005']) or found('NJ'):
                # 0005 without 0075 turns the pump off
                self.update_status(pump=OFF)

            # check 0005 wedge position:
            # find the earliest row number or default to 15
            if found(['0005']) or found('NJ'):
                for pos in range(1, 15):
                    if str(pos) in signals:
                        self.update_status(wedge_0005=pos)
                        break
                else:
                    self.update_status(wedge_0005=15)

        if not self.status.get('machine'):
            raise librpi2caster.InterfaceNotStarted

        start_time = time.time()
        max_wait_time = max(timeout or 0, request_timeout or 0) or 10
        # convert signals based on modes
        converted_signals = parse_signals(signals, self.row16_mode)
        signals_string = ''.join(converted_signals)
        self.status.update(signals=converted_signals)
        try:
            update_wedges_and_pump()
            if self.testing_mode:
                ui.display('Testing signals: {}'.format(signals_string))
            elif self.punch_mode:
                ui.display('punches going up')
                time.sleep(self.config['punching_on_time'])
                ui.display('punches going down')
                time.sleep(self.config['punching_off_time'])
            else:
                ui.display('photocell ON')
                time.sleep(0.5)
                ui.display('photocell OFF')
                time.sleep(0.5)
            if (time.time() - start_time) > max_wait_time:
                raise librpi2caster.MachineStopped
        except (KeyboardInterrupt, EOFError):
            self.emergency_stop = ON

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
        self.send(signals, timeout=timeout, request_timeout=request_timeout)

    def punch_one(self, signals):
        """Punch a single signals combination"""
        off_time = self.config['punching_off_time']
        on_time = self.config['punching_on_time']
        timeout = on_time + off_time + 5
        self.send(signals, request_timeout=timeout)

    def test_one(self, signals):
        """Test a single signals combination"""
        self.testing_mode = True
        self.send(signals, request_timeout=5)

    def cast_or_punch(self, ribbon):
        """Cast / punch a ribbon, based on the selected operation mode."""
        return (self.punch(ribbon) if self.punch_mode
                else self.advanced_cast(ribbon))

    def simple_cast(self, input_sequence, ask=True, repetitions=1):
        """Cast a series of multiple records.
        This is a simplified routine without statistics."""
        source = [parse_record(item) for item in input_sequence]
        # do we need to cast from row 16 and choose an attachment?
        row16_in_use = any((record.uses_row_16 for record in source))
        self.choose_row16_mode(row16_in_use)
        # use caster context to check machine rotation and ensure
        # that no valves stay open after we're done
        with self:
            # cast as many as initially ordered and ask to continue
            while repetitions > 0:
                try:
                    for record in source:
                        found = '{r.signals:<20}{r.comment}'.format(r=record)
                        ui.display(found)
                        self.cast_one(record)
                        signals = self.status.get('signals', [])
                        ui.display('casting: {}'.format(' '.join(signals)))
                    # repetition successful
                    repetitions -= 1
                except librpi2caster.MachineStopped:
                    # repetition failed
                    if ui.confirm('Machine stopped: continue casting?',
                                  abort_answer=False):
                        # restart the machine
                        self.start()
                if ask and not repetitions and ui.confirm('Repeat?'):
                    repetitions += 1

    def advanced_cast(self, input_sequence):
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
        def rewind_if_needed():
            """Decide whether to rewind the ribbon or not.
            If casting and stop comes first, rewind. Otherwise not."""
            nonlocal ribbon
            for record in ribbon:
                if record.is_pump_stop:
                    # rewind
                    ribbon = [x for x in reversed(ribbon)]
                    return
                if record.is_pump_start:
                    # no need to rewind
                    return

        def skip_lines(source):
            """Skip a definite number of lines"""
            # Apply constraints: 0 <= lines_skipped < lines in ribbon
            lines_skipped = stats.run_lines_skipped()
            if lines_skipped:
                ui.display('Skipping {} lines'.format(lines_skipped))
            # Take away combinations until we skip the desired number of lines
            # BEWARE: ribbon starts with galley trip!
            # We must give it back after lines are taken away
            record = parse_record('')
            sequence = deque(source)
            while lines_skipped > 0:
                record = sequence.popleft()
                lines_skipped -= 1 * record.is_newline
            # give the last code back
            sequence.appendleft(record)
            return sequence

        def set_lines_skipped(run=True, session=True):
            """Set the number of lines skipped for run and session
            (in case of multi-session runs)."""
            # allow skipping only if ribbon is more than 2 lines long
            limit = max(0, stats.ribbon_lines() - 2)
            if not limit:
                return
            # how many can we skip?
            if run or session:
                ui.display('We can skip up to {} lines.'.format(limit))

            if run:
                # run lines skipping
                # how many lines were successfully cast?
                lines_done = stats.lines_done()
                if lines_done:
                    ui.display('{} lines were cast in the last run.'
                               .format(lines_done))
                # Ask user how many to skip (default: all successfully cast)
                r_skip = ui.enter('How many lines to skip for THIS run?',
                                  default=lines_done, minimum=0, maximum=limit)
                stats.update(run_line_skip=r_skip)

            if session:
                # Skip lines effective for ALL runs
                # session line skipping affects multi-run sessions only
                # don't do it for single-run sessions
                if stats.runs() > 1:
                    s_skip = ui.enter('How many lines to skip for ALL runs?',
                                      default=0, minimum=0, maximum=limit)
                    stats.update(session_line_skip=s_skip)

        def cast_queue(queue):
            """Casts the sequence of codes in given sequence.
            This function is executed until the sequence is exhausted
            or casting is stopped by machine or user."""
            # in punching mode, lack of row will trigger signal 15,
            # lack of column will trigger signal O
            # in punching and testing mode, signal O or 15 will be present
            # in the output combination as O15
            for record in queue:
                # check if signal will be cast at all
                if not record.has_signals:
                    ui.display_header(record.comment)
                    continue
                # display some info and cast the signals
                stats.update(record=record)
                self.cast_one(record)
                # prepare data for display
                info = OrderedDict()
                info['Signals sent'] = ' '.join(self.status.get('signals', []))
                info['Pump'] = 'ON' if self.status['pump'] else 'OFF'
                info['Wedge 0005 at'] = self.status['wedge_0005']
                info['Wedge 0075 at'] = self.status['wedge_0075']
                info['Speed'] = self.status['speed']
                # display status
                ui.clear()
                ui.display_parameters(stats.code_parameters(), info)

        # Ribbon pre-processing and casting parameters setup
        ribbon = [parse_record(code) for code in input_sequence]
        rewind_if_needed()
        # initialize statistics
        stats.reset()
        stats.update(ribbon=ribbon)
        # display some info for the user
        ui.display_parameters(stats.ribbon_parameters())
        # set the number of casting runs
        stats.update(runs=ui.enter('How many times do you want to cast this?',
                                   default=1, minimum=0))
        # initial line skipping
        set_lines_skipped(run=True, session=True)
        ui.display_parameters(stats.session_parameters())
        # check if the row 16 addressing will be used;
        # connect with the interface
        row16_in_use = any(record.uses_row_16 for record in ribbon)
        self.choose_row16_mode(row16_in_use)
        with self:
            while stats.runs_left():
                # Prepare the ribbon ad hoc
                queue = skip_lines(ribbon)
                stats.update(queue=queue)
                # Cast the run and check if it was successful
                try:
                    cast_queue(queue)
                    stats.update(casting_success=True)
                    if not stats.runs_left():
                        # user might want to re-run this
                        msg = 'Casting successfully finished. Any more runs?'
                        stats.update(runs=ui.enter(msg, default=0, minimum=0))

                except librpi2caster.MachineStopped:
                    stats.update(casting_success=False)
                    ui.display('The composition caster stopped working!\n')
                    # aborted - ask if user wants to continue
                    runs_left = stats.runs_left()
                    if runs_left > 1:
                        ui.confirm('{} runs left, continue?'.format(runs_left),
                                   default=True, abort_answer=False)
                    else:
                        ui.confirm('Do you want to repeat the casting job?',
                                   default=True, abort_answer=False)
                    # offer to skip lines for re-casting the failed run
                    skip_successful = stats.lines_done() >= 2
                    set_lines_skipped(run=skip_successful, session=False)
                    # restart the machine after emergency stop
                    self.start()

    def punch(self, signals_sequence):
        """Punching sequence: valves on - wait - valves off- wait"""
        # do we need to use any row16 addressing attachment?
        source = [parse_record(item) for item in signals_sequence]
        row16_in_use = any(record.uses_row_16 for record in source)
        self.choose_row16_mode(row16_in_use)
        # start punching
        with self:
            for record in source:
                try:
                    ui.display('{r.signals:<20}{r.comment}'.format(r=record))
                    self.punch_one(record.signals)
                    signals = self.status.get('signals', [])
                    ui.display('punching: {}'.format(' '.join(signals)))
                except librpi2caster.MachineStopped:
                    if ui.confirm('Machine stopped - continue?'):
                        self.punch_one(record.signals)
                        signals = self.status.get('signals', [])
                        ui.display('punching: {}'.format(' '.join(signals)))
                    else:
                        break
            else:
                ui.display('All codes successfully punched.')
            ui.pause('Punching finished. Take the ribbon off the tower.')

    def test(self, signals_sequence, duration=None):
        """Testing: advance manually or automatically"""
        source = [parse_record(item) for item in signals_sequence]
        self.testing_mode = True
        with self:
            while True:
                try:
                    pairs = zip(source, [*source[1:], None])
                    for record, next_record in pairs:
                        self.test_one(record.signals)
                        signals = self.status.get('signals', [])
                        ui.display('testing: {}'.format(' '.join(signals)))
                        if duration:
                            time.sleep(duration)
                        elif next_record:
                            ui.pause('Next: {}'.format(next_record.signals),
                                     allow_abort=True)
                except librpi2caster.MachineStopped:
                    ui.display('Testing stopped.')
                if len(signals_sequence) == 1:
                    ui.pause('Sending signals...')
                    break
                else:
                    ui.confirm('Repeat?', abort_answer=False)


class MonotypeCaster(SimulationCaster):
    """Methods common for Caster classes, used for instantiating
    caster driver objects (whether real hardware or mockup for simulation)."""
    def _request(self, path='', method='get', request_timeout=None, **kwargs):
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
            response = requests.request(method, url,
                                        json=data, timeout=request_timeout)
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
            raise librpi2caster.ConfigurationError(msg.format(url))
        except requests.HTTPError as error:
            if response.status_code == 501:
                raise NotImplementedError('{}: feature not supported by server'
                                          .format(url))
            # 400, 404, 503 etc.
            raise librpi2caster.CommunicationError(message=str(error))
        except requests.Timeout:
            msg = 'Connection to {} timed out.'
            raise librpi2caster.CommunicationError(message=msg.format(url))
        except JSONDecodeError:
            msg = 'Connection to {} returned incorrect data (expected: JSON).'
            raise librpi2caster.CommunicationError(message=msg.format(url))
        except requests.ConnectionError:
            msg = 'Error connecting to {}.'
            raise librpi2caster.CommunicationError(message=msg.format(url))

    @handle_communication_error
    def send(self, signals='', timeout=None, request_timeout=None):
        """Send signals to the interface. Wait for an OK response."""
        try:
            codes = parse_signals(signals, self.row16_mode)
            data = dict(signals=codes, timeout=timeout)
            self._request('signals', method='post',
                          request_timeout=request_timeout, **data)
        except librpi2caster.InterfaceNotStarted:
            self.start()
            self._request('signals', method='post',
                          request_timeout=request_timeout, **data)
        except KeyboardInterrupt:
            self.emergency_stop = ON
            raise librpi2caster.MachineStopped
        except (EOFError, librpi2caster.CommunicationError):
            self.stop()
            raise librpi2caster.MachineStopped
        self.update_status()

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

        try:
            if self.emergency_stop and ui.confirm(
                    '\n**********\nWARNING!!!\n**********\n'
                    '\nEmergency stop is engaged!\n'
                    'It is necessary to clear it before starting.\n'
                    'Answering "no" will abort casting.',
                    default=None, abort_answer=False, allow_abort=False):
                self.emergency_stop = OFF

            if self.testing_mode:
                request_timeout = 5
            elif self.punch_mode:
                ui.pause('Waiting for you to start punching...')
                request_timeout = 5
            else:
                info = ('Starting the composition caster now...\n\n'
                        'Turn on the motor if needed, and engage the clutch.\n'
                        'When the machine is turning, casting will begin.\n'
                        '\n\nCommence casting? (N = abort)')
                if ui.confirm(info, abort_answer=False, default=True):
                    ui.display('\nWait for a few turns of the cam shaft...\n')
                request_timeout = 3 * self.config['startup_timeout'] + 2
            # send the request and handle any exceptions
            try:
                self._request('machine', method='put',
                              request_timeout=request_timeout)
                if not self.punch_mode and not self.testing_mode:
                    ui.display('\nOK, the machine is running...\n')
            except librpi2caster.InterfaceBusy:
                if ui.confirm('\nThis interface is already busy.\n'
                              'If this is not the case, answer YES to '
                              'stop and reset it. Otherwise abort.\n',
                              abort_answer=False, default=None):
                    self.stop()
                    self.start()
            except KeyboardInterrupt:
                self.emergency_stop = ON
                self.start()
        except librpi2caster.MachineStopped:
            ui.display('\nThe machine was stopped because it was stalling,\n'
                       'or because emergency stop button was pressed.\n')
            self.start()
        finally:
            self.update_status()

    @handle_communication_error
    def stop(self):
        """Machine stop sequence.
        The interface driver checks if the pump is active
        and turns it off if necessary.

        In the casting mode, the driver will turn off the motor
        and cut off the cooling water supply.
        Then, the air supply is cut off.
        """
        try:
            if self.testing_mode or self.punch_mode:
                request_timeout = 3
            else:
                ui.display('Turning the machine off...')
                request_timeout = self.config['pump_stop_timeout'] * 2 + 2
            try:
                self._request('machine', method='delete',
                              request_timeout=request_timeout)
            except KeyboardInterrupt:
                self.emergency_stop = ON
        except librpi2caster.MachineStopped:
            self.stop()
        finally:
            self.update_status()

    @property
    def emergency_stop(self):
        """Check the emergency stop state"""
        self.update_status()
        return self.status.get('emergency_stop')

    @emergency_stop.setter
    @handle_communication_error
    def emergency_stop(self, state):
        """Activate or reset the emergency stop on the machine"""
        method = 'put' if state else 'delete'
        if state:
            ui.display('\n**********\nWARNING!!!\n**********\n'
                       'Emergency stop - stopping the machine NOW.\n\n'
                       'Turn the machine by hand a few times.\n')
        try:
            # will raise MachineStopped
            self._request('emergency_stop', method=method,
                          request_timeout=(120, 120))
        finally:
            self.update_status()

    @handle_communication_error
    def update_status(self, **kwargs):
        """Send the new (optional) parameters to the interface server.
        Update the local status afterwards."""
        status = self._request(method='post', request_timeout=(3, 3), **kwargs)
        self.status.update(status)

    @handle_communication_error
    def update_config(self, **kwargs):
        """Send the new (optional) parameters to the interface server.
        Update the local configuration afterwards."""
        config = self._request('config', method='post',
                               request_timeout=(3, 3), **kwargs)
        self.config.update(config)
