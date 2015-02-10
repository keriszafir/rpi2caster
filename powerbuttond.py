#!/usr/bin/python
import RPi.GPIO as gpio
import ConfigParser
import os, sys, time, signal
global photocellGPIO, shutdownbuttonGPIO, rebootbuttonGPIO, ledGPIO
ledGPIO = 0
shutdownbuttonGPIO = 22
rebootbuttonGPIO = 0
photocellGPIO = 0
emergencyGPIO = 0

"""
# initial config, use BCM GPIO numbers
# the colours are for my prototype; "production"  interfaces will
# have a PCB directly on top of RPi
photocellGPIO      = 17    # black, don't confuse with GND!
shutdownbuttonGPIO = 22    # brown
rebootbuttonGPIO   = 23    # yellow
emergencyGPIO      = 24    # not used yet
ledGPIO            = 18    # blue
"""

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

def blink(n,speed):
  for i in range(0,n):
    gpio.output(ledGPIO,0)
    time.sleep(speed)
    gpio.output(ledGPIO,1)
    time.sleep(speed)

def signal_handler(signal, frame):
  print("Terminated by OS")
  if(signal=='SIGINT'):
    blink(3,0.1)
  # turn the green LED off if you stop the program with ctrl-C
    gpio.output(ledGPIO,0)
  gpio.cleanup()
  os.system('echo "%i" > /sys/class/gpio/unexport' % photocellGPIO)
  sys.exit()

def poweroff(channel):
  shutdown(shutdownbuttonGPIO, 0)
def reboot(channel):
  shutdown(rebootbuttonGPIO, 1)

def shutdown(buttonGPIO, mode):
  command = {0 : 'poweroff', 1 : 'reboot', 2: 'echo "debug info"'}
  time.sleep(1)
  if (gpio.input(buttonGPIO) == 1):   #check if you're still pressing the button after 1sec
    blink(5,0.1)
    os.system(command[mode])
    gpio.output(ledGPIO,1) # keep the green LED lit up until system shuts down completely
    gpio.cleanup()
    os.system('echo "%i" > /sys/class/gpio/unexport' % photocellGPIO)
    sys.exit()

try:

  [ledGPIO, shutdownbuttonGPIO, rebootbuttonGPIO] = get_control_settings()
  print [ledGPIO, shutdownbuttonGPIO, rebootbuttonGPIO]
# Set up the GPIO for button and green LED:
  gpio.setmode(gpio.BCM)
  gpio.setwarnings(False)
  gpio.setup(shutdownbuttonGPIO, gpio.IN, pull_up_down = gpio.PUD_DOWN) # shutdown button
  gpio.setup(rebootbuttonGPIO, gpio.IN, pull_up_down = gpio.PUD_DOWN) # reboot button
  gpio.setup(ledGPIO, gpio.OUT) # green LED
  gpio.output(ledGPIO, 1)

# Set up the machine cycle sensor (photocell) GPIO to be used with rpi2caster:
  os.system('echo "%i" > /sys/class/gpio/export' % photocellGPIO) # define BCM pin no for photocell input
  os.system('echo "in" > /sys/class/gpio/gpio%i/direction' % photocellGPIO) # set gpio up as input

# Enable generating interrupts when the photocell becomes obscured AND lit up
  os.system('echo "both" > /sys/class/gpio/gpio%i/edge' % photocellGPIO)

# Set up the emergency stop button GPIO to be used with rpi2caster:
  os.system('echo "%i" > /sys/class/gpio/export' % emergencyGPIO) # define BCM pin no for photocell input
  os.system('echo "in" > /sys/class/gpio/gpio%i/direction' % emergencyGPIO) # set gpio up as input

# Enable generating interrupts when the photocell becomes obscured AND lit up
  os.system('echo "both" > /sys/class/gpio/gpio%i/edge' % emergencyGPIO)

except RuntimeError:

  print("You must run this program as root!")
  sys.exit()


if __name__ == '__main__':

  # Add signal handling:
  signal.signal(signal.SIGINT, signal_handler)
  signal.signal(signal.SIGTERM, signal_handler)

  # If user presses shutdown or reboot button,
  # do a threaded callback to shutdown function:
  gpio.add_event_detect(shutdownbuttonGPIO, gpio.RISING,
                        callback = poweroff, bouncetime = 1000)

  gpio.add_event_detect(rebootbuttonGPIO, gpio.RISING,
                        callback = reboot, bouncetime = 1000)

  # Do nothing and wait for interrupt from the reboot/shutdown buttons:
  while True:
    time.sleep(1)