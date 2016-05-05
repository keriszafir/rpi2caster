# -*- coding: utf-8 -*-
"""Parallel port input and output driver"""

from parallel import Parallel


class ParallelOutputDriver(object):
    """Output driver for parallel port. Sends four bytes in sequence:
    byte0: O N M L K J I H
    byte1: G F S E D 0075 C B
    byte2: A 1 2 3 4 5 6 7
    byte3: 8 9 10 11 12 13 14 0005
    byte4: 0xFF - control byte
    """

    def __init__(self):
        port = Parallel()
