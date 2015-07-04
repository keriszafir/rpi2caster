#!/usr/bin/python
import wiringpi2 as wiringpi
import os
import sys
import time
import signal


# Set up the GPIO numbers:
sensor_gpio = 17  # photocell input
shutdown_button_gpio = 22  # shutdown button input, pulled up
reboot_button_gpio = 23  # reboot button input, pulled up
emergency_gpio = 24  # emergency stop button input, pulled up
led_gpio = 18  # "system ready" LED output


def blink(n, speed=0.1):
    """Blink a "system ready" LED for n times at a given duration:"""
    for i in range(0, n):
        wiringpi.digitalWrite(led_gpio, 0)
        time.sleep(speed)
        wiringpi.digitalWrite(led_gpio, 1)
        time.sleep(speed)


def signal_handler(signal, frame):
    """Handle the SIGTERM and SIGINT"""
    print("Terminated by OS")
    if signal == 'SIGINT':
        blink(3)
        # Turn the green LED off if you stop the program with ctrl-C
        wiringpi.digitalWrite(led_gpio, 0)
    os.system('echo "%i" > /sys/class/gpio/unexport' % sensor_gpio)
    os.system('echo "%i" > /sys/class/gpio/unexport' % emergency_gpio)
    sys.exit()


def poweroff(channel):
    shutdown(shutdown_button_gpio, 'poweroff')


def reboot(channel):
    shutdown(reboot_button_gpio, 'reboot')


def PI_THREAD(shutdown_button):
    wiringpi.wiringPiISR(shutdown_button_gpio, 2, poweroff)


def PI_THREAD1(reboot_button):
    wiringpi.wiringPiISR(reboot_button_gpio, 2, reboot)


def shutdown(buttonGPIO, command):
    """A function to shut down or reboot the Raspberry, depending on
    the button which was pressed:
    """
    time.sleep(1)
    """Check if the button is being pressed for more than one second:"""
    if (wiringpi.digitalRead(buttonGPIO) == 1):
        blink(5)
        """Execute the command given as input:"""
        os.system(command)
        """Keep the LED lit until system shuts down:"""
        wiringpi.digitalWrite(led_gpio, 1)
        os.system('echo "%i" > /sys/class/gpio/unexport' % sensor_gpio)
        sys.exit()


def gpio_setup():
    """Set up the GPIOs for LED and buttons:"""
    wiringpi.wiringPiSetupGpio()

    """Internal pull-up for buttons:"""
    wiringpi.pullUpDnControl(shutdown_button_gpio, 2)
    wiringpi.pullUpDnControl(reboot_button_gpio, 2)

    """LED output:"""
    wiringpi.pinMode(led_gpio, 1)
    wiringpi.digitalWrite(led_gpio, 1)

    """Export the machine cycle sensor GPIO output as file,
    so that rpi2caster can access it without root privileges:
    """
    os.system('echo "%i" > /sys/class/gpio/export' % sensor_gpio)
    os.system('echo "in" > /sys/class/gpio/gpio%i/direction' % sensor_gpio)

    """Enable generating interrupts on rising and falling edges:"""
    os.system('echo "both" > /sys/class/gpio/gpio%i/edge' % sensor_gpio)

    """Export the emergency stop button GPIO output as file,
    so that rpi2caster can access it without root privileges:
    """
    os.system('echo "%i" > /sys/class/gpio/export' % emergency_gpio)
    os.system('echo "in" > /sys/class/gpio/gpio%i/direction' % emergency_gpio)

    """Enable generating interrupts on rising and falling edges:"""
    os.system('echo "both" > /sys/class/gpio/gpio%i/edge' % emergency_gpio)


try:
    gpio_setup()
except RuntimeError:
    print("You must run this program as root!")
    sys.exit()


if __name__ == '__main__':
    """Add signal handling:"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    """Do a threaded callback when one of buttons is pressed:"""
    wiringpi.piThreadCreate(shutdown_button)
    wiringpi.piThreadCreate(reboot_button)

    # Do nothing and wait for interrupt from the reboot/shutdown buttons:
    while True:
        time.sleep(1)
