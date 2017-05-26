# -*- coding: utf-8 -*-
"""rpi2caster:
-- specialized typesetting and machine control software
for Monotype composition casting machines."""

from . import misc
from . import config
from . import data
from . import datatypes
from . import definitions
from . import ui
from . import parsing
from . import typesetting_funcs
from . import basic_models
from . import casting_models
from . import main_models
from . import basic_controllers
from . import matrix_controller
from . import typesetting
from . import monotype
from . import utilities
from . import rpi2caster

__all__ = [basic_models, basic_controllers, casting_models, config, data,
           datatypes, definitions, main_models, matrix_controller, misc,
           monotype, parsing, rpi2caster, typesetting, typesetting_funcs, ui,
           utilities]


__version__ = '0.7.dev1'

__author__ = 'Krzysztof Słychań'

__doc__ = """
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


if __name__ == '__main__':
    rpi2caster.main()
