# -*- coding: utf-8 -*-
"""Decorator functions and classes for rpi2caster"""

# Start by choosing the user interface
from .global_config import UI
from .exceptions import CastingAborted
from .wedge_data import Wedge
from .measure import Measure


def choose_sensor_and_driver(casting_routine):
    """Checks current modes (simulation, perforation, testing)"""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        def debug():
            """Show some info"""
            UI.debug_pause('About to %s...' %
                           ('cast composition' if mode.casting
                            else 'test the outputs' if mode.testing
                            else 'calibrate the machine' if mode.calibration
                            else 'punch the ribbon' if mode.punching
                            else 'blow'))

        mode = self.caster.mode
        # Instantiate and enter context
        debug()
        with self.caster:
            debug()
            return casting_routine(self, *args, **kwargs)
    return wrapper


def cast_or_punch_result(ribbon_source):
    """Get the ribbon from decorated routine and cast it"""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        mode = self.caster.mode
        try:
            ribbon = ribbon_source(self, *args, **kwargs)
            if ribbon:
                self.cast_ribbon(ribbon)
        except CastingAborted:
            pass
        finally:
            # Reset row 16 addressing modes
            mode.kmn = False
            mode.hmn = False
            mode.unitshift = False
    return wrapper


def calibration_mode(routine):
    """Use a calibration mode for the routine.
    This will affect casting statistics and some prompts."""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        # Turn on the calibration mode
        self.caster.mode.calibration = True
        retval = routine(self, *args, **kwargs)
        # Reset the mode
        self.caster.mode.calibration = False
        return retval
    return wrapper


def testing_mode(routine):
    """Output testing mode - skip some steps in casting"""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        # Turn on the calibration mode
        self.caster.mode.testing = True
        retval = routine(self, *args, **kwargs)
        # Reset the mode
        self.caster.mode.testing = False
        return retval
    return wrapper


def temp_wedge(routine):
    """Assign a temporary alternative wedge for casting/calibration"""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        # Assign a temporary wedge
        old_wedge = self.wedge
        self.wedge = Wedge(wedge_name=self.wedge.name, manual_choice=True)
        UI.display_parameters({'Wedge parameters': self.wedge.parameters})
        UI.display('\n\n')
        retval = routine(self, *args, **kwargs)
        # Restore the former wedge and exit
        self.wedge = old_wedge
        return retval
    return wrapper


def temp_measure(routine):
    """Allow user to change measure i.e. line length"""
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        prompt = 'Current measure is %s, change it?' % self.measure
        if UI.confirm(prompt, False):
            # Change measure before, restore after
            old_measure = self.measure
            self.measure = Measure(self, value=None, manual_choice=True)
            retval = routine(self, *args, **kwargs)
            self.measure = old_measure
            return retval
        else:
            # Just do it
            return routine(self, *args, **kwargs)
    return wrapper


def singleton(cls):
    """Decorator function for singletons"""
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance
