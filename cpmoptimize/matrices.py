#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import izip

class Matrix(object):
    def __init__(self, content):
        self.content = content
    
    @classmethod
    def identity(cls, side):
        return cls([
            [
                int(i == j) for j in xrange(side)
            ] for i in xrange(side)
        ])
        
        
    @property
    def rows(self):
        return len(self.content)
        
    @property
    def cols(self):
        try:
            return len(self.content[0])
        except IndexError:
            return 0
    
    
    def _do_mul(self, other):
        return Matrix([
            [
                sum(
                    (
                        self.content[y][k] * other.content[k][x]
                    ) for k in xrange(self.cols)
                ) for x in xrange(other.cols)
            ] for y in xrange(self.rows)
        ])
    
    def __mul__(self, other):
        if not isinstance(other, Matrix):
            raise TypeError((
                "Can't multiply %s matrix by non-matrix object " +
                "with type %s"
            ) % (self.size_repr(), type(other)))
        if self.cols != other.rows:
            raise ValueError((
                "First %s matrix isn't matches to " +
                "second %s matrix by sizes in multiplication"
            ) % (self.size_repr(), other.size_repr()))
        return self._do_mul(other)
    
    def __pow__(self, n):
        if self.rows != self.cols:
            raise ValueError((
                "Can't construct power of non-square %s matrix"
            ) % self.size_repr())
        
        # Construct power of matrix with O(log(n)) asymptotics and
        # some optimizations with bit operations
        res = Matrix.identity(self.rows)
        if not n:
            return res
        while True:
            if n & 1:
                res = res._do_mul(self)
                if n == 1:
                    return res
            self = self._do_mul(self)
            n >>= 1


    def size_repr(self):
        return '%sx%s' % (self.rows, self.cols)
    
    def __str__(self):
        reprs = [
            [
                repr(elem) for elem in row
            ] for row in self.content
        ]
        elem_width = max(
            max(
                len(elem) for elem in row
            ) for row in reprs
        )
        return '\n'.join(
            ' '.join(
                elem.rjust(elem_width) for elem in row
            ) for row in reprs
        )
    
    def __repr__(self):
        return 'Matrix %s:\n' % self.size_repr() + str(self)
    
    
    def transposed(self):
        return Matrix(map(list, izip(*self.content)))
