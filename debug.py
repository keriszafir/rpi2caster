#!/usr/bin/python
import rpi2caster

global DebugMode
DebugMode = True


database = rpi2caster.Database('database/monotype.db')
caster = rpi2caster.Monotype('mkart-cc', database)
actions = rpi2caster.Actions(caster)
userInterface = rpi2caster.TextUserInterface(database, caster, actions)


with database, caster, actions, userInterface:
  userInterface.consoleUI()