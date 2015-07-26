===========
cpmoptimize
===========

A decorator for automatic algorithms optimization via fast matrix exponentiation

.. image:: https://img.shields.io/travis/borzunov/cpmoptimize.svg?style=flat-square
    :target: https://travis-ci.org/borzunov/cpmoptimize

.. image:: https://img.shields.io/pypi/v/cpmoptimize.svg?style=flat-square
    :target: https://pypi.python.org/pypi/cpmoptimize

Installation
------------

The library supports only Python 2.6 and 2.7 (including PyPy).

You can install the stable version of the library using pip::

    sudo pip install cpmoptimize

Or install a previously downloaded and extracted package::

    sudo python setup.py install

Basic Example
-------------

Suppose we want to calculate the ten millionth `Fibonacci number`_ using a program in Python. The function with a trivial algorithm is rather slow::

    def fib(n):
        a = 0
        b = 1
        for i in xrange(n):
            a, b = b, a + b
        return a

    print fib(10 ** 7)

    # Time: 25 min 31 sec

But if we apply the optimizing decorator, the function will give you the answer much faster::

    from cpmoptimize import cpmoptimize

    @cpmoptimize()
    def fib(n):
        a = 0
        b = 1
        for i in xrange(n):
            a, b = b, a + b
        return a

    print fib(10 ** 7)

    # Time: 18 sec (85x faster)

.. _Fibonacci number: https://en.wikipedia.org/wiki/Fibonacci_number

Description
-----------

Actually, the decorator disassembles bytecode of a function using pretty ``byteplay`` library, analyzes the code, and tries to reduce `time complexity`_ of the algorithm used in it using `fast matrix exponentiation`_.

.. _time complexity: https://en.wikipedia.org/wiki/Time_complexity
.. _fast matrix exponentiation: https://en.wikipedia.org/wiki/Exponentiation_by_squaring

The decorator uses a method implemented by `Alexander Skidanov`_ in his simple `optimizing interpreter`_.

.. _Alexander Skidanov: https://github.com/SkidanovAlex
.. _optimizing interpreter: https://github.com/SkidanovAlex/interpreter

A detailed description of the library (including an idea explanation and an interface reference) is available in English_ and Russian_.

.. _English: http://kukuruku.co/hub/algorithms/automatic-algorithms-optimization-via-fast-matrix-exponentiation
.. _Russian: http://habrahabr.ru/post/236689/

Author
------

Copyright (c) 2014, 2015 Alexander Borzunov
