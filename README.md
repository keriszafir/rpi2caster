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
	You have to choose the different addresses for both MCP23017. This is achieved by connecting different combinations of A0, A1
	and A2 input (pin numbers 15, 16, 17) to +3V3 or GND. For my device, I've chosen 0x20 (all pins grounded) for the chip that 
	controls rows, and 1x20 (3V3 on pin 15 and pins 16, 17 grounded) for the chip that controls columns. See pin-mappings.csv 
	BTW, I've got a nice power supply salvaged from a fax machine - it supplies +5V and +24V.
5. Resolve the dependencies as described further.
6. Port the source so that it uses RPi I/O addresses, can be built with GNU toolchain and supports UTF-8. 
7. Add some extra hardware functionality, e.g. status LED, shutdown button etc.


Dependencies
============

You need to install some software to use the RPi GPIO for controlling the interface.

1. Raspbian wheezy, jessie, etc.
	Initial setup (Squeeze won't work because SSH is disabled by default; you have to set up with a local console!):

        Find the hosts on your network by typing "nmap -sP 192.168.1.0/24" (if your IP address is on the 192.168.1.x).
	Connect the Raspberry to your LAN and power. It should get its IP address by DHCP. Try to find the IP address by running 
        "nmap -sP {subnet IP address}" again; you should see one more IP address and that's probably your RPi.
        SSH into it (username: pi, password: raspberry). Since it's your first logon, raspi-config will start automatically. 
        Expand rootfs, choose locale, timezone & keyboard layout. You can change the hostname (I've named my machine "monotype"), 
        set up the password etc. 
        Exit raspi-config and run ifconfig, check the MAC address if you don't know it already.

	Network setup - I recommend configuring your router to offer Raspberry a static DHCP lease based on the MAC address. 
	If that's not possible (e.g. you're not a network admin), use static IP address... or scan the network for a host 
	with the RPi's MAC address after each boot. 
 
	Create user accounts and disable no-password sudoing for "pi" by commenting out the respective line in /etc/sudoers.
	Add new users to groups user "pi" belongs to. For security reasons, you may want to  remove "pi" from the "sudo" and "adm" groups.
        
        Since you'll log on the machine via SSH, you can use a RSA key authentication instead of entering a password on each logon.
        Create a ~/.ssh/authorized_keys file and paste your account@machine's id_rsa.pub contents there. Then you can just ssh by typing
        "ssh username@monotype" 

        You may want to change LXDE to Xfce, sysvinit to systemd (for Jessie users), bash to zsh etc. if you want to, know what you're doing 
	and don't have anything against fiddling with your config files.

	You can enable GUI access by VNC. Install tightvncserver. Edit /etc/lightdm/lightdm.conf and uncomment the lines in VNC section. 
	Change the port, geometry etc. if you wish. You don't have to create any init scripts; lightdm will already take care of running the
	VNC server. Just run "vncviewer [hostname or IP addr]:[port]" client-side and you'll get a lightdm login screen. Sign in to your account.

	If we want to use the pins 8 and 10 on the GPIO (which are used as the serial port's RxD and TxD lines by default!), we have to disable
	the serial port. That is done by editing two files:
	/etc/inittab: we have to comment out any lines containing the "ttyAMA0 115200 vt100" string
	/boot/cmdline.txt: remove all references to ttyAMA0
	 
	Some of the dependencies will be marked as "(repo)". This means that you can install them from Raspbian repository using apt or aptitude.

2. RPi.GPIO Python library - https://pypi.python.org/packages/source/R/RPi.GPIO
	Make sure you have python-dev and python3-dev installed (build dependencies). Download, untar and run "sudo python setup.py install".
3. libi2c-dev (repo) - I2C device library, which provides the I2C kernel module.
	Install with "sudo aptitude install libi2c-dev"
	After installing i2c-dev, add user(s) to the i2c group unless you want to run the software as root, which is obviously not recommended. 
	Add "i2c-dev" module to the /etc/modules file so that you won't have to modprobe it each time.
	Remove (or comment) the i2c-bcm2708 in /etc/modprobe.d/raspi-blacklist.conf

4. wiringPi2 library - find it (with setup instructions) at https://projects.drogon.net/raspberry-pi/wiringpi/download-and-install/
	This is required for programs to access GPIO.
5. i2c-tools (repo) - this provides i2cdetect which is used for finding the I2C device address, and i2cset, i2cdump and i2cget, for debugging.
	libi2c-dev depends on i2c-tools, so this will already be installed in step 3.
6. python-smbus (repo), Python SMBus & I2C library, needed to control the valves
7. python-setuptools (repo) - you need it to install a Python module for WiringPi
8. WiringPi2-Python - install it from GitHub. Instructions at https://github.com/WiringPi/WiringPi2-Python/blob/master/README
9. gpio - command line utility for GPIO setup & management, used by powerbuttond.py


Garbage removal
===============

The original Raspbian distro has some unneeded software installed by default. We can get rid of it by using "sudo aptitude purge...":
-wolfram-engine - removing it will clean aomewhere around 450MB (!)
-X, LXDE etc. unless you want to VNC into the machine or set up a local console with GUI
-anything related to Scratch
