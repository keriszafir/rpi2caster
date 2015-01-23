#!/usr/bin/python
import os
import sys
import json
from rpi2caster import DatabaseBackend

try:
  import sqlite3
except ImportError:
    print('You must install sqlite3 database and python-sqlite2 package.')
    exit()
finally:
  pass

def is_hex(s):
  try:
    int(s, 16)
    return True
  except ValueError:
    return False

def conv_hex(s):
  n = int(s, 16)
  return hex(n)

def add_caster(casterSerial='', casterName='', casterType='',
               unitAdding='', diecaseSystem='', interfaceID=''):
  """Add a caster. The function will pass at least twice -
  until all data is entered correctly"""

  """Reset revalidation; if everything is OK, the data can be written
  to the database. Else, the add_caster function will recurse into itself
  with entered data as arguments. The user will have to re-enter
  any parameter which does not match the expected values or type."""
  revalidate = False

  """Check if the serial No is numeric - we must ensure
  that the value in db is integer"""
  if str(casterSerial).isdigit():
    casterSerial = int(casterSerial)
  else:
    casterSerial = raw_input('Enter the serial number of your caster: ')
    revalidate = True

  """Enter a string for machine name"""
  if not casterName:
    casterName = raw_input('Enter the name you use for this machine: ')
    revalidate = True

  """Choose the machine type - and validate the choice. Case insensitive; value stored in db as uppercase"""
  if casterType not in ['comp', 'large_comp']:
    casterType = raw_input('What type is the machine? 1 = composition caster, 2 = type & rule / large comp. caster: ')
    if casterType == '1':
      casterType = 'comp'
    elif casterType == '2':
      casterType = 'large_comp'
    else:
      casterType = ''
    revalidate = True

  """Choose if the machine has unit adding or not"""
  if unitAdding not in (True, False):
    unitAdding = raw_input('Does the caster use unit adding attachment? 1 - yes, 0 - no: ')
    if unitAdding == '0':
      unitAdding = False
    elif unitAdding == '1':
      unitAdding = True
    else:
      unitAdding = ''
    revalidate = True

  """Choose the diecase format the machine is using, and validate the choice"""
  dcsystems = ['norm15', 'norm17', 'hmn', 'kmn', 'shift']
  if diecaseSystem not in dcsystems:
    diecaseSystem = raw_input('Diecase format this machine works with: 0 for 15x15, 1 for 15x17, 2 for HMN, 3 for KMN, 4 for unit-shift. \nDefault is 15x17: ')
    if diecaseSystem == '0':
      diecaseSystem = dcsystems[0]
    elif diecaseSystem == '1':
      diecaseSystem = dcsystems[1]
    elif diecaseSystem == '2':
      diecaseSystem = dcsystems[2]
    elif diecaseSystem == '3':
      diecaseSystem = dcsystems[3]
    elif diecaseSystem == '4':
      diecaseSystem = dcsystems[4]
    else:
      diecaseSystem = dcsystems[1]
    revalidate = True

  """Choose the interface ID"""
  if str(interfaceID).isdigit() and int(interfaceID) in range(4):
    interfaceID = int(interfaceID)
  else:
    interfaceID = raw_input('Raspberry interface number for this machine. Can be 0, 1, 2, 3. Default 0: ')
    if interfaceID == '':
      interfaceID = '0'
    revalidate = True

  """Now we can list entered data and ask for user's confirmation:"""
  if not revalidate:
    print('Caster serial number: %i \n' % casterSerial)
    print('Caster name: %s \n' % casterName)
    print('Caster type: %s \n' % casterType)
    print('Unit adding: %s \n' % str(unitAdding))
    print('Diecase system: %s \n' % diecaseSystem)
    print('Interface ID for this caster: %i \n' % interfaceID)

    ans = raw_input('\nCommit? [y/n]')

    if ans.lower() == 'y':
      config.add_caster(
        casterSerial, casterName, casterType,
        unitAdding, diecaseSystem, interfaceID
        )
      menu()

    elif ans.lower() == 'n':
      """Add caster again"""
      add_caster()

  else:
    """Recursively call this function to revalidate parameters:"""
    add_caster(
      casterSerial, casterName, casterType,
      unitAdding, diecaseSystem, interfaceID
      )


