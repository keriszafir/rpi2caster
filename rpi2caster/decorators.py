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
        mode = self.caster.mode
        UI.debug_pause('About to %s...' %
                       (mode.casting and 'cast composition' or
                        mode.testing and 'test the outputs' or
                        mode.calibration and 'calibrate the machine' or
                        mode.punching and 'punch the ribbon'))
        # Instantiate and enter context
        sensor, output = mode.casting_backend
        with sensor() as self.caster.sensor:
            with output() as self.caster.output:
                with self.caster:
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
                self.cast_codes(ribbon)
        except CastingAborted:
            pass
        finally:
            # Reset diagnostics and row 16 addressing modes
            mode.kmn = False
            mode.hmn = False
            mode.unitshift = False
            mode.diagnostics = False
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
        old_measure = self.measure
        self.measure = Measure(manual_choice=True)
        retval = routine(self, *args, **kwargs)
        self.measure = old_measure
        return retval
    return wrapper