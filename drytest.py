#!/usr/bin/python
import rpi2caster

session = rpi2caster.Session(
                             database=rpi2caster.Database('database/monotype.db'),
                             UI=rpi2caster.TextUI(debugMode=True),
                             caster=rpi2caster.MonotypeSimulation()
                            )