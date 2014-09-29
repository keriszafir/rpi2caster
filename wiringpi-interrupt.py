#!/usr/bin/python
import wiringpi2 as wiringpi
import time

wiringpi.wiringPiSetupSys()
wiringpi.pinMode(14, 0)
# wiringpi.pullUpDnControl(14, 2) not working in sys mode, exported with gpio utility at system startup

def interrupt_test():
  print('It works')
  return True

wiringpi.wiringPiISR(14, wiringpi.INT_EDGE_BOTH, interrupt_test())
while True:
  time.sleep(1)
  print('Waiting...')
