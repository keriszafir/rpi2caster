#!/usr/bin/python
import rpi2caster
import userinterfaces
import database
import simulation

session = rpi2caster.Session(
                             job=rpi2caster.Casting(),
                             db=database.Database('database/monotype.db'),
                             UI=userinterfaces.TextUI(debug_mode=True),
                             caster=simulation.Monotype()
                            )
