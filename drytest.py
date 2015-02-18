#!/usr/bin/python
import rpi2caster


job = rpi2caster.Casting()
job.database = rpi2caster.Database(job)
job.caster = rpi2caster.MonotypeSimulation(job)
job.userInterface = rpi2caster.TextUserInterface(job)

with job:
  job.userInterface.consoleUI()
