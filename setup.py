#!/usr/bin/python
import rpi2caster

#DebugMode = True

database = rpi2caster.Database('database/monotype.db')
caster = rpi2caster.MonotypeSimulation()
actions = rpi2caster.Actions(caster)
userInterface = rpi2caster.TextUserInterface(database, caster, actions)
setup = rpi2caster.MonotypeConfiguration(database, userInterface)


with database, caster, actions, userInterface, setup:
  setup.main_menu()
