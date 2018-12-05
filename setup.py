# -*- coding: utf-8 -*-
"""Setuptools for rpi2caster."""

from setuptools import setup, find_packages

# global package-wide declarations
__version__ = '2.1.dev2'
__author__ = 'Christophe Catherine Slychan'
__author_email__ = 'krzysztof.slychan@gmail.com'
__github_url__ = 'http://github.com/elegantandrogyne/rpi2caster'
__dependencies__ = ['pip > 1.5', 'click > 6.0', 'peewee > 2.0',
                    'qrcode > 5.0', 'requests > 2.0', 
                    'librpi2caster >= 2.0'],

with open('README.rst', 'r') as readme_file:
    long_description = readme_file.read()

clas = ['Development Status :: 4 - Beta',
        'Intended Audience :: Manufacturing',
        ('License :: OSI Approved :: '
         'GNU General Public License v3 or later (GPLv3+)'),
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Artistic Software']

setup(name='rpi2caster',
      version=__version__,
      description='Machine control software for Monotype composition casters',
      long_description=long_description,
      url='http://github.com/elegantandrogyne/rpi2caster',
      author=__author__,
      author_email='krzysztof.slychan@gmail.com',
      license='GPLv3',
      zip_safe=True,
      include_package_data=True,
      classifiers=clas,
      install_requires=__dependencies__,
      keywords=['Monotype', 'typography', 'printing', 'letterpress',
                'typesetting', 'typecasting', 'Raspberry Pi'],
      packages=find_packages(exclude=['data', 'docs', 'tests']),
      entry_points={'console_scripts': ['rpi2caster = rpi2caster:cli']})
