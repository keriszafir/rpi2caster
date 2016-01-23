#!/usr/bin/env python3
"""Simulate

Casting simulation without an actual caster, for development/testing.
Uses a mockup caster class - simulation.Monotype.
"""
from rpi2caster import casting, simulation
job = casting.Casting()
job.caster = simulation.Monotype()
casting.ui.DEBUG_MODE = True


def main():
    casting.main_menu(job)


if __name__ == '__main__':
    main()
