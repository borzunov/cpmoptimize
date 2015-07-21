cpmoptimize
===========

A decorator for automatic algorithms optimization via fast matrix exponentiation

Installation
------------

A library supports only Python 2.6 and 2.7 (including PyPy).

You can install the latest version of the library using [pip](https://pip.readthedocs.org/en/latest/):

    sudo pip install git+https://github.com/borzunov/cpmoptimize.git

Or install a previously downloaded and extracted package:

    sudo python setup.py install

Dependencies (`byteplay >= 0.2`) will be installed automatically.

Basic Example
-------------

Suppose we want to calculate the ten millionth [Fibonacci number](https://en.wikipedia.org/wiki/Fibonacci_number) using a program in Python. The function with a trivial algorithm is rather slow:

```python
def fib(n):
    a = 0
    b = 1
    for i in xrange(n):
        a, b = b, a + b
    return a

print fib(10 ** 7)

# Time: 25 min 31 sec
```

But if we apply the optimizing decorator, the function will give you the answer much faster:

```python
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
```

Description
-----------

Actually, the decorator disassembles and analyzes bytecode of a function and tries to reduce [time complexity](https://en.wikipedia.org/wiki/Time_complexity) of the algorithm used in it using [fast matrix exponentiation](https://en.wikipedia.org/wiki/Exponentiation_by_squaring).

The decorator uses a method implemented by [Alexander Skidanov](https://github.com/SkidanovAlex) in his simple optimizing [interpreter](https://github.com/SkidanovAlex/interpreter).

A detailed description of the library (including an idea explanation and an interface reference) is available in [English](http://kukuruku.co/hub/algorithms/automatic-algorithms-optimization-via-fast-matrix-exponentiation) and [Russian](http://habrahabr.ru/post/236689/).

Author
------

Copyright (c) 2014, 2015 Alexander Borzunov
