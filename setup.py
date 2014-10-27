#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name = "cpmoptimize",
    version = "0.2",
    packages = ['cpmoptimize'],
    
    install_requires = ['byteplay>=0.2'],

    author = "Alexander Borzunov",
    author_email = "hxrussia@gmail.com",
    description = "Library for automatic algorithms optimization via fast matrix exponentiation",
    license = "MIT",
    keywords = "optimize matrix bytecode",
    url = "http://github.com/borzunov/cpmoptimize",
    download_url = 'https://github.com/borzunov/cpmoptimize/archive/v0.2.tar.gz',
)
