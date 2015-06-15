#!/usr/bin/env python3
"""debug-cast

Used for casting actual type, but in debugging mode.
"""
from rpi2caster import casting, monotype
monotype.ui.DEBUG_MODE = True
# C - caster, J - job (casting)
C = monotype.Monotype()
J = casting.Casting()
# set up a caster for this job
J.caster = C
casting.main_menu(J)
