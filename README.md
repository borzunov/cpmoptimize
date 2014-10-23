cpmoptimize
===========

Decorator for automatic algorithms optimization via fast matrix exponentiation

Installation
------------

To install the package, extract it and run:

    python setup.py install

Dependencies (`byteplay >= 0.2`) will be installed automatically.

Basic Example
-------------

Let we want to calculate ten millionth Fibonacci number in Python. The function with trivial algorithm is rather slow:

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

But if we would use the described decorator the function will be able to figure out the answer much faster:

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

Explanation
-----------

Actually the decorator disassembles and analyzes function's bytecode and tries to optimize applied algorithm and reduce it's complexity.

Disassembling bytecode performs using pretty [byteplay](https://pypi.python.org/pypi/byteplay) library. This is the reason that the project is written in Python 2 branch.

The decorator uses the method implemented by [Alexander Skidanov](https://github.com/SkidanovAlex) in his experimental simple optimizing [interpreter](https://github.com/SkidanovAlex/interpreter).

This interpreter supports the following operations with numeric variables:

```python
# Assign another variable or a constant
x = y
x = 2

# Add or subtract another variable or a constant
x += y
x += 2
x -= y
x -= 3

# Multiply by a constant
x *= 4

# Run a loop with a constant number of iterations
loop 100000
    ...
end
```

The interpreter can represent every supported operation as a special square matrix. To perform the operation is necessary to multiply a vector with old variables' values by this matrix and obtain a vector with new values:

![Performing the operation](http://habrastorage.org/files/3b6/e12/ec6/3b6e12ec6c4b4ed083dca38f5c3d6b0f.png)

To perform a sequence of the operations is necessary to multiply vector by all corresponding matrices. Another method is to multiply matrices first and then multiply source vector by the resulting product (using associativity of matrix multiplication):

![Performing the sequence of the operations](http://habrastorage.org/files/902/b25/58b/902b2558b1da4984925bc84dd028de65.png)

To perform the loop we should compute a number *n* (number of loop's iterations) and a matrix *B* (product of the corresponding matrices in the loop's body). Then we should multiply source vector by *B* for *n* times. Another method is to construct the *n*-th power of the matrix *B* and then multiply source vector to the result:

![Performing the loop](http://habrastorage.org/files/1e8/dae/5bc/1e8dae5bcc874648abb3686adbc3274d.png)

To speed up these operations and reduce its' complexity we can use the algorithm of [exponentiation by squaring](https://en.wikipedia.org/wiki/Exponentiation_by_squaring).

If the loop isn't operates with big numbers and [arbitrary-precision arithmetic](https://en.wikipedia.org/wiki/Arbitrary-precision_arithmetic), it allows to change loop's complexity from *O(n)* to *O(log n)*. In this case we can execute a loops with _10 ** 1000_ iterations less than one second:

```python
from cpmoptimize import cpmoptimize, xrange

@cpmoptimize()
def f(n):
    step1 = 1
    step2 = 1
    res = 1
    for i in xrange(n):
        res += step2
        step2 += step1
        step1 += 1
    return res

print f(10 ** 1000)

# Time: 445 ms
```

Even if loop operates with big numbers (as in the example with the Fibonacci numbers above), complexity is also reduced (but not so much). This can be seen in the following chart:

![Comparison of the execution time of function with naive algorithm and automatically optimized function](http://habrastorage.org/files/785/fbe/249/785fbe249f084eda977b853ceb8981a9.png)

More Examples
-------------

You can see the comparison of the execution time with other algorithms for computing Fibonacci numbers and learn more benchmarks in "*tests/*" directory in the project sources. If *matplotlib* is installed on your system, you can also make the corresponding plots.

Library Interface
-----------------

Library name comes from the words "<i><b>c</b>ompute the <b>p</b>ower of a <b>m</b>atrix and <b>optimize</b></i>". It contains two elements.

### Reimplemented *xrange*

cpmoptimize.<strong>xrange</strong>(<i>stop</i>)

cpmoptimize.<strong>xrange</strong>(<i>start</i>, <i>stop</i>[, <i>step</i>])

Built-in *xrange* in Python 2 doesn't support long integers as its' arguments (passing them leads to *OverflowError*).

Since our library can run loops with _10 ** 1000_ and more iterations in a short time, it provides it's own implementation of *xrange*. This implementation supports all features of original *xrange* and moreover arguments with type *long*.

However, if in your case the number of iterations in the loops is small, you can continue to use built-in *xrange*.

### Function *cpmoptimize*

cpmoptimize.<strong>cpmoptimize</strong>(<i>strict</i>=False, <i>iters_limit</i>=5000, <i>types</i>=(int, long), <i>opt_min_rows</i>=True, <i>opt_clear_stack</i>=True)

#### Applying the decorator

*cpmoptimize* function accepts optimization settings and returns the decorator that consider these settings. You can apply this decorator with special syntax with "*@*" symbol or without it:

```python
from cpmoptimize import cpmoptimize

@cpmoptimize()
def f(n):
    # Code

def naive_g(n):
    # Code

smart_g = cpmoptimize()(naive_g)
```

Before modifying function's bytecode will be copied. Thus in code above only *f* and *smart_g* functions will be optimized.

#### Search *for* loops

The decorator look for normal *for* loops in function's bytecode. *while* loops, generator expressions and list comprehensions are ignored. Nested loops are not supported yet (only innermost loop is optimized). Constructions *for-else* are handled correctly.

#### Allowed types

Complex types can have user-defined side effects on application different operators. Changing the order of application of these operators can disrupt the proper program's behavior.

Further, during operations with matrices variables are added and multiplied implicitly, so the types of variables are shuffling. If one of the constants or variables would be of type *float*, the variables that would have type *int* after the code, could also get the type *float* (since the addition of *int* and *float* returns *float*). This behavior can cause errors and is also unacceptable.

For these reasons, decorator optimizes loops only if all the variables and constants in them have one of an *allowed types*. By default only *int* and *long* types and its' heirs are allowed (shuffling of these types usually does not cause undesirable effects).

To change set of allowed types, you should place a tuple of the relevant types to the __*types*__ argument. Types from this tuple and its' heirs will be considered as allowed (it will be checked by calling *isinstance(value, types)*).

#### Loop optimization conditions

...

#### Parameter *iters_limit*

...

#### Flag *strict*

...

#### Option *verbose*

...

#### Options of advanced optimization

...

Application
-----------

...

What's next?
------------

...

Author
------

Copyright (c) 2014 Alexander Borzunov

A detailed article and discussion in Russian: http://habrahabr.ru/post/236689/
