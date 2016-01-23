#!/usr/bin/env python3
"""debug-cast

Used for casting actual type, but in debugging mode.
"""
from rpi2caster import casting, monotype
monotype.UI.DEBUG_MODE = True
job = casting.Casting()
job.caster = monotype.Monotype()


def main():
    casting.main_menu(job)


if __name__ == '__main__':
    main()
