===========
cpmoptimize
===========

A decorator for automatic algorithms optimization via fast matrix exponentiation

.. image:: https://img.shields.io/travis/borzunov/cpmoptimize/master.svg
    :target: https://travis-ci.org/borzunov/cpmoptimize

.. image:: https://img.shields.io/pypi/v/cpmoptimize.svg
    :target: https://pypi.python.org/pypi/cpmoptimize

.. image:: https://img.shields.io/pypi/pyversions/cpmoptimize.svg
    :target: https://pypi.python.org/pypi/cpmoptimize

.. image:: https://img.shields.io/pypi/implementation/cpmoptimize.svg
    :target: https://pypi.python.org/pypi/cpmoptimize

Description
-----------

The decorator disassembles the function's bytecode and tries to reduce the algorithm's time complexity using the fast matrix exponentiation.

**Detailed description:** Russian_, English_.

.. _English: http://kukuruku.co/hub/algorithms/automatic-algorithms-optimization-via-fast-matrix-exponentiation
.. _Russian: http://habrahabr.ru/post/236689/

Inspired by the `Alexander Skidanov`_'s `optimizing interpreter`_.

.. _Alexander Skidanov: https://github.com/SkidanovAlex
.. _optimizing interpreter: https://github.com/SkidanovAlex/interpreter

Example
-------

Suppose we want to calculate the ten millionth `Fibonacci number`_ using a program in Python. The function with a trivial algorithm is rather slow:

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
