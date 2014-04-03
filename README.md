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
	John Cornelisse used the MATRIX (Italy) 750 series. Th valve block is very compact. It features up to 8 valves in 
	a 55x55mm enclosure, with 12V DC or 24V DC controls and minimal pressure of 0 bar. Perfect. I'll use four 8-valve blocks.
4. Make a RPi I2C I/O extension as shown at:
	http://www.abelectronics.co.uk/products/3/Raspberry-Pi/18/IO-Pi-32-Channel-Port-Expander-for-the-Raspberry-Pi-computer-boards
	Since I live in Poland, buying a module with shipment from the site is more expensive than building one myself, 
	especially given that the unit needs customizing. I built a module on a THT prototyping board and DIP IC's. The extension needs 
	drivers to connect the MCP23017 outputs with each of the solenoid valves. ULN2803 ICs (8-channel Darlington drivers 
	with surge suppressing diodes) are perfect for this. You need 4 of them - two for each of the MCP23017's.
	BTW, I've got a nice power supply salvaged from a fax machine - it supplies +5V and +24V.
5. Resolve the dependencies as described further.
6. Port the source so that it uses RPi I/O addresses, can be built with GNU toolchain and supports UTF-8. 
7. Add some extra hardware functionality, e.g. status LED, shutdown button etc.


Dependencies
============

You need to install some software to use the RPi GPIO for controlling the interface.

1. Raspbian wheezy (jessie, etc.)
	Initial setup: expand rootfs, enable SSH, choose locale, change the hostname, set up the password etc. using raspi-config. 
	Create user accounts and disable no-password admin login for "pi" by commenting out the respective line in /etc/sudoers.
	Add new users to groups user "pi" belongs to.
	You can enable GUI access by VNC. Install tightvncserver. Edit /etc/lightdm/lightdm.conf and uncomment the lines in VNC section. 
	You can change the port, geometry etc. as well. You don't have to create any init scripts; lightdm will take care of running the
	VNC server. Just run "vncviewer [hostname or IP addr]:[port]" client-side and you'll get a lightdm login screen. Sign in to your account.
2. RPi.GPIO Python library - https://pypi.python.org/packages/source/R/RPi.GPIO
	Make sure you have python-dev and python3-dev installed (build dependencies). Download, untar and run "sudo python setup.py install".
3. libi2c-dev - I2C device library, which provides the I2C kernel module.
	Install with "sudo aptitude install libi2c-dev"
	After installing i2c-dev, add user(s) to the i2c group unless you want to run the software as root, which is obviously not recommended. 
	Add "i2c-dev" module to the /etc/modules file so that you won't have to modprobe it each time.
4. wiringPi library - find it here with setup instructions: https://projects.drogon.net/raspberry-pi/wiringpi/download-and-install/
	This is required for C programs to use the GPIO. 
5. i2c-tools - this provides i2cdetect which is used for finding the I2C device address, and i2cset, i2cdump and i2cget, for debugging.
Install with "sudo aptitude install i2c-tools".
