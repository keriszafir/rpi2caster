from setuptools import setup, find_packages

long_description = """
Typesetting and casting software for a Raspberry Pi-based computer control
attachment for Monotype composition casters.

This program suite consists of three major parts:

1. Typesetting program for parsing UTF-8 text, calculating justification 
   and coding it as a series of control codes accepted by the Monotype composition caster,
2. Casting program for sending said codes to the casting machine using an interface with 
   32 pneumatic outputs, a pneumatic connection block attached to the caster's paper tower
   and a machine cycle sensor input. The program also allows to cast sorts, test the machine
   or set a short text on-the-fly, then cast the composed type.
3. Inventory management program for adding, editing and deleting the definitions for
   replaceable machine components: normal wedges and matrix cases (diecases).

The workflow is as follows:
1. define matrix case layouts for your matrix cases (and edit if needed),
2. define your normal wedges so that the program knows what series in which set widths you have,
3. use a typesetting program to generate a "ribbon" i.e. series of control codes from a text,
   for a specified matrix case and normal wedge,
4. use the casting program to test the machine/interface, perform machine adjustments, and cast
   the type from ribbon you made earlier.
"""

setup(name='rpi2caster',
      version='0.1dev4',
      description='Raspberry Pi controls a Monotype composition caster',
      long_description=long_description,
      url='http://github.com/elegantandrogyne/rpi2caster',
      author='Christophe Slychan',
      author_email='krzysztof.slychan@gmail.com',
      license='GPLv3',
      zip_safe=False,
      #tests.suite='nose.collector',
      #tests.require=['nose'],
      classifiers=['Development Status :: 2 - Pre-Alpha',
                   'Intended Audience :: Manufacturing',
                   'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                   'Natural Language :: English',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 3 :: Only',
                   'Topic :: Artistic Software'],
      keywords=['Monotype', 'typography', 'printing', 'letterpress', 'typesetting', 'typecasting', 'Raspberry Pi'],
      packages=find_packages(exclude=['tests']),
      entry_points={'console_scripts':['rpi2caster = rpi2caster:main']})
