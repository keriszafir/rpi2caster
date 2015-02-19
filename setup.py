#!/usr/bin/python
import rpi2caster

job = rpi2caster.Inventory()
job.database = rpi2caster.Database(job, 'database/monotype.db')
job.UI = rpi2caster.TextUI(job)


with job:
  job.main_menu()