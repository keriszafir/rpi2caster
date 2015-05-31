#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
typesetter - program for generating the code sequence fed to
a Monotype composition caster or type&rule caster.

This program reads an input file (UTF-8 text file) or allows to enter
a string, then parses it, auto-hyphenates (with TeX hyphenation algorithm),
calculates justification figures and outputs the combinations of Monotype
signals, one by one, to the file or database. These sequences are to be read
and parsed by the casting program, which sends the signals to the machine.
"""

# IMPORTS, and warnings if package is not found in system:
unmetDependencies = []

# Typical libs, used by most routines:
import sys
import os
import time

# HTML/XML parser:
try:
    from bs4 import BeautifulSoup
except ImportError:
    unmetDependencies.append('BeautifulSoup: python-bs4')

# Warn about unmet dependencies:
if unmetDependencies:
    warning = 'Unmet dependencies - some functionality will not work:\n'
    for dep in unmetDependencies:
        warning += (dep + '\n')
    print warning
    time.sleep(2)

