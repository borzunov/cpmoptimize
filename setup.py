#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

from cpmoptimize import __version__ as version


project_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(project_dir, 'README.rst')) as f:
    long_description = f.read()

setup(
    name="cpmoptimize",
    version=version,
    packages=['cpmoptimize'],

    install_requires=['byteplay>=0.2'],

    author="Alexander Borzunov",
    author_email="borzunov.alexander@gmail.com",

    description='A decorator for automatic algorithms optimization '
                'via fast matrix exponentiation',
    long_description=long_description,
    url="http://github.com/borzunov/cpmoptimize",

    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    license="MIT",
    keywords=['optimize', 'matrix', 'bytecode'],
)
