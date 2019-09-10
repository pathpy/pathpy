#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_edge.py -- Test environment for the Edge class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2019-09-10 09:47 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest

from pathpy import Edge, Node


def test_id():
    """Test the id assignment."""

    vw = Edge('vw', 'v', 'w')

    assert isinstance(vw, Edge)
    assert isinstance(vw.id, str)
    assert vw.id == 'vw'
    assert isinstance(vw.v, Node) and vw.v.id == 'v'
    assert isinstance(vw.w, Node) and vw.w.id == 'w'

    a = Node('a')
    b = Node('b')
    ab = Edge('ab', a, b)

    assert isinstance(ab, Edge)
    assert isinstance(ab.id, str)
    assert ab.id == 'ab'
    assert isinstance(ab.v, Node) and ab.v.id == 'a'
    assert isinstance(ab.w, Node) and ab.w.id == 'b'


def test_setitem():
    """Test the assignment of attributes."""

    vw = Edge('vw', 'v', 'w')
    vw['capacity'] = 5.5

    assert vw['capacity'] == 5.5


def test_getitem():
    """Test the extraction of attributes."""

    vw = Edge('vw', 'v', 'w', length=10)

    assert vw['length'] == 10
    with pytest.raises(KeyError):
        vw['attribute not in dict']


def test_repr():
    """Test printing the node."""

    vw = Edge('vw', 'v', 'w')

    assert vw.__repr__() == 'Edge vw'


def test_update():
    """Test update node attributes."""

    vw = Edge('vw', 'v', 'w', length=5)

    assert vw['length'] == 5

    vw.update(length=10, capacity=6)

    assert vw['length'] == 10
    assert vw['capacity'] == 6


def test_copy():
    """Test to make a copy of a node."""

    vw = Edge('vw', 'v', 'w')
    ab = vw.copy()

    assert ab.id == vw.id == 'vw'


def test_weight():
    """Test the weight assigment."""

    vw = Edge('vw', 'v', 'w')

    assert vw.weight() == 1.0

    vw['weight'] = 4

    assert vw.weight() == 4.0
    assert vw.weight(weight=None) == 1.0
    assert vw.weight(weight=False) == 1.0

    vw['length'] = 5
    assert vw.weight('length') == 5.0

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
