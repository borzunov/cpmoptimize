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

But if we use the described decorator the function will be able to figure out the answer much faster:

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

Actually the decorator disassembles and analyzes function's bytecode and tries to optimize applied algorithm and reduce its complexity.

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

To speed up these operations and reduce their complexity we can use the algorithm of [exponentiation by squaring](https://en.wikipedia.org/wiki/Exponentiation_by_squaring).

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

Built-in *xrange* in Python 2 doesn't support long integers as their arguments (passing them leads to *OverflowError*).

Since the library can run loops with _10 ** 1000_ and more iterations in a short time, it provides its own implementation of *xrange*. This implementation supports all features of original *xrange* and moreover arguments with type *long*.

However, if in your case the number of iterations in the loops is small, you can continue to use built-in *xrange*.

### Function *cpmoptimize*

cpmoptimize.<strong>cpmoptimize</strong>(<i>strict</i>=False, <i>iters_limit</i>=5000, <i>types</i>=(int, long), <i>opt_min_rows</i>=True, <i>opt_clear_stack</i>=True, <i>verbose</i>=None)

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

Further, during operations with matrices variables are added and multiplied implicitly, so the types of variables are shuffling. If one of the constants or variables have type *float*, the variables that would have type *int* after the code could also get the type *float* (since the addition of *int* and *float* returns *float*). This behavior can cause errors and is also unacceptable.

For these reasons, decorator optimizes loops only if all the variables and constants in them have one of an *allowed types*. By default only *int* and *long* types and their heirs are allowed (shuffling of these types usually does not cause undesirable effects).

To change set of allowed types, you should place a tuple of the relevant types to the __*types*__ argument. Types from this tuple and their heirs will be considered as allowed (it will be checked by calling *isinstance(value, types)*).

#### Loop optimization conditions

Every found loop must satisfy a number of conditions. Some of them are checked at the stage of application of the decorator (during the bytecode analysis):

1. Loop's body must contain only assignment instructions and unary and binary operations, which may be arranged in a complex expressions. It can't contain conditions, function calls, *return* and *yield* operators etc.

2. Operands must satisfy the *predictability* conditions:

    * All operands of addition and subtraction and operand of the unary minus can be unpredictable.
    
    * At least one operand of multiplication must be predictable (similarly that only multiplication by a constant is allowed in the original interpreter).
    
    * All operands of exponentiation, division, taking the remainder and bitwise operations must be predictable.
    
3. All constant used in the loop must have allowed type.

If these conditions are satisfied, a special *hook* is installed to bytecode before the loop (the loop's original bytecode isn't removed). This hook will check the remaining conditions, which can be checked only immediately before the start of the loop due the dynamic typing in Python:

1. The object that the loop iterates must have built-in type *xrange* or its reimplementation *cpmoptimize.xrange*. Slow *range* function isn't supported.

2. Values of all variables used in the loop must have allowed type.

If the hook has concluded that optimization is admissible, the corresponding matrices will be calculated, and then values of used variables will change to the new ones. Otherwise the loop's original bytecode will be executed.

#### Loop-invariant code motion

Despite the fact that the described method doesn't support exponentiation and bitwise operations, the following code will be optimized:

```python
@cpmoptimize()
def f(n, k):
    res = 0
    for i in xrange(n):
        m = 3
        res += ((k ** m) & 676) + i
    return res
```

When analyzing the bytecode the decorator concludes that the values of variables *k* and *m* in the expression _(k ** m) & 676_ don't depend on which iteration of the loop they are used, therefore the value of the whole expression doesn't change. It's enough to compute this value once moving relevant instructions and executing them immediately before the start of the loop. The source code will be converted to a code similar to the following:

```python
@cpmoptimize()
def f(n, k):
    res = 0
    m = 3
    _const1 = (k ** m) & 676
    for i in xrange(n):
        res += _const1 + i
    return res
```

It's important that the invariant values are calculated every time on calling function because they can depend on global variables and function's parameters (for example, *_const1* depends on parameter *k*). Now it's easy to optimize the resulting code via operations with a matrices.

The aforesaid checking of values predictability is perfomed at the same time. For example, if one of operands of bitwise AND have been unpredictable, this operation can no longer be taken out of the loop and optimization could not be applied.

Also the decorator partially supports multiple assignments. If they contains a few elements, Python generate supported bytecode without using tuples:

```python
a, b = b, a + b
```

#### Parameter *iters_limit*

An optimized loop may run slower on a small number of iterations (it can be seen at the chart above) because it requires some time to construct the matrices and check the types. You can set the __*iters_limit*__ parameter to neutralize this effect. Then hook will check number of the iterations in the loop before executing optimization and will cancel optimization if this number doesn't exceed the given parameter.

The limit is set to *5000* by default. It can't be set lesser than *2* iterations.

It's clear that the best value of the parameter is the point of intersection of the lines on the chart corresponding to the execution time of the original and optimized variants of the function. Then the function can choose the fastest algorithm in each case:

![Choosing different algorithms in the different cases](http://habrastorage.org/files/854/2e0/75a/8542e075adca431596cc575474a4ba71.png)

#### Flag *strict*

Sometimes it's necessary to apply the optimization. For example, program will hang if a loop with _10 ** 1000_ iterations will not be optimized. Flag __*strict*__ is created for such cases. It's disabled by default, but if you enable it, program will throw exception if one of normal *for* loops will not be optimized.

If the optimization fails at the stage of application the decorator, *cpmoptimize.recompiler.RecompilationError* will be raised. For example, let's try to multiply two unpredictable variables:

```python
>>> from cpmoptimize import cpmoptimize
>>>
>>> @cpmoptimize(strict=True)
... def f(n, k):
...     res = 0
...     for i in xrange(n):
...         res += i * res
...     return res
... 
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "cpmoptimize/__init__.py", line 100, in upgrade_func
    index += analyze_loop(settings, code, index) + 1
  File "cpmoptimize/__init__.py", line 59, in analyze_loop
    raise err
cpmoptimize.recompiler.RecompileError: Multiplication of two unpredictable values is unsupported
```

If the optimization fails during the checks in the hook (it was found that the iterator or variables types aren't supported), *TypeError* will be raised:

```python
>>> from cpmoptimize import cpmoptimize
>>>
>>> @cpmoptimize(strict=True)
... def f(iterable):
...     res = 0
...     for elem in iterable:
...         res += elem
...     return res
... 
>>> f(xrange(30))
435
>>> f(range(30))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<stdin>", line 4, in f
  File "cpmoptimize/hook.py", line 170, in exec_loop
    raise err
TypeError: Iterator in optimized loops must have type "xrange" instead of <type 'list'>
```

#### Options of advanced optimization

Flags *opt_min_rows* and *opt_clear_stack* are responsible for using additional methods of optimizing during constructing of the matrices. They are enabled by default and can be disabled only for demonstration purposes.

Usually the multiplication of long numbers in some cells of generated matrices takes most of the execution time of the optimized code. Multiplication of the other cells is negligible in comparison with this time-consuming process.

During recompilation the decorator creates temporary, *virtual* variables corresponding to the positions of the Python's interpreter stack. After complex computations they can contain long numbers that already saved in another, real variables. Actually we don't need to save these values and multiply they again during matrices multiplication. Option __*opt_clear_stack*__ enables mechanism of clearing these variables: if we assign them to zero at the end of their use, long values therein will disappear.

This option is particularly effective when program operates with very big numbers. Excluding of excess multiplications can speed up the program more than two times.

Option __*opt_min_rows*__ activates algorithm of reducing size of the used square matrices. Unnecessary rows and columns corresponding to unused and predictable variables will be excluded.

This option can speed up the program on a small number of the iterations, when the numbers were not very big yet and the dimensions of the matrix are important for execution time.

If you use both options at the same time, virtual variables begin to have predictable value (zero) and *opt_min_rows* works more efficiently. Therefore effectiveness of both options together is greater than effectiveness of each option separately.

The following chart shows the execution time for computing Fibonacci numbers during disabling different options ("*-m*" means that *opt_min_rows* is disabled, "*-c*" means that *opt_clear_stack* is disabled, "*-mc*" means that both options are disabled):

![Disabling options of advanced optimization](http://habrastorage.org/files/9af/7c0/076/9af7c007610b4880863cb5bb39a899ac.png)

#### Parameter *verbose*

__*verbose*__ option allows you to collect more information about failed and successful optimizations to profile your program and find reasons for which optimizations weren't applied. The parameter is set to *None* by default. To enable the option you should assign to the parameter a stream that will be used for writing debug messages (for example, *sys.stderr*).

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
