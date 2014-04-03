rpi2caster
==========

Raspberry Pi controls a Monotype composition caster.


Based on computer2caster by John Cornelisse
Original idea described at http://letterpress.ch

Target functionality:

1. deprecating all obsolete technology [M$ DOS, LPT / RS232...]

2. complete embedded system with no need to connect a PC to caster

3. standalone or headless, remotely controlled via SSH, VNC and/or web server

4. perhaps adding Mactronic-like functionality of composing based on the input file [PDF, ODS, DOC, LaTeX...]


TODO
====

1. Get a Raspberry Pi mod B and install Raspbian
2. Make a pneumatic interface that attaches on the Monotype's paper tower - or have it made by someone with a CNC mill. 
	This is the hardest part. The pneumatic interface must be very precisely done, so that no air leaks out.
3. Get 31 three-way solenoid valves on valve islands. 12 or 24V DC. 
	IMPORTANT: Some valves require minimum air pressure of 2...2.5bar. Since the Monotype uses 1bar, 
	the pressure differential across the valve will be too low and the valve won't open. We need the 0bar minimum 
	pressure variety, even though they may take more electrical power.
4. Make a RPi I/O extension as shown at:
	http://www.abelectronics.co.uk/products/3/Raspberry-Pi/18/IO-Pi-32-Channel-Port-Expander-for-the-Raspberry-Pi-computer-boards
	Since I live in Poland, buying a module with shipment from the site is more expensive than building one myself. 
	Especially given that the unit needs customizing. I'll use a THT prototyping board and DIP IC's. The extension needs 
	31 additional resistors, transistors and surge suppressing diodes to drive each of the solenoid valves. 
	BTW, I've got a nice power supply salvaged from a fax machine - it supplies +5V and +24V.
5. Port the source so that it uses RPi I/O addresses, can be built with GNU toolchain and supports UTF-8. 


Dependencies
============

You need to install some software to use the RPi GPIO for controlling the interface.

1. Raspbian wheezy (jessie, etc.)
2. RPi.GPIO Python library - https://pypi.python.org/packages/source/R/RPi.GPIO
Make sure you have python-dev and python3-dev installed (build dependencies). Download, untar and run "sudo python setup.py install".
3. i2c-dev - sudo aptitude install i2c-dev
After installing i2c-dev, add user(s) to the i2c group. Add "i2c-dev" module to the /etc/modules file so that you won't have to modprobe it each time.
4. wiringPi C library - find it here with setup instructions: https://projects.drogon.net/raspberry-pi/wiringpi/download-and-install/
