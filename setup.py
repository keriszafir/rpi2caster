from setuptools import setup, find_packages

with open('README.rst', 'r') as readme_file:
    long_description = readme_file.read()

setup(name='rpi2caster',
      version='0.1.dev11',
      description='Raspberry Pi controls a Monotype composition caster',
      long_description=long_description,
      url='http://github.com/elegantandrogyne/rpi2caster',
      author='Christophe Slychan',
      author_email='krzysztof.slychan@gmail.com',
      license='GPLv3',
      zip_safe=True,
      include_package_data=True,
      data_files=[('/var/local/rpi2caster', ['data/rpi2caster.db']), ('/etc', ['data/rpi2caster.conf'])],
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
      packages=find_packages(exclude=['data', 'docs', 'tests']),
      entry_points={'console_scripts':['rpi2caster = rpi2caster.__main__:main']},
      install_requires=['wiringpi2 >= 1.1'])
