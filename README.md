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
