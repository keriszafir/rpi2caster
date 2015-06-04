#rpi2caster

####Raspberry Pi controls a Monotype composition caster.

Based on computer2caster by John Cornelisse
Original idea described at http://letterpress.ch

##Target functionality:

1. deprecating all obsolete technology [M$ DOS, LPT / RS232...]
2. complete embedded system with no need to connect a PC to caster (use TCP/IP networking over a LAN instead)
3. standalone or headless, remotely controlled from other machine on the net (if net unavailable, make your own WLAN with wireless USB dongle, hostapd and dnsmasq)
4. perhaps adding Mactronic-like functionality of composing based on the input file [PDF, ODS, DOC, LaTeX...]
5. web-based UI using node.js along with text UI available from console
6. local configuration stored in SQLite3 database
7. web-based matrix manipulation utility

##Things you need to do

1. Get a Raspberry Pi mod B (rev. 2 has mounting holes; models B+ and 2B are redesigned and much better) and install Raspbian
2. Use Raspbian jessie or stretch
3. Make a pneumatic interface that attaches on the Monotype's paper tower - or have it made by someone with a CNC mill, 3D printer etc. This is the hardest part. The pneumatic interface must be very precisely done, so that no air leaks out.
3. Get 31 three-way solenoid valves on valve islands. 12 or 24V DC. 
IMPORTANT: Some valves require minimum air pressure of 2...2.5bar. Since the Monotype uses 1bar, 
the pressure differential across the valve will be too low and the valve won't open. We need the 0bar minimum 
pressure variety, even though they may take more electrical power.
Like John Cornelisse, I've used the MATRIX (Italy) BX758-8E1C3-24. The valve block is very compact. It features up to 8 valves in a 55x55mm enclosure, with 12V DC or 24V DC controls and minimal pressure of 0 bar (this is important - we'll be using just 1bar!) The cost is about 200 Euro, which still is cheaper than Festo etc.
4. Make a RPi I2C I/O extension as shown at [AB Electronics website](http://www.abelectronics.co.uk/products/3/Raspberry-Pi/18/IO-Pi-32-Channel-Port-Expander-for-the-Raspberry-Pi-computer-boards)
Since I live in Poland, buying a module with shipment from the site is more expensive than building one myself, especially given that the unit needs customizing. I built a module on a THT prototyping board and DIP IC's. The extension needs driver chipss to connect the MCP23017 outputs with each of the solenoid valves. ULN2803 ICs (8-channel Darlington drivers with surge suppressing diodes) are perfect for this. You need 4 of them - two for each of the MCP23017's.You have to choose the different addresses for both MCP23017. This is achieved by connecting different combinations of A0, A1 and A2 input (pin numbers 15, 16, 17) to +3V3 or GND. For my device, I've chosen 0x20 (all pins grounded) for the chip that controls rows, and 1x20 (3V3 on pin 15 and pins 16, 17 grounded) for the chip that controls columns. See pin-mappings.csv 
BTW, I've got a nice power supply salvaged from a fax machine - it supplies +5V and +24V. For future interfaces, I'll use an industrial 24VDC/3A SMPS and a 24VDC/5VDC SMPS to power the Raspberry.
5. Make an enclosure for your project. My device has two parts: one houses Raspberry, a power supply and I/O interface, and is built in an old alarm panel box. The second part is a valve box attached to the caster, made of aluminum mostly by hand (except for the CNC-milled base). They're connected with a 20-pair cable with 37-pin D-SUB connectors, just because I happened to have one lying around. The future controllers will be built as single units, with the Raspberry, interface board and valves in the same box. The only external component would be a 24VDC supply.
6. Resolve the dependencies as described further.
7. Install this software on your RPi. 
8. Add some extra hardware functionality, e.g. status LED, shutdown button etc.

##System config

The most common distro is Raspbian and we'll use jessie or newer.

  * Initial setup (Squeeze won't work because SSH is disabled by default; you have to set up with a local console!):
    1. Find the hosts on your network by typing "nmap -sP 192.168.1.0/24" (if your IP address is on the 192.168.1.x).
    2. Connect the Raspberry to your LAN and power. It should get its IP address by DHCP. Try to find the IP address by running "nmap -sP {subnet IP address}" again; you should see one more IP address and that's probably your RPi.
    3. SSH into it (username: pi, password: raspberry). Since it's your first logon, raspi-config will start automatically. 
    4. Expand rootfs, choose locale, timezone & keyboard layout. You can change the hostname (I've named my machine "monotype"), set up the password etc. 
    5. Exit raspi-config and run ifconfig, check the MAC address if you don't know it already.
  * Network setup - I recommend configuring your router to offer Raspberry a static DHCP lease based on the MAC address. If that's not possible (e.g. you're not a network admin), use static IP address... or scan the network for a host with the RPi's MAC address after each boot. 
  * User & security config
    1. Create user accounts and disable no-password sudoing for "pi" by commenting out the respective line in /etc/sudoers.
    2. Add new users to groups user "pi" belongs to. For security reasons, you may want to  remove "pi" from the "sudo" and "adm" groups.
    3. Since you'll log on the machine via SSH, you can use a RSA key authentication instead of entering a password on each logon. Create a ~/.ssh/authorized_keys file and paste your account@machine's id_rsa.pub contents there. Then you can just ssh by typing "ssh username@monotype" 
  * Various improvements
    1. You may want to change LXDE to Xfce, sysvinit to systemd (for Jessie users), bash to zsh etc. if you want to, know what you're doing and don't have anything against fiddling with your config files.
    2. You can enable GUI access by VNC. Install tightvncserver. Edit /etc/lightdm/lightdm.conf and uncomment the lines in VNC section. Change the port, geometry etc. if you wish. You don't have to create any init scripts; lightdm will already take care of running the VNC server. Just run "vncviewer [hostname or IP addr]:[port]" client-side and you'll get a lightdm login screen. Sign in to your account.
    3. Using a web-based SSH client might be a good idea. I've used shellinabox with great results. This way, you won't have to install any additional software, esp. if you're using M$ Windows (otherwise, you'll need PuTTY or other SSH client).
    4. If we want to use the pins 8 and 10 on the GPIO (which are used as the serial port's RxD and TxD lines by default!), we have to disable the serial port. That is done by editing two files:
      * /etc/inittab: we have to comment out any lines containing the "ttyAMA0 115200 vt100" string
      * /boot/cmdline.txt: remove all references to ttyAMA0
      In my case, these GPIOs are left alone and we don't have to do anything with serial tty config.
  * Get rid of unneeded stuff!
    The original Raspbian distro has some unneeded software installed by default. We can get rid of it by using "sudo aptitude purge...":
    1. wolfram-engine - removing it will clean aomewhere around 450MB (!)
    2. X, LXDE etc. unless you want to VNC into the machine or set up a local console with GUI
    3. anything related to Scratch
    4. Minecraft or any other games, LibreOffice etc., they're huge diskspace hogs, not really needed
	 
##Dependencies

Some of the dependencies will be marked as "(repo)". This means that you can install them from Raspbian repository using apt or aptitude.

1. RPi.GPIO Python library you can find [here](https://pypi.python.org/packages/source/R/RPi.GPIO) - make sure you have python-dev and python3-dev installed (build dependencies). Download, untar and run "sudo python setup.py install".
2. libi2c-dev (repo) - I2C device library, which provides the I2C kernel module. You probably have this already, if you're using Raspbian wheezy or jessie. Run raspi-config and go to advanced settings, then enable GPIO and SPI.	If that didn't work, install with "sudo aptitude install libi2c-dev". After installing i2c-dev, add user(s) to the i2c group unless you want to run the software as root, which is obviously not recommended. Add "i2c-dev" module to the /etc/modules file so that you won't have to modprobe it each time. Remove (or comment) the i2c-bcm2708 in /etc/modprobe.d/raspi-blacklist.conf (raspi-config should do that already)
3. wiringPi2 library - find it (with setup instructions) at [github](https://projects.drogon.net/raspberry-pi/wiringpi/download-and-install/) - necessary. This is required for rpi2caster, it takes care of communicating with MCP23017 via I2C. It also provides the gpio utility used for setting up the inputs in powerbuttond.py daemon.
4. i2c-tools (repo) - this provides i2cdetect which is used for finding the I2C device address, and i2cset, i2cdump and i2cget, for debugging. Not really necessary; I'll try a new deployment without it.
5. python-smbus (repo), Python SMBus & I2C library, wiringpi2 probably depends on it.
6. python-setuptools (repo) - wiringpi2-python depends on it.
7. wiringpi2-python - Python bindings for wiringpi2. You can install it with pip: `sudo pip install wiringpi2` - necessary for program to work!
8. sqlite3 - rpi2caster depends on a sqlite3 database, used for storing caster & interface parameters, diecases and wedges.
9. systemd, systemd-sysv - this software uses a daemon that sets up the GPIOs and runs as a systemd service unit file.
10. python-bs4 - BeautifulSoup is used for parsing the input file in the typesetting program.
