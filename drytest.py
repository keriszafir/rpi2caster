#!/usr/bin/python
import rpi2caster


rpi2caster.DebugMode = True


database = rpi2caster.Database()
caster = rpi2caster.MonotypeSimulation()
userInterface = rpi2caster.TextUserInterface(caster)


with database, caster, userInterface:
  userInterface.consoleUI()
