# -*- coding: utf-8 -*-
"""Setuptools for rpi2caster."""

from setuptools import setup, find_packages
from rpi2caster import __version__

with open('README.rst', 'r') as readme_file:
    long_description = readme_file.read()

clas = ['Development Status :: 3 - Alpha',
        'Intended Audience :: Manufacturing',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Artistic Software']

setup(name='rpi2caster',
      version=__version__,
      description='Raspberry Pi controls a Monotype composition caster',
      long_description=long_description,
      url='http://github.com/elegantandrogyne/rpi2caster',
      author='Christophe Slychan',
      author_email='krzysztof.slychan@gmail.com',
      license='GPLv3',
      zip_safe=True,
      include_package_data=True,
      classifiers=clas,
      extras_require={'driver-wiringpi': ['wiringpi >= 2.3'],
                      'driver-gpiozero': ['gpiozero >= 1.0'],
                      'driver-sysfs': ['gpiodaemon >= 0.5'],
                      'driver-parallel': ['pyparallel >= 0.2'],
                      'database-postgresql': ['psycopg2 >= 2.6'],
                      'database-sqlite': ['sqlite >= 0.9'],
                      'database-mysql': ['PyMySQL >=0.6']},
      install_requires=['pip > 1.5', 'click > 6.0', 'sqlalchemy > 1.1'],
      keywords=['Monotype', 'typography', 'printing', 'letterpress',
                'typesetting', 'typecasting', 'Raspberry Pi'],
      packages=find_packages(exclude=['data', 'docs', 'tests']),
      entry_points={'console_scripts':
                    ['rpi2caster = rpi2caster.rpi2caster:main']})
