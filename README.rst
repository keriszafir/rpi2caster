rpi2caster
==========

Raspberry Pi controls a Monotype composition caster.
----------------------------------------------------

Based on computer2caster by John Cornelisse Original idea described at
http://letterpress.ch

Typesetting and casting software for a Raspberry Pi-based computer
control attachment for Monotype composition casters.

This program suite consists of three major parts:

1. Typesetting program for parsing UTF-8 text, calculating justification
   and coding it as a series of control codes accepted by the Monotype
   composition caster,
2. Casting program for sending said codes to the casting machine using
   an interface with 32 pneumatic outputs, a pneumatic connection block
   attached to the caster's paper tower and a machine cycle sensor
   input. The program also allows to cast sorts, test the machine or set
   a short text on-the-fly, then cast the composed type.
3. Inventory management program for adding, editing and deleting the
   definitions for replaceable machine components: normal wedges and
   matrix cases (diecases).

The workflow is as follows: 1. define matrix case layouts for your
matrix cases (and edit if needed), 2. define your normal wedges so that
the program knows what series in which set widths you have, 3. use a
typesetting program to generate a "ribbon" i.e. series of control codes
from a text, for a specified matrix case and normal wedge, 4. use the
casting program to test the machine/interface, perform machine
adjustments, and cast the type from ribbon you made earlier.

Things you need to do
~~~~~~~~~~~~~~~~~~~~~

1. Get a Raspberry Pi mod B+ or 2B and install Raspbian
2. Use Raspbian jessie or stretch
3. Make a pneumatic interface that attaches on the Monotype's paper
   tower - or have it made by someone with a CNC mill, 3D printer etc.
   This is the hardest part. The pneumatic interface must be very
   precisely done, so that no air leaks out.
4. Get 31 three-way solenoid valves on valve islands. 12 or 24V DC.
   IMPORTANT: Some valves require minimum air pressure of 2...2.5bar.
   Since the Monotype caster uses 1bar, the pressure differential across
   the valve will be too low and the valve won't open. We need the 0bar
   minimum pressure variety, even though they may take more electrical
   power. A great candidate is the MATRIX BX758-8E1C3-24. The valve
   block is very compact and looks a bit like a stepper motor. It
   features up to 8 valves in a 55x55mm enclosure, with 12V DC or 24V DC
   controls and minimal pressure of 0 bar (this is important - we'll be
   using just 1bar!) The cost is about 200 Euro per piece (we need a set
   of 4). Another good candidates are e.g. two Festo CPV10-GE-MP-8
   islands with 8 x "C" valve (i.e. dual 3/2) and separate connections
   for pilot supply.
5. Make a RPi to 32 open collector output interface (the Raspberry's
   native GPIO pins cannot drive 24V loads, and there's not enough of
   them). Check out
   https://github.com/elegantandrogyne/rpi2caster-doc-hardware for the
   documentation (electrical in Eagle, PDF and Gerber, mechanical in
   CorelDraw) of my interface.
6. Resolve the dependencies as described further.
7. Install this software on your RPi.

System config
~~~~~~~~~~~~~

The most common distro is Raspbian and we'll use jessie or newer. If you
need GUI (HDMI connection from Raspberry to monitor/TV, local console),
choose the standard image; otherwise (for headless setup) use minimal.
Assuming that you know your way around the Raspberry, SSH into it, set
it up (you must enable I2C), choose locale, change password, update the
system etc.

-  Network setup - I recommend configuring your router to offer the
   Raspberry a static DHCP lease based on the MAC address. If that's not
   possible (e.g. you don't have admin access to the router), use static
   IP address or scan the network for a host with the RPi's MAC address
   after each boot.
-  User & security config advice:

   1. Create user accounts and disable no-password sudoing for "pi" by
      commenting out the respective line in /etc/sudoers.
   2. Add new users to groups user "pi" belongs to. For security
      reasons, you may want to remove "pi" from the "sudo" and "adm"
      groups.
   3. Since you'll log on the machine via SSH, you can use a RSA key
      authentication instead of entering a password on each logon.
      Either use a "ssh-copy-id [target-username@]target-host" command
      or create a ~/.ssh/authorized\_keys file on the Raspberry and
      paste your id\_rsa.pub contents there. Then you can just ssh by
      typing "ssh [username@]monotype" or via PuTTY.

-  Various improvements

   1. You can enable GUI access by VNC. Install tightvncserver. Edit
      /etc/lightdm/lightdm.conf and uncomment the lines in VNC section.
      Change the port, geometry etc. if you wish. You don't have to
      create any init scripts; lightdm will already take care of running
      the VNC server. Just run "vncviewer [hostname or IP addr]:[port]"
      client-side and you'll get a lightdm login screen. Sign in to your
      account.
   2. Using a web-based SSH client might be a good idea. I've used
      shellinabox with great results. This way, you won't have to
      install any additional software, esp. if you're using M$ Windows
      (otherwise, you'll need PuTTY or other SSH client).

-  Get rid of unneeded stuff! The original Raspbian distro has some
   unneeded software installed by default. We can get rid of it by using
   "sudo aptitude purge...":

   1. wolfram-engine - removing it will clean somewhere around 450MB (!)
   2. X, LXDE etc. unless you want to VNC into the machine or set up a
      local console with GUI
   3. anything related to Scratch
   4. Minecraft or any other games, LibreOffice etc., they're huge
      diskspace hogs, not really needed

Dependencies
~~~~~~~~~~~~

Some of the dependencies will be marked as "(repo)". This means that you
can install them from Raspbian repository using apt or aptitude.

1. python3 - doesn't come with minimal Jessie, and rpi2caster is written
   in python3 only (it's relatively new and there's no need for
   backwards compatibility)
2. python3-pip - for installing python3 packages (install it with apt or
   aptitude; python3 will be installed automatically)
3. wiringpi2-python - Python bindings for wiringpi2. You can install it
   with pip3: ``sudo pip3 install wiringpi2`` - necessary for program to
   work!
