#!/usr/bin/python
import os
import sys
from rpi2caster import CasterConfig

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

def add_caster(serialNumber='', casterName='', casterType='',
               justification='', diecaseFormat='', interfaceID=''):
  """Add a caster. The function will pass at least twice - until all data is entered correctly"""
  """Reset revalidation"""
  revalidate = False

  """Check if the serial No is numeric - we must ensure that the value in db is integer"""
  if serialNumber.isdigit():
    serialNumber = int(serialNumber)
  else:
    serialNumber = raw_input('Enter the serial number of your caster, digits only: ')
    revalidate += 1

  """Enter a string for machine name"""
  if not casterName:
    casterName = raw_input('Enter the name you use for this machine: ')
    revalidate += 1

  """Choose the machine type - and validate the choice. Case insensitive; value stored in db as uppercase"""
  if casterType not in ['CC', 'LC', 'K']:
    casterType = raw_input('What type is the machine? CC = composition caster, LC = type & rule / large comp. caster, K = keyboard: ').upper()
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




  if not revalidate:
    print('Caster serial number: %i \n' % serialNumber)
    print('Caster name: %s \n' % casterName)
    print('Caster type: %s \n' % casterType)
    print('Justification mode: %s \n' % justification)
    print('Diecase format: %s \n' % diecaseFormat)
    print('Interface ID for this caster: %i \n' % interfaceID)

    ans = raw_input('\nCommit? [y/n]')

    if ans.lower() == 'y':
      config.add_caster(serialNumber, casterName, casterType,
      justification, diecaseFormat, interfaceID)
      menu()

    elif ans.lower() == 'n':
      add_caster()

  else:
    add_caster(serialNumber, casterName, casterType, justification,
               diecaseFormat, interfaceID)


def add_interface(interfaceID='', interfaceName='', emergencyGPIO='',
        photocellGPIO='', mcp0Address='', mcp1Address='', pinBase=''):

  """Check if the serial No is numeric - we must ensure that the value in db is integer"""
  if interfaceID.isdigit() and int(interfaceID) >= 0:
    interfaceID = int(interfaceID)
  else:
    serialNumber = raw_input('Enter the interface ID, positive number: ')
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
    print('Interface ID: %i \n' % interfaceID)
    print('Interface name: %s \n' % interfaceName)
    print('Emergency GPIO: %i \n' % emergencyGPIO)
    print('Photocell GPIO: %i \n' % photocellGPIO)
    print('MCP0 Address: %s \n' % mcp0Address)
    print('MCP1 Address: %s \n' % mcp1Address)
    print('Pin base: %i \n' % pinBase)

    ans = raw_input('\nCommit? [y/n]')

    if ans.lower() == 'y':
      CasterConfig.add_interface(interfaceID, interfaceName, emergencyGPIO,
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
  """Used for deleting a caster from database"""
  """TODO!"""
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

    elif ans=='0':
      exit()
    else:
      print('\nNo such option. Choose again.')
      ans = ''


config = CasterConfig()
menu()