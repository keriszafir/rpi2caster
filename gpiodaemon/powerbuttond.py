#!/usr/bin/python
import RPi.GPIO as gpio
import os
import sys
import time
import signal
import ConfigParser

ready_led_gpio = 18
shutdown_button_gpio = 24
reboot_button_gpio = 23
sensor_gpio = 17
emergency_stop_gpio = 5


def get_control_settings():
    """Read the GPIO settings from conffile, or revert to defaults
    if they're not found:
    """
    config = ConfigParser.SafeConfigParser()
    config.read('/etc/rpi2caster.conf')
    try:
        ready_led_gpio = config.get('Control', 'led_gpio')
        shutdown_button_gpio = config.get('Control', 'shutdown_gpio')
        reboot_button_gpio = config.get('Control', 'reboot_gpio')
        ready_led_gpio = int(ready_led_gpio)
        shutdown_button_gpio = int(shutdown_button_gpio)
        reboot_button_gpio = int(reboot_button_gpio)
        return (ready_led_gpio, shutdown_button_gpio, reboot_button_gpio)
    except (ConfigParser.NoSectionError, TypeError, ValueError):
        # Return default parameters in case they can't be read from file
        return [18, 24, 23]


def blink(n, speed):
    """Blinks a LED."""
    for i in range(0, n):
        gpio.output(ready_led_gpio, 0)
        time.sleep(speed)
        gpio.output(ready_led_gpio, 1)
        time.sleep(speed)


def signal_handler(signal, frame):
    """Handles the SIGTERM or SIGINT (ctrl-C) received from OS."""
    print("Terminated by OS")
    if(signal == 'SIGINT'):
        blink(3, 0.1)
        # turn the green LED off if you stop the program with ctrl-C
        gpio.output(ready_led_gpio, 0)
    gpio.cleanup()
    os.system('echo "%i" > /sys/class/gpio/unexport' % sensor_gpio)
    sys.exit()


def poweroff(channel):
    """Calls shutdown with shutdown mode"""
    shutdown(shutdown_button_gpio, 0)


def reboot(channel):
    """Calls shutdown with reboot mode"""
    shutdown(reboot_button_gpio, 1)


def shutdown(button_gpio, mode):
    """Sends a command to OS to shutdown or reboot the Raspberry."""
    command = {0: 'poweroff', 1: 'reboot', 2: 'echo "debug info"'}
    time.sleep(1)
    # Check if you're still pressing the button after 1sec
    if gpio.input(button_gpio) == 1:
        blink(5, 0.1)
        os.system(command[mode])
        # Keep the green LED lit up until system shuts down completely
        gpio.output(ready_led_gpio, 1)
        gpio.cleanup()
        os.system('echo "%i" > /sys/class/gpio/unexport' % sensor_gpio)
        os.system('echo "%i" > /sys/class/gpio/unexport' % emergency_stop_gpio)
        sys.exit()

try:
    (ready_led_gpio, shutdown_button_gpio,
     reboot_button_gpio) = get_control_settings()
    # Set up the GPIO for button and green LED:
    gpio.setmode(gpio.BCM)
    gpio.setwarnings(False)
    gpio.setup(shutdown_button_gpio, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    gpio.setup(reboot_button_gpio, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    gpio.setup(ready_led_gpio, gpio.OUT)  # green LED
    gpio.output(ready_led_gpio, 1)
    # Set up the machine cycle sensor GPIO to be used with rpi2caster:
    # Define BCM pin no for photocell input
    os.system('echo "%i" > /sys/class/gpio/export'
              % sensor_gpio)
    # Set up the GPIO as input:
    os.system('echo "in" > /sys/class/gpio/gpio%i/direction'
              % sensor_gpio)
    # Enable generating interrupts when the photocell goes on and off
    os.system('echo "both" > /sys/class/gpio/gpio%i/edge'
              % sensor_gpio)
    # Set up the emergency stop button GPIO to be used with rpi2caster:
    # Define BCM pin no for emergency stop button input
    os.system('echo "%i" > /sys/class/gpio/export'
              % emergency_stop_gpio)
    # Set up the GPIO as input
    os.system('echo "in" > /sys/class/gpio/gpio%i/direction'
              % emergency_stop_gpio)
    # Enable generating interrupts when the button becomes on off
    os.system('echo "both" > /sys/class/gpio/gpio%i/edge'
              % emergency_stop_gpio)

except RuntimeError:
    print("You must run this program as root!")
    sys.exit()

if __name__ == '__main__':
    # Add signal handling:
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # If user presses shutdown or reboot button,
    # do a threaded callback to shutdown function:
    gpio.add_event_detect(shutdown_button_gpio, gpio.RISING,
                          callback=poweroff, bouncetime=1000)
    gpio.add_event_detect(reboot_button_gpio, gpio.RISING,
                          callback=reboot, bouncetime=1000)
    # Do nothing and wait for interrupt from the reboot/shutdown buttons:
    while True:
        time.sleep(1)
