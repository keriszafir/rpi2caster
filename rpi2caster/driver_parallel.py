# -*- coding: utf-8 -*-
"""Parallel port input and output driver"""
import time
from parallel import Parallel
from .monotype import SimulationSensor, SimulationOutput
from .global_config import UI, SIGNALS_ARRANGEMENT
from .helpers import singleton


@singleton
class ParallelOutputDriver(SimulationOutput):
    """Output driver for parallel port. Sends four bytes in sequence:
    byte0: O N M L K J I H
    byte1: G F S E D 0075 C B
    byte2: A 1 2 3 4 5 6 7
    byte3: 8 9 10 11 12 13 14 0005
    """
    numbers = (2 ** x for x in range(31, -1, -1))
    mapping = dict(zip(SIGNALS_ARRANGEMENT, numbers))

    def __init__(self):
        super().__init__()
        self.name = 'Symbiosys parallel port interface'
        self.working = False
        self.port = None
        self.lock = False

    def __enter__(self):
        if not self.lock:
            try:
                self.lock = True
                self.port = self.port or Parallel()
                if not self.working:
                    # Check for working to avoid re-initialization
                    self._init_on()
                    self._init_off()
                    UI.display('\nPress the button on the interface...')
                    self._wait_until_not_busy()
                    self.working = True
                return self
            except (FileNotFoundError, IOError, OSError):
                UI.pause('ERROR: Cannot access the parallel port!\n'
                         'Check your hardware and OS configuration...\n'
                         'Simulating casting instead.')
                return SimulationOutput()

    def __exit__(self, *_, **__):
        self.lock = False
        # Release the parallel port
        self.port = None

    def valves_on(self, signals_list=None):
        """Activate the valves"""
        if signals_list:
            mapping = ParallelOutputDriver.mapping
            number = sum(mapping.get(signal, 0) for signal in signals_list)
            # Split it to four bytes sent in sequence
            byte0 = (number >> 24) & 0xff
            byte1 = (number >> 16) & 0xff
            byte2 = (number >> 8) & 0xff
            byte3 = number & 0xff
        else:
            # Turn off the valves
            byte0 = byte1 = byte2 = byte3 = 0x00
        # Display debug information about the bytes
        UI.debug_info('%s %s %s %s' % (format(byte0, 'b').zfill(8),
                                       format(byte1, 'b').zfill(8),
                                       format(byte2, 'b').zfill(8),
                                       format(byte3, 'b').zfill(8)))
        for byte in (byte0, byte1, byte2, byte3):
            self._send(byte)

    def valves_off(self):
        """Deactivate the valves - actually, do nothing"""
        pass

    def _send(self, data):
        """Send the codes through the data port"""
        # Wait until we can send the codes
        self._wait_until_not_busy()
        self._set_data(data)
        # Signal that we finished and wait until interface acknowledges
        self._strobe_on()
        self._wait_until_busy()
        self._strobe_off()
        self._wait_until_not_busy()

    def _set_data(self, data):
        "Set the lines on the data port"""
        if self.port:
            self.port.setData(data)

    def _wait_until_busy(self):
        """Wait until busy goes ON"""
        if self.port:
            while self.port.getInBusy():
                pass

    def _wait_until_not_busy(self):
        """Wait until busy goes OFF"""
        if self.port:
            while not self.port.getInBusy():
                pass

    def _strobe_on(self):
        """Send the strobe signal"""
        # Negative logic!
        if self.port:
            self.port.setDataStrobe(False)
            # 5us sleep
            time.sleep(0.000005)

    def _strobe_off(self):
        """Send the strobe signal"""
        # Negative logic!
        if self.port:
            self.port.setDataStrobe(True)

    def _init_on(self):
        """Sends the init signal"""
        # Negative logic!
        if self.port:
            self.port.setInitOut(False)

    def _init_off(self):
        """Sends the init signal"""
        # Negative logic!
        if self.port:
            self.port.setInitOut(True)


@singleton
class ParallelSensor(SimulationSensor):
    """Parallel port sensor driver"""
    def __init__(self):
        super().__init__()
        self.name = 'Symbiosys parallel port interface'

    def check_if_machine_is_working(self):
        """Reset the interface if needed and go on"""
        UI.pause('Turn on the machine... (or ctrl-C to abort)')

    def wait_for(self, *args, **kw):
        """Do nothing"""
        pass
