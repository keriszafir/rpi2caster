#!/usr/bin/python
import rpi2caster

job = rpi2caster.Inventory()
job.database = rpi2caster.Database(job, 'database/monotype.db')
job.userInterface = rpi2caster.TextUserInterface(job)


with job:
  job.main_menu()
