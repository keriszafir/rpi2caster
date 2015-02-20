#!/usr/bin/python
import rpi2caster

print 'Initializing job...'
job = rpi2caster.Casting()
print 'Initializing database...'
database = rpi2caster.Database(job)
print 'Initializing UI...'
UI = rpi2caster.TextUI(job)

# This is for now needed for initializing caster
job.UI = UI

print 'Initializing caster...'
caster = rpi2caster.Monotype(job, 'mkart-cc')

print('Objects initialized.')

name = {job : 'job', database : 'database', caster : 'caster', UI : 'user interface'}


for object in name:
  for dependency in name:
    if (dependency != object):
      print 'Setting', name[dependency], 'for', name[object], '...'
      object.dependency = dependency
      print name[object], '-', name[dependency], 'is of type:', type(object.dependency)
