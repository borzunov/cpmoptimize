#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = "cpmoptimize",
    version = "0.1",
    packages = find_packages(),
    
    install_requires = ['byteplay>=0.2'],

    author = "Alexander Borzunov",
    author_email = "hxrussia@gmail.com",
    description = "Library for automatic algorithms optimization via fast matrix exponentiation",
    license = "MIT",
    keywords = "optimize matrix bytecode",
    url = "http://github.com/borzunov/cpmoptimize",
)
