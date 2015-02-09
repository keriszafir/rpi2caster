#!/usr/bin/python
import wiringpi2 as wiringpi
import os, sys, time, signal



"""Set up the GPIO numbers:"""

photocellGPIO      = 17    # photocell input
shutdownbuttonGPIO = 22    # shutdown button input, pulled up
rebootbuttonGPIO   = 23    # reboot button input, pulled up
emergencyGPIO      = 24    # emergency stop button input, pulled up
ledGPIO            = 18    # "system ready" LED output


def blink(n,speed=0.1):
  """Blink a "system ready" LED for n times at a given duration:"""
  for i in range(0,n):
    wiringpi.digitalWrite(ledGPIO,0)
    time.sleep(speed)
    wiringpi.digitalWrite(ledGPIO,1)
    time.sleep(speed)


def signal_handler(signal, frame):
  """Handle the SIGTERM and SIGINT"""
  print("Terminated by OS")
  if(signal=='SIGINT'):
    blink(3)
  """Turn the green LED off if you stop the program with ctrl-C:"""
    wiringpi.digitalWrite(ledGPIO,0)
  os.system('echo "%i" > /sys/class/gpio/unexport' % photocellGPIO)
  sys.exit()

def poweroff(channel):
  shutdown(shutdownbuttonGPIO, 'poweroff')
def reboot(channel):
  shutdown(rebootbuttonGPIO, 'reboot')


def shutdownButton():
  wiringpi.wiringPiISR(shutdownbuttonGPIO, 2, poweroff)

def rebootButton():
  wiringpi.wiringPiISR(rebootbuttonGPIO, 2, reboot)


def shutdown(buttonGPIO, command):
  """A function to shut down or reboot the Raspberry, depending on
  the button which was pressed:
  """
  time.sleep(1)
  """Check if the button is being pressed for more than one second:"""
  if (wiringpi.digitalRead(buttonGPIO) == 1):
    blink(5)
    """Execute the command given as input:"""
    os.system(command)
    """Keep the LED lit until system shuts down:"""
    wiringpi.digitalWrite(ledGPIO,1)
    os.system('echo "%i" > /sys/class/gpio/unexport' % photocellGPIO)
    sys.exit()


def gpio_setup():
  """Set up the GPIOs for LED and buttons:"""
  wiringpi.wiringPiSetupGpio()

  """Internal pull-up for buttons:"""
  wiringpi.pullUpDnControl(shutdownbuttonGPIO, 2)
  wiringpi.pullUpDnControl(rebootbuttonGPIO, 2)
  """LED output:"""
  wiringpi.pinMode(ledGPIO, 1)
  wiringpi.digitalWrite(ledGPIO, 1)

  """Export the machine cycle sensor GPIO output as file,
  so that rpi2caster can access it without root privileges:
  """
  os.system('echo "%i" > /sys/class/gpio/export' % photocellGPIO)
  os.system('echo "in" > /sys/class/gpio/gpio%i/direction' % photocellGPIO)

  """Enable generating interrupts on rising and falling edges:"""
  os.system('echo "both" > /sys/class/gpio/gpio%i/edge' % photocellGPIO)

  """Export the emergency stop button GPIO output as file,
  so that rpi2caster can access it without root privileges:
  """
  os.system('echo "%i" > /sys/class/gpio/export' % emergencyGPIO)
  os.system('echo "in" > /sys/class/gpio/gpio%i/direction' % emergencyGPIO)

  """Enable generating interrupts on rising and falling edges:"""
  os.system('echo "both" > /sys/class/gpio/gpio%i/edge' % emergencyGPIO)


try:
  gpio_setup()

except RuntimeError:

  print("You must run this program as root!")
  sys.exit()


if __name__ == '__main__':

  """Add signal handling:"""
  signal.signal(signal.SIGINT, signal_handler)
  signal.signal(signal.SIGTERM, signal_handler)

  """Do a threaded callback when one of buttons is pressed:"""
  wiringpi.piThreadCreate('shutdownButton')
  wiringpi.piThreadCreate('rebootButton')


  # Do nothing and wait for interrupt from the reboot/shutdown buttons:
  while True:
    time.sleep(1)