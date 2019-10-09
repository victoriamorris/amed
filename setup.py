#!/usr/bin/env python
# -*- coding: utf8 -*-

"""setup.py file for amed_tools."""

# Import required modules
import re
from distutils.core import setup

__author__ = 'Victoria Morris'
__license__ = 'MIT License'
__version__ = '1.0.0'
__status__ = '4 - Beta Development'

# Version
version = '2.0.0'

# Long description
long_description = ''

# List requirements.
# All other requirements should all be contained in the standard library
requirements = [
    'pyinstaller',
	'regex',
	'csv',
]

# Setup
setup(
    console=[
        'amed/amed_pre.py',
        'amed/amed_post.py',
    ],
    zipfile=None,
    options=None,
    name='amed',
    version=version,
    author='Victoria Morris',
    url='',
    license='MIT',
    description='Scripts for processing AMED files.',
    long_description=long_description,
    packages=['amed'],
    scripts=[
        'amed/amed_pre.py',
        'amed/amed_post.py',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python'
    ],
    requires=requirements
)
