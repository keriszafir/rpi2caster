#!/usr/bin/env python
from rpi2caster import casting
from rpi2caster import simulation
caster = simulation.Monotype()
job = casting.Casting()
job.caster = caster
job.main_menu()
