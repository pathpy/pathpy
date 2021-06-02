#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_core.py -- Test environment for the core classes
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2021-06-02 14:17 juergen>
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
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
