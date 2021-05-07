#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_core.py -- Test environment for the core classes
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2021-05-07 13:22 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================

import pytest

from pathpy.core.core import PathPyPath, PathPyCollection


def test_PathPyPath():
    """Test the PathPyPath"""

    p = PathPyPath('a')


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

    paths = PathPyCollection(directed=False, multiple=True)
    paths.add('a', 'b', 'c', uid='p1')
    paths.add('c', 'b', 'a', uid='p2')

    assert 'p1' in paths
    assert ('a', 'b', 'c') in paths

    #paths.add(1, 2, 3, 4)

    #paths.remove('a', 'b', 'c')
    # paths.remove('p1')
    paths.add('a')
    print(paths)
    print(paths._objects)
    print(paths._relations)
    print(paths._mapping)

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
