#!/usr/bin/python
import rpi2caster


rpi2caster.DebugMode = True


database = rpi2caster.Database('database/monotype.db')
caster = rpi2caster.Monotype('mkart-cc', database)
userInterface = rpi2caster.TextUserInterface(caster)


with database, caster, userInterface:
  userInterface.consoleUI()
