#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_core.py -- Test environment for the core classes
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-06-07 13:26 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================

import pytest
from collections import Counter
from pathpy.core.core import (
    PathPyPath,
    PathPyCollection,
    PathPySet,
    PathPyRelation,
    PathPyEmpty,
    PathPyCounter)


def test_PathPyEmpty():
    """Test the PathPyEmpty"""
    u = PathPyEmpty('u')
    assert u.uid == 'u'


def test_PathPyPath():
    """Test the PathPyPath"""

    p = PathPyPath('a')

    p = PathPyPath()

    p = PathPyPath(uid='a')


def test_PathPyCollection_add_PathPyPath():
    """Test the PathPyCollection"""

    paths = PathPyCollection()
    a = PathPyPath('a', uid='a')
    b = PathPyPath('b', uid='b')
    p1 = PathPyPath(a, b, uid='p1')
    p2 = PathPyPath('a', 'b', 'c', uid='p2')

    paths.add(p1)

    assert len(paths) == 1
    assert p1 in paths and p2 not in paths

    paths.add(p2)
    assert len(paths) == 2
    assert p1 and p2 in paths
    assert paths.counter['p1'] == 1

    paths.add(p1)
    assert paths.counter['p1'] == 2

    paths.add(p1, count=8)
    assert paths.counter['p1'] == 10


def test_PathPyCollection_add_str():
    """Test the PathPyCollection"""

    paths = PathPyCollection(directed=False, multiple=False)
    paths.add('a', 'b', 'c', uid='p1', frequency=44)
    paths.add('c', 'b', 'a', uid='p2', frequency=11)

    assert 'p1' in paths
    assert ('a', 'b', 'c') in paths


def test_PathPySet():
    """Test the set for pathpy objects"""

    s = PathPySet(('a', 'b', 'c', 'd'))
    f = frozenset(('a', 'c', 'b', 'd'))

    assert s == f
    assert 'a' and 'b' and 'c' and 'd' in s
    assert len(s) == 4


def test_PathPyRelation():
    """Test relational object"""

    r1 = PathPyRelation(('a', 'b', 'c'), ordered=True, directed=False)
    r2 = PathPyRelation(('c', 'b', 'a'), ordered=True, directed=False)

    assert r1 == r2


def test_PathPyIter():
    """Test the Object iterator"""
    path = PathPyPath('a', 'b', 'c', 'd', 'a', 'b', uid='p1')

    assert [n.uid for n in path] == ['a', 'b', 'c', 'd', 'a', 'b']


def test_PathPyPath_subobjects():
    """Get subobjects of a path"""

    a = PathPyPath('a')
    b = PathPyPath('b')
    c = PathPyPath('c')

    e1 = PathPyPath(a, b, uid='e1')
    e2 = PathPyPath(b, c, uid='e2')

    p = PathPyPath(e1, e2, uid='p1')

    assert ('a',) in p.subobjects(depth=3)


def test_PathPyCollection_add_diff():
    """Test to add similar and different objects to the collection"""

    p1 = PathPyPath('a', 'x', 'c', uid='a-x-c')

    # create counter NO MULTIPLE objects are allowed
    pc = PathPyCollection(multiple=True)

    # add a new object to the collection
    pc.add(p1)

    assert len(pc) == 1
    assert p1 in pc

    # add the same (ptyhon) object again to the collection
    pc.add(p1)

    # add a different (python) object with same uid and relations
    p2 = PathPyPath('a', 'x', 'c', uid='a-x-c')
    pc.add(p2)

    # generate new object within the collection having the same uid
    pc.add('a', 'x', 'c', uid='a-x-c')

    # add a different (python) object with same relations but different uid
    p3 = PathPyPath('a', 'x', 'c', uid='a-x-c-2')
    pc.add(p3)

    # generate new object within the collection having a different uid
    pc.add('a', 'x', 'c', uid='a-x-c-3')

    # add a different (python) object with same relations but no uid
    p4 = PathPyPath('a', 'x', 'c')
    pc.add(p4)

    # generate new object within the collection having no uid
    pc.add('a', 'x', 'c')

    assert len(pc.counter) == 5


def test_PathPyCollection_counter():
    """Test the counter of the collection object"""
    col = PathPyCollection()

    col.add('a', uid='a')
    assert len(col) == 1

    assert col.counter['a'] == 1

    col.add('a', count=100)

    assert col.counter['a'] == 101

    col.counter['a'] = 20
    assert col.counter['a'] == 20

    col.remove('a')
    assert len(col) == 0
    assert col.counter['a'] == 0

    col = PathPyCollection(ordered=False)
    col.add('a', 'b', 'c', uid='p1', count=10)
    assert col.counter['p1'] == 10
    assert col.counter['a', 'b', 'c'] == 10
    assert col.counter['b', 'a', 'c'] == 10
    assert col.counter['c', 'b', 'a'] == 10

    col.counter['c', 'a', 'b'] = 100
    assert col.counter['p1'] == 100

    col.add('a', 'c', uid='p2')
    assert len(col.counter) == 2


def test_PathPyCollection_iadd():
    """add other collection"""

    c1 = PathPyCollection()
    c1.add('a', 'b', uid='ab', count=20, color='red')

    c2 = PathPyCollection()
    c2.add('x', 'y', uid='xy', count=5, color='green')

    assert len(c1) == 1
    c1 += c2

    assert len(c1) == 2
    assert ('x', 'y') in c1
    assert c1.counter['ab'] == 20
    assert c1.counter['xy'] == 5

    c3 = PathPyCollection()
    c3.add('a', 'b', count=10, color='blue')

    c1 += c3
    assert c1.counter['ab'] == 30
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
