#!/usr/bin/python
import rpi2caster


job = rpi2caster.Casting()
job.database = rpi2caster.Database(job)
job.UI = rpi2caster.TextUI(job)
job.caster = rpi2caster.MonotypeSimulation(job)


with job:
  job.main_menu()
