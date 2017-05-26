# -*- coding: utf-8 -*-
"""
    rpi2caster is a CAT (computer-aided typesetting) software
    for the Monotype composition caster (a hot-metal typesetting machine).

    This project uses a control interface for 31/32 solenoid valves
    and a machine cycle sensor. It can control a casting machine
    or a pneumatic paper tape perforator from the Monotype keyboard.

    The rpi2caster package consists of three main utilities:
        * machine control,
        * typesetting,
        * inventory management.

    Machine control utility also serves as a diagnostic program
    for calibrating and testing the machine and control interface.

    For usage info, run `rpi2caster --help`

"""

from .rpi2caster import main

MODULES = ['basic_models', 'basic_controllers', 'casting_models', 'config',
           'data', 'datatypes', 'definitions', 'main_models',
           'matrix_controller', 'misc', 'monotype', 'parsing', 'rpi2caster',
           'typesetting', 'typesetting_funcs', 'ui', 'utilities']

__all__ = MODULES

__version__ = '0.7.dev1'

__author__ = 'Krzysztof Słychań'


if __name__ == '__main__':
    main()
