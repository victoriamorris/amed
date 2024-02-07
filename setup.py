#!/usr/bin/env python
# -*- coding: utf8 -*-

"""setup.py file for amed_tools."""

# Import required modules
from distutils.core import setup

__author__ = 'Victoria Morris'
__license__ = 'MIT License'
__version__ = '3.0.0'
__status__ = '4 - Beta Development'

# List requirements.
# All other requirements should all be contained in the standard library
requirements = [
    'regex',
    'sqlite3'
]

# Setup
setup(
    console=[
        'bin/amed_pre.py',
        'bin/amed_post.py',
    ],
    zipfile=None,
    options={
        'py2exe': {
            'bundle_files': 0,
        }
    },
    name='amed',
    version='3.0.0',
    author='Victoria Morris',
    url='https://github.com/victoriamorris/AMED',
    license='MIT',
    description='Scripts for processing AMED files.',
    long_description='Scripts for processing AMED files.',
    packages=['amed_tools',],
    scripts=[
        'bin/amed_pre.py',
        'bin/amed_post.py',
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
