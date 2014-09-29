#! /usr/bin/python
import select, os, sys, time
gpiofilename='/sys/class/gpio/gpio14/value'

with open(gpiofilename, 'r') as gpiostate:
  po = select.epoll()
  po.register(gpiostate, select.POLLPRI)
  while 1:
    events = po.poll(5)
    if events:
      gpiostate.seek(0)
      state_last = gpiostate.read()
      print 'Val: %s' % state_last
    else:
      print('Machine not running!')
      exit()
