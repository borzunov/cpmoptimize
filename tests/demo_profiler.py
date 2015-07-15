#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import traceback

sys.path.append(os.path.pardir)
from cpmoptimize import cpmoptimize


# Recompile-time exceptions

@cpmoptimize(verbose=sys.stderr)
def unsupported_instr():
    res = 0
    for i in xrange(6000):
        if i < 100:
            res += 1
        else:
            res += 2
    return res

@cpmoptimize(verbose=sys.stderr)
def unpredictable_operands():
    res = 1
    for i in xrange(6000):
        res *= res
    return res

@cpmoptimize(verbose=sys.stderr)
def unallowed_constant():
    res = ''
    for i in xrange(6000):
        res += 'a'
    return res

@cpmoptimize(verbose=sys.stderr)
def fib(a_start, iterator):
    a = a_start
    b = 1
    for i in iterator:
        a, b = b, a + b
    return a


# Run-time exceptions

fib(0, range(6000))
fib(0.5, xrange(6000))


fib(0, xrange(1000)) # Skipped optimization
fib(0, xrange(6000)) # Successful optimization
