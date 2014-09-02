#!/usr/bin/python
import sys, os, time
import wiringpi2 as wiringpi
wiringpi.mcp23017Setup(65,0x20)
wiringpi.mcp23017Setup(81,0x21)

monotypeSignal = dict([(65, '1'), (66, '2'), (67, '3'), (68, '4'), (69, '5'), (70, '6'), (71, '7'), (72, '8'), (73, '9'), (74, '10'), (75, '11'), (76, '12'), (77, '13'), (78, '14'), (79, '0005'), (80, '0075'), (81, 'A'), (82, 'B'), (83, 'C'), (84, 'D'), (85, 'E'), (86, 'F'), (87, 'G'), (88, 'H'), (89, 'I'), (90, 'J'), (91, 'K'), (92, 'L'), (93, 'M'), (94, 'N'), (95, 'S'), (96, 'O15')])

for pin in range(65,97):
	wiringpi.pinMode(pin,1)

try:
	while 1:
		print("We'll test the Monotype interface. \nEach line will be switched on and the number will be displayed on screen.")
		for pin in range(65,97):
			print("Line: " + monotypeSignal[pin])
			wiringpi.digitalWrite(pin,1)
			time.sleep(1)
			wiringpi.digitalWrite(pin,0)
		print("The test is done. Starting all over again!")
		
except RuntimeError:
	print("You must run this program as root!")
except KeyboardInterrupt:
	print("Terminated by user.")
finally:
	for pin in range(65,97):
		wiringpi.digitalWrite(pin, 0)
	exit()