def add_interface(ID='', interfaceName='', emergencyGPIO='',
        photocellGPIO='', mcp0Address='', mcp1Address='', pinBase=''):

  """Check if the serial No is numeric - we must ensure that the value in db is integer"""
  if ID.isdigit() and int(ID) in range(4):
    ID = int(ID)
  else:
    ID = raw_input('Enter the interface ID: 0, 1, 2, 3, 4; default 0: ')
    if ID == '':
      ID = 0
    revalidate += 1

  """Enter a string for interface name"""
  if not interfaceName:
    interfaceName = raw_input('Enter the name you use for this interface: ')
    revalidate += 1

  """Emergency button GPIO for this interface"""
  if emergencyGPIO.isdigit() and int(emergencyGPIO) > 3:
    emergencyGPIO = int(emergencyGPIO)
  else:
    emergencyGPIO = raw_input('Enter the emergency button GPIO - BCM number: ')
    revalidate += 1

  """Photocell GPIO for this interface"""
  if photocellGPIO.isdigit() and int(photocellGPIO) > 3 and photocellGPIO != emergencyGPIO:
    photocellGPIO = int(photocellGPIO)
  else:
    emergencyGPIO = raw_input('Enter the photocell GPIO - BCM number: ')
    revalidate += 1

  """First MCP23017 address for this interface, typically 0x20:"""
  if is_hex(mcp0Address):
    mcp0Address = conv_hex(mcp0Address)
  else:
    mcp0Address = raw_input('Enter the first MCP23017 I2C address - hex, typically 20: ')
    revalidate += 1

  """Second MCP23017 address for this interface, typically 0x21:"""
  if is_hex(mcp0Address):
    mcp0Address = conv_hex(mcp0Address)
  else:
    mcp0Address = raw_input('Enter the second MCP23017 I2C address - hex, typically 21: ')
    revalidate += 1

  """Pin base for GPIOs on MCP23017. Typically 65 for first interface,
  97 for second, 129 for third. 0 to 64 are RESERVED, we can't use them!"""
  if pinBase.isdigit() and int(pinBase) > 64:
    pinBase = int(pinBase)
  else:
    pinBase = raw_input('Enter the photocell GPIO - BCM number: ')
    revalidate += 1


  if not revalidate:
    print('Interface ID: %i \n' % ID)
    print('Interface name: %s \n' % interfaceName)
    print('Emergency GPIO: %i \n' % emergencyGPIO)
    print('Photocell GPIO: %i \n' % photocellGPIO)
    print('MCP0 Address: %s \n' % mcp0Address)
    print('MCP1 Address: %s \n' % mcp1Address)
    print('Pin base: %i \n' % pinBase)

    ans = raw_input('\nCommit? [y/n]')

    if ans.lower() == 'y':
      CasterConfig.add_interface(ID, interfaceName, emergencyGPIO,
      photocellGPIO, mcp0Address, mcp1Address, pinBase)
      menu()
    elif ans.lower() == 'n':
      add_caster(False)
  else:
    add_interface(interfaceID, interfaceName, emergencyGPIO, photocellGPIO,
    mcp0Address, mcp1Address, pinBase)


def add_wedge():
  """Used for adding wedges"""
  """TODO!"""
  menu()


def delete_caster():
  ID = raw_input('Enter the caster ID to delete: ')
  if ID.isdigit():
    config.delete_caster(int(ID))
  menu()

def delete_interface():
  """Used for deleting an interface from database"""
  """TODO!"""
  menu()

def delete_wedge():
  """Used for deleting a wedge from database"""
  """TODO!"""
  menu()


def list_casters():
  """lists all casters we have in database"""
  config.list_casters()

def list_interfaces():
  """lists all available interfaces"""
  config.list_interfaces()

def list_wedges():
  """lists all wedges we have"""
  config.list_wedges()


def menu():
  """Main menu. On entering, clear the screen and turn any valves off."""
  os.system('clear')
  print('Setup program for rpi2caster\n')
  ans = ''
  while ans == '':
    print ("""
\t Main menu:

\t 1. List casters
\t 2. Add caster
\t 3. Delete caster

\t 4. List interfaces
\t 5. Add interface
\t 6. Delete interface

\t 7. List wedges
\t 8. Add wedge
\t 9. Delete wedge

\t 10. Add a comp. caster no 28539, name 'mkart-cc', unit adding off, norm17 diecase

\t 0. Exit to shell

""")

    ans = raw_input('Choose an option: ')
    if ans=='1':
      list_casters()
      raw_input('\nPress return to go back to menu.\n')
      menu()
    elif ans=='2':
      add_caster()
      raw_input('\nPress return to go back to menu.\n')
      menu()
    elif ans=='3':
      delete_caster()
      raw_input('\nPress return to go back to menu.\n')
      menu()
    elif ans=='4':
      list_interfaces()
      raw_input('\nPress return to go back to menu.\n')
      menu()
    elif ans=='5':
      add_interface()
      raw_input('\nPress return to go back to menu.\n')
      menu()
    elif ans=='6':
      delete_interface()
      raw_input('\nPress return to go back to menu.\n')
      menu()
    elif ans=='7':
      list_wedges()
      raw_input('\nPress return to go back to menu.\n')
      menu()
    elif ans=='8':
      add_wedge()
      raw_input('\nPress return to go back to menu.\n')
      menu()
    elif ans=='9':
      delete_wedge()
      raw_input('\nPress return to go back to menu.\n')
      menu()
    elif ans=='10':
      add_caster(28539, 'mkart-cc', 'comp', False, 'norm17', 0)
      raw_input('\nCaster added. Press return to go back to menu.\n')
      menu()

    elif ans=='0':
      exit()
    else:
      print('\nNo such option. Choose again.')
      ans = ''


config = DatabaseBackend()
menu()