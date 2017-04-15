# -*- coding: utf-8 -*-
"""rpi2caster:
-- specialized typesetting and machine control software
for Monotype composition casting machines."""

from . import basic_models, basic_controllers, casting, casting_models, config
from . import datatypes, definitions, documentation, easteregg
from . import matrix_controller, misc, database_models, monotype
from . import parsing, rpi2caster, typesetting, typesetting_funcs, ui

__all__ = [basic_models, basic_controllers, casting, casting_models, config,
           datatypes, definitions, documentation, easteregg,
           matrix_controller, misc, database_models, monotype,
           parsing, rpi2caster, typesetting, typesetting_funcs, ui]


__version__ = '0.7.dev1'

if __name__ == '__main__':
    rpi2caster.main()
