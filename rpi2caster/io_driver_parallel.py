# -*- coding: utf-8 -*-
"""Parallel port input and output driver"""
import time
from parallel import Parallel
from . import exceptions as e
from .monotype import SensorBase, OutputBase
from .misc import weakref_singleton
from .global_config import Config
from .ui import UIFactory

UI = UIFactory()
CFG = Config()


@weakref_singleton
class ParallelInterface(SensorBase, OutputBase):
    """Output driver for parallel port. Sends four bytes in sequence:
    byte0: O N M L K J I H
    byte1: G F S E D 0075 C B
    byte2: A 1 2 3 4 5 6 7
    byte3: 8 9 10 11 12 13 14 0005
    """
    working = False
    # port will be lazily instantiated when entering context
    port = None
    name = 'Symbiosys parallel port interface'
    numbers = (2 ** x for x in range(31, -1, -1))
    mapping = dict(zip(CFG.get_option('signals_arrangement'), numbers))

    def __enter__(self):
        if not self.lock:
            self.lock = True
            self.port = self.port or Parallel()
            if not self.working:
                # Check for working to avoid re-initialization
                self._init_on()
                self._init_off()
                UI.display('\nPress the button on the interface...')
                self._wait_until_not_busy()
                self.working = True

    def __exit__(self, *_, **__):
        self.lock = False
        # Release the parallel port
        self.port = None

    def valves_on(self, signals_list=None):
        """Activate the valves"""
        if signals_list:
            mapping = ParallelInterface.mapping
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
        UI.display('%s %s %s %s' % (format(byte0, 'b').zfill(8),
                                    format(byte1, 'b').zfill(8),
                                    format(byte2, 'b').zfill(8),
                                    format(byte3, 'b').zfill(8)),
                   min_verbosity=3)
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

    def check_if_machine_is_working(self, exception=e.ReturnToMenu):
        """Reset the interface if needed and go on"""
        try:
            UI.pause('Turn on the machine...')
        except KeyboardInterrupt:
            raise exception

    def wait_for(self, *args, **kw):
        """Do nothing"""
        pass
