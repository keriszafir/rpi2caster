#!/usr/bin/python
import wiringpi2
import time

wiringpi2.wiringPiSetupGpio()
wiringpi2.pinMode(14, 0)
wiringpi2.pullUpDnControl(14, 2)

def my_int():
    print('Interrupt')
    return True

#wpi = wiringpi2.GPIO(wiringpi2.GPIO.WPI_MODE_PINS)
#wpi.pullUpDnControl(14,wpi.PUD_UP) 
wpi.wiringPiISR(14, wpi.INT_EDGE_RISING, my_int())
while True:
    time.sleep(1)
    print('Waiting...')
