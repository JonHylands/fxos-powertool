import os
from setuptools import setup, find_packages

# get documentation from the README
try:
    here = os.path.dirname(os.path.abspath(__file__))
    description = file(os.path.join(here, 'README.md')).read()
except (OSError, IOError):
    description = ''

# version number
version = {}
execfile(os.path.join('powertool', 'version.py'), version)

# dependencies
deps = ['yoctopuce==1.01.12553', 'numpy==1.7.1', 'pyserial']

setup(name='powertool',
      version=version['__version__'],
      description="Power consumption visualization and testing tool.",
      long_description=description,
      classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='mozilla',
      author='Jon Hylands, Dave Huseby',
      author_email='jhylands@mozilla.com, dhuseby@mozilla.com',
      url='https://developer.mozilla.org/en-US/Firefox_OS/Performance/Power',
      license='MPL',
      packages=['powertool'],
      zip_safe=False,
      entry_points={'console_scripts': [
          'powertool = powertool.powertool:main']},
      install_requires=deps)
