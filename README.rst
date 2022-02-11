===========
cpmoptimize
===========

.. image:: https://img.shields.io/pypi/v/cpmoptimize.svg?color=blue
    :target: https://pypi.python.org/pypi/cpmoptimize

.. image:: https://img.shields.io/pypi/pyversions/cpmoptimize.svg
    :target: https://pypi.python.org/pypi/cpmoptimize

.. image:: https://img.shields.io/pypi/implementation/cpmoptimize.svg
    :target: https://pypi.python.org/pypi/cpmoptimize

Description
-----------

This library provides a decorator that disassembles the function's bytecode, checks if it calculates linear recurrences, and tries to reduce the algorithm's time complexity from O(n) to O(log n) using the `fast matrix exponentiation`_.

.. _fast matrix exponentiation: https://en.wikipedia.org/wiki/Exponentiation_by_squaring

**Detailed description:** Russian_, English_.

.. _English: http://kukuruku.co/hub/algorithms/automatic-algorithms-optimization-via-fast-matrix-exponentiation
.. _Russian: http://habrahabr.ru/post/236689/

Inspired by the `Alexander Skidanov`_'s `optimizing interpreter`_.

.. _Alexander Skidanov: https://github.com/SkidanovAlex
.. _optimizing interpreter: https://github.com/SkidanovAlex/interpreter

**Update (Feb 2022):** This library was created in 2014 and only supports Python 2.6-2.7 (not Python 3). I don't plan to upgrade it myself but I'd be happy to help anyone willing to do that (this is a good exercise to understand how it works). If you're interested, please open an issue.

Example
-------

Suppose we want to calculate the ten millionth `Fibonacci number`_ in Python. The function with a trivial algorithm is rather slow:

.. code:: python

    def fib(n):
        a = 0
        b = 1
        for i in xrange(n):
            a, b = b, a + b
        return a

    result = fib(10 ** 7)

    # Time: 25 min 31 sec

But if we apply the optimizing decorator, the function will give you the answer much faster:

.. code:: python

    from cpmoptimize import cpmoptimize

    @cpmoptimize()
    def fib(n):
        a = 0
        b = 1
        for i in xrange(n):
            a, b = b, a + b
        return a

    result = fib(10 ** 7)

    # Time: 18 sec (85x faster)

.. _Fibonacci number: https://en.wikipedia.org/wiki/Fibonacci_number

Installation
------------

You can install the stable version of the library using pip::

    sudo pip install cpmoptimize

Or install a previously downloaded and extracted package::

    sudo python setup.py install

Author
------

Copyright (c) 2014, 2015 Alexander Borzunov
