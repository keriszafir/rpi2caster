#!/usr/bin/python
import RPi.GPIO as gpio
import os, sys, time, signal

# initial config, use BCM GPIO numbers
photocellGPIO = 17         # yellow - was gpio 14, pin 8 - let's leave that alone for UART TxD
shutdownbuttonGPIO = 22    # brown - was gpio 15, pin 10 - let's leave that alone for UART RxD
rebootbuttonGPIO = 23      # black
ledGPIO = 4                # blue

def blink(n,speed):
  for i in range(0,n):
    gpio.output(ledGPIO,0)
    time.sleep(speed)
    gpio.output(ledGPIO,1)
    time.sleep(speed)

def signal_handler(signal, frame):
  print("Terminated by OS")
  if(signal==SIGINT):
    blink(3,0.1)
# turn the green LED off if you stop the program with ctrl-C
    gpio.output(ledGPIO,0)
  gpio.cleanup()
  os.system('echo "%i" > /sys/class/gpio/unexport' % photocellGPIO)
  sys.exit()

def shutdown(buttonGPIO, mode):
  command = [0 : 'poweroff', 1 : 'reboot', 2: 'echo "debug info"']
  time.sleep(1)
  if (gpio.input(buttonGPIO) == 1):   #check if you're still pressing the button after 1sec
    blink(5,0.1)
    os.system(command[mode])
    gpio.output(ledGPIO,1) # keep the green LED lit up until system shuts down completely
    gpio.cleanup()
    os.system('echo "%i" > /sys/class/gpio/unexport' % photocellGPIO)
    sys.exit()

try:
# Set up the GPIO for button and green LED:
  gpio.setmode(gpio.BCM)
  gpio.setwarnings(False)
  gpio.setup(shutdownbuttonGPIO, gpio.IN, pull_up_down = gpio.PUD_DOWN) # shutdown button
  gpio.setup(rebootbuttonGPIO, gpio.IN, pull_up_down = gpio.PUD_DOWN) # reboot button
  gpio.setup(ledGPIO, gpio.OUT) # green LED
  gpio.output(ledGPIO,1)
# Set up the machine cycle sensor (photocell) GPIO to be used with rpi2caster:
  os.system('echo "%i" > /sys/class/gpio/export' % photocellGPIO) # define BCM pin no for photocell input
  os.system('echo "in" > /sys/class/gpio/gpio%i/direction' % photocellGPIO) # set gpio up as input
# Enable generating interrupts when the photocell becomes obscured AND lit up
  os.system('echo "both" > /sys/class/gpio/gpio%i/edge' % photocellGPIO)

except RuntimeError:

  print("You must run this program as root!")
  sys.exit()


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# If user presses shutdown or reboot button, do a threaded callback to shutdown function:
gpio.add_event_detect(shutdownbuttonGPIO, gpio.RISING,
    callback = shutdown(shutdownbuttonGPIO, 0), bouncetime = 1000)
gpio.add_event_detect(rebootbuttonGPIO, gpio.RISING,
    callback = shutdown(rebootbuttonGPIO, 1), bouncetime = 1000)

while True:
  time.sleep(1)  # just wait