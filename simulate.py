#!/usr/bin/env python
"""Simulate

Casting simulation without an actual caster, for development/testing.
Uses a mockup caster class - simulation.Monotype.
"""
from rpi2caster import casting, simulation
# C - caster, J - job (casting)
C = simulation.Monotype()
J = casting.Casting()
# set up a caster for this job
J.caster = C
casting.main_menu(J)
