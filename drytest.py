#!/usr/bin/python
import rpi2caster
import casting
import text_ui as ui
import database
import simulation

session = rpi2caster.Session(
                             job=casting.Casting(),
                             db=database.Database('database/monotype.db'),
                             caster=simulation.Monotype()
                            )
