#!/usr/bin/env python3
"""Cast

Used for casting actual type.
"""
from rpi2caster import casting, monotype
# C - caster, J - job (casting)
C = monotype.Monotype()
J = casting.Casting()
# set up a caster for this job
J.caster = C
casting.main_menu(J)
