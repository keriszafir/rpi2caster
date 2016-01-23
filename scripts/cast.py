#!/usr/bin/env python3
"""Cast

Used for casting actual type.
"""
from rpi2caster import casting, monotype
job = casting.Casting()
job.caster = monotype.Monotype()


def main():
    casting.main_menu(job)


if __name__ == '__main__':
    main()

