#!/usr/bin/python
from rpi2caster import CasterConfig

try:
  import sqlite3
except ImportError:
    print('You must install sqlite3 database and python-sqlite2 package.')
    exit()
finally:
  pass

def add_caster(revalidate=False):
  """Add a caster. The function will pass at least twice - until all data is entered correctly"""
  if not revalidate:
    """Will occur at first time the function is called"""
    serialNumber = ''
    machineName = ''
    machineType = ''
    justification = ''
    diecaseFormat = ''
    interfaceID = ''
  
  """Check if the serial No is numeric - we must ensure that the value in db is integer"""
  if serialNumber.isdigit():
    serialNumber = int(serialNumber)
  else:
    serialNumber = raw_input('Enter the serial number of your caster, digits only: ')
    revalidate += 1

  """Enter a string for machine name"""
  if not machineName:
    machineName = raw_input('Enter the name you use for this machine: ')
    revalidate += 1

  """Choose the machine type - and validate the choice. Case insensitive; value stored in db as uppercase"""
  if machineType not in ['CC', 'LC', 'K']:
    machineType = raw_input('What type is the machine? CC = composition caster, LC = type & rule / large comp. caster, K = keyboard: ').upper()
    revalidate += 1

  """Choose the justification mode the machine is using, and validate the choice"""
  if justification not in ('norm', 'alt'):
    justification = raw_input('Justification mode: norm = 0005, 0075; alt = NJ, NK: ')
    revalidate += 1

  """Choose the diecase format the machine is using, and validate the choice"""
  if diecaseFormat not in ['norm15', 'norm17', 'hmn', 'kmn', 'shift']:
    diecaseFormat = raw_input('Diecase format this machine works with: norm15 = 15x15, norm17 = 15x17, hmn, kmn, shift = unit-shift: ')
    revalidate += 1

  """Choose the interface ID"""
  if interfaceID.isdigit():
    interfaceID = int(interfaceID)
  else:
    interfaceID = raw_input('Raspberry interface number for this machine. Usually 0: ')
    if interfaceID == '':
      interfaceID = '0'
    revalidate += 1
  
  if revalidate:
    add_caster(True)
  else:
    CasterConfig.add_caster(serialNumber, machineName, machineType, justification, diecaseFormat, interfaceID)

config = CasterConfig()

def list_casters():
  config.list_casters()

def list_interfaces():
  config.list_interfaces()

list_casters()
list_interfaces()
