#!/usr/bin/python
import ConfigParser

def get_interface_settings(interfaceID=0):
  """get_interface_settings(interfaceID):

  Reads a configuration file and gets interface parameters.

  If the config file is correct, it returns a list:
  [emergencyGPIO, photocellGPIO, mcp0Address, mcp1Address, pinBase]

  emergencyGPIO - BCM number for emergency stop button GPIO
  photocellGPIO - BCM number for photocell GPIO
  mcp0Address   - I2C address for 1st MCP23017
  mcp1Address   - I2C address for 2nd MCP23017
  pinBase       - pin numbering base for GPIO outputs on MCP23017

  Multiple interfaces attached to a single Raspberry Pi:

  It's possible to use up to four interfaces (i.e. 2xMCP23017, 4xULN2803)
  for a single Raspberry. It can be used for operating multiple casters,
  or a caster and a keyboard's paper tower, simultaneously (without
  detaching a valve block from the paper tower and moving it elsewhere).

  These interfaces should be identified by numbers: 0, 1, 2, 3.

  Each of the MCP23017 chips has to have unique I2C addresses. They are
  set by pulling the A0, A1, A2 pins up (to 3.3V) or down (to GND).
  There are 2^3 = 8 possible addresses, and an interface uses two chips,
  so you can use up to four interfaces.

  It's best to order the MCP23017 chips' addresses ascending, i.e.

  interfaceID    mcp0 pin    mcp1 pin    mcp0     mcp1
                 A2,A1,A0    A2,A1,A0    addr     addr

  0              000         001         0x20     0x21
  1              010         011         0x22     0x23
  2              100         101         0x24     0x25
  3              110         111         0x26     0x27

  where 0 means the pin is pulled down, and 1 means pin pulled up.

  As for pinBase parameter, it's the wiringPi's way of identifying GPIOs
  on MCP23017 extenders. WiringPi is an abstraction layer which allows
  you to control (read/write) pins on MCP23017 just like you do it on
  typical Raspberry Pi's GPIO pins. Thus you don't have to send bytes
  to registers.
  The initial 64 GPIO numbers are reserved for Broadcom SoC, so the lowest
  pin base you can use is 65. Each interface (2xMCP23017) uses 32 pins.

  If you are using multiple interfaces per Raspberry, you SHOULD
  assign the following pin bases to each interface:

  interfaceID    pinBase

  0              65
  1              98          (pinBase0 + 32)
  2              131         (pinBase1 + 32)
  3              164         (pinBase2 + 32)

  """
  interfaceName = 'Interface' + str(interfaceID)
  config = ConfigParser.SafeConfigParser()
  config.read('/etc/rpi2caster.conf')
  try:
    """Check if the interface is active, else return False"""
    if config.get(interfaceName, 'active').lower() in ['true', '1', 'on', 'yes']:
      emergencyGPIO = config.get(interfaceName, 'emergency_gpio')
      photocellGPIO = config.get(interfaceName, 'photocell_gpio')
      mcp0Address = config.get(interfaceName, 'mcp0_address')
      mcp1Address = config.get(interfaceName, 'mcp1_address')
      pinBase = config.get(interfaceName, 'pin_base')
    else:
      return False
  except ConfigParser.NoSectionError:
    print 'Interface ', interfaceName, 'not configured!'

    """Hard-code params for interface ID 0 if it's not configured:"""
    if interfaceID == 0:
      emergencyGPIO = 18
      photocellGPIO = 24
      mcp0Address = 0x20
      mcp1Address = 0x21
      pinBase = 65

  try:

    """Now build a list of interface parameters that will be returned...
    If the values cannot be converted to int, the function will
    return False.
    """
    return [int(emergencyGPIO), int(photocellGPIO),
            int(mcp0Address, 16), int(mcp1Address, 16), int(pinBase)]

  except (ValueError, TypeError):
    raise
    return False

def get_control_settings():
  """Read the GPIO settings from conffile, or revert to defaults
  if they're not found:
  """
  config = ConfigParser.SafeConfigParser()
  config.read('/etc/rpi2caster.conf')
  try:
    ledGPIO = config.get('Control', 'led_gpio')
    shutdownbuttonGPIO = config.get('Control', 'shutdown_gpio')
    rebootbuttonGPIO = config.get('Control', 'reboot_gpio')
    ledGPIO = int(ledGPIO)
    shutdownbuttonGPIO = int(shutdownbuttonGPIO)
    rebootbuttonGPIO = int(rebootbuttonGPIO)
    return [ledGPIO, shutdownbuttonGPIO, rebootbuttonGPIO]
  except (ConfigParser.NoSectionError, TypeError, ValueError):
    """Return default parameters in case they can't be read from file:
    """
    print 'Cannot read from file...'
    return [18, 22, 23]