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

if __name__ == '__main__':
    rpi2caster.main()
