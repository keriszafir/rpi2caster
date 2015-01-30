#!/usr/bin/python
import rpi2caster


rpi2caster.DebugMode = True


database = rpi2caster.Database('database/monotype.db')
caster = rpi2caster.Monotype('mkart-cc', database)
actions = rpi2caster.Actions(caster)
userInterface = rpi2caster.TextUserInterface(actions)


with database, caster, actions, userInterface:
  userInterface.consoleUI()