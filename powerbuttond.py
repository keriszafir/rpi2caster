#!/usr/bin/python
import RPi.GPIO as gpio
import os, sys, time, signal

try:
# Set up the GPIO for button and green LED:
  gpio.setmode(gpio.BCM)
  gpio.setwarnings(False)
  gpio.setup(15, gpio.IN, pull_up_down = gpio.PUD_DOWN) # button
  gpio.setup(4, gpio.OUT) # LED
  gpio.output(4,1)
# Set up the photocell line to be used with rpi2caster:
  os.system('echo "14" > /sys/class/gpio/export') # BCM pin no 14
  os.system('echo "in" > /sys/class/gpio/gpio14/direction') # input
  os.system('echo "both" > /sys/class/gpio/gpio14/edge') # generate interrupts when the photocell becomes obscured AND lit up
  os.system('gpio -g mode 14 up') # set the input as initially high (pull-up)

except RuntimeError:

  print("You must run this program as root!")
  sys.exit()

def blink(n,speed):
  for i in range(0,n):
    gpio.output(4,0)
    time.sleep(speed)
    gpio.output(4,1)
    time.sleep(speed)

def signal_handler(signal, frame):
  print("Terminated by OS")
  blink(3,0.1)
  gpio.output(4,0)
  gpio.cleanup()
  os.system('echo "14" > /sys/class/gpio/unexport')
  sys.exit()

def shutdown(channel):
  time.sleep(2)
  if (gpio.input(15) == 1):
    blink(5,0.1)
    os.system("poweroff")
    gpio.output(4,1)
    gpio.cleanup()

signal.signal(signal.SIGINT, signal_handler)

gpio.add_event_detect(15, gpio.RISING, callback = shutdown, bouncetime = 2000)

while True:
  time.sleep(1)
