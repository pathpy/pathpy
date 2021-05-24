#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_core.py -- Test environment for the core classes
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-05-24 15:36 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================

import pytest

from pathpy.core.core import PathPyPath, PathPyCollection, PathPySet, PathPyRelation, PathPyEmpty


def test_PathPyEmpty():
    """Test empty element"""
    u = PathPyEmpty('u')
    print(u.uid)


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

    r = PathPyRelation(('a', 'b', 'c'), ordered=True, directed=False)
    print(r)
    print(type(r))


def test_PathPyIter():
    """Test the Object iterator"""
    path = PathPyPath('a', 'b', 'c', 'd', 'a', 'b', uid='p1')
    # print(path.relations)
    # print(path.objects)
    # print(path.items())
    # paths.add(1, 2, 3, 4)

    # paths.remove('a', 'b', 'c')
    # paths.remove('p1')
    # paths.add('a')
    # print(paths)
    # print(paths._objects)
    # print(paths._relations)
    # print(paths._mapping)

    # paths = PathPyCollection(multiple=False)
    # paths.add('a', 'b', uid='ab')
    # print(paths['a', 'b'])

    # print(paths.counter)
    # col.add(p)
    # col.add(q)

    # # print(a.relations)
    # # print(a.objects)
    # # print(a.uid)
    # # print(a.attributes)

    # print('aaaaaaaaaaaaaaaaaaa')

    # print(col)
    # print('objects', col._objects)
    # print('mapping', col._mapping)
    # print('relations', col._relations)

    # print('get ------------')
    # print(col[(a, b)])

    # print(p in col)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
