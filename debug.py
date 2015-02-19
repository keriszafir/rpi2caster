#!/usr/bin/python
import rpi2caster


job = rpi2caster.Casting()
job.debugMode = True
job.database = rpi2caster.Database(job, 'database/monotype.db')
job.caster = rpi2caster.Monotype(job, 'mkart-cc')
job.UI = rpi2caster.TextUI(job)

with job:
  job.main_menu()
