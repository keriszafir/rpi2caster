#!/usr/bin/python
import RPi.GPIO as gpio
import os, sys, time, signal

# initial config, use BCM GPIO numbers
photocellGPIO = 14
buttonGPIO = 15
ledGPIO = 4

try:
# Set up the GPIO for button and green LED:
  gpio.setmode(gpio.BCM)
  gpio.setwarnings(False)
  gpio.setup(buttonGPIO, gpio.IN, pull_up_down = gpio.PUD_DOWN) # shutdown button
  gpio.setup(ledGPIO, gpio.OUT) # green LED
  gpio.output(ledGPIO,1)
# Set up the machine cycle sensor (photocell) GPIO to be used with rpi2caster:
  os.system('echo "%s" > /sys/class/gpio/export' % photocellGPIO) # BCM pin for photocell input
  os.system('echo "in" > /sys/class/gpio/gpio%s/direction' % photocellGPIO) # input
# Enable generating interrupts when the photocell becomes obscured AND lit up
  os.system('echo "both" > /sys/class/gpio/gpio%s/edge' % photocellGPIO)

except RuntimeError:

  print("You must run this program as root!")
  sys.exit()

def blink(n,speed):
  for i in range(0,n):
    gpio.output(ledGPIO,0)
    time.sleep(speed)
    gpio.output(ledGPIO,1)
    time.sleep(speed)

def signal_handler(signal, frame):
  print("Terminated by OS")
  blink(3,0.1)
# turn the green LED off if you stop the program with ctrl-C or SIGTERM
  gpio.output(ledGPIO,0)
  gpio.cleanup()
  os.system('echo "%s" > /sys/class/gpio/unexport' % photocellGPIO)
  sys.exit()

def shutdown():
  time.sleep(1000)
  if (gpio.input(buttonGPIO) == 1):   #check if you're still pressing the button after 1sec
    blink(5,0.1)
    os.system("poweroff")
    gpio.output(ledGPIO,1) # keep the green LED lit up until system shuts down completely
    gpio.cleanup()
    os.system('echo "%s" > /sys/class/gpio/unexport' % photocellGPIO)
    sys.exit()
  else
    continue

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
# gpio.add_event_detect(buttonGPIO, gpio.RISING, callback = shutdown, bouncetime = 1000)

while True:
  gpio.wait_for_edge(buttonGPIO, gpio.RISING)  # hold the program execution until interrupt
  shutdown()