#!/usr/bin/python
import rpi2caster
import userinterfaces
import database

session = rpi2caster.Session(
                             job=rpi2caster.Casting(),
                             db=database.Database('database/monotype.db'),
                             UI=userinterfaces.TextUI(debugMode=True),
                             caster=rpi2caster.MonotypeSimulation()
                            )
