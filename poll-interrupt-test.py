#! /usr/bin/python
import select, os

f = open(os.path('/sys/class/gpio/gpio14/value'), 'r')

po = select.poll()
po.register(f, select.POLLPRI)

while 1:
  events = po.poll(30000)
  if not events:
    print('timeout')
  else:
    f.seek(0)
    state.last=f.read()
