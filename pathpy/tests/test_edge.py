# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_edge.py -- Test environment for the Edge class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2020-04-16 10:00 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest

from pathpy import Edge, Node


@pytest.fixture(params=[True, False])
def nodes(request):
    """Generate node objects."""
    v = Node('v')
    w = Node('w')
    return v, w


def test_hash():
    """Test the hash of an edge"""
    a = Node('a')
    b = Node('b')
    c = Node('c')

    e1 = Edge(a, b)
    e2 = Edge(b, c)
    e3 = Edge(a, b)

    # different objects
    assert e1.__hash__() != e2.__hash__()

    # different objects but same uid
    assert e1.__hash__() != e3.__hash__()


def test_uid():
    """Test the uid assignment."""

    a = Node('a')
    b = Node('b')

    e = Edge(a, b, uid='e')

    assert isinstance(e, Edge)
    assert isinstance(e.uid, str)
    assert e.uid == 'e'

    a = Node('a')
    b = Node('b')

    e = Edge(a, b, 'e')

    assert isinstance(e, Edge)
    assert isinstance(e.uid, str)
    assert e.uid == 'e'

    a = Node()
    b = Node()

    e = Edge(a, b)

    assert isinstance(e, Edge)
    assert isinstance(e.uid, str)
    assert e.uid == hex(id(e))


def test_setitem(nodes):
    """Test the assignment of attributes."""

    v, w = nodes

    vw = Edge(v, w)
    vw['capacity'] = 5.5

    assert vw['capacity'] == 5.5


def test_getitem(nodes):
    """Test the extraction of attributes."""

    v, w = nodes

    vw = Edge(v, w, length=10)

    assert vw['length'] == 10
    assert vw['attribute not in dict'] is None


def test_repr(nodes):
    """Test printing the node."""

    v, w = nodes

    vw = Edge(v, w, 'vw')

    assert vw.__repr__() == 'Edge vw'

    vw = Edge(v, w)

    assert vw.__repr__().replace('>', '').split(' ')[-1] == vw.uid


def test_update(nodes):
    """Test update node attributes."""
    v, w = nodes
    vw = Edge(v, w, length=5)

    assert vw['length'] == 5

    vw.update(length=10, capacity=6)

    assert vw['length'] == 10
    assert vw['capacity'] == 6


def test_copy(nodes):
    """Test to make a copy of a node."""

    v, w = nodes
    vw = Edge(v, w, 'vw')
    ab = vw.copy()

    assert ab.uid == vw.uid == 'vw'

    # different objects
    assert ab != vw


def test_weight(nodes):
    """Test the weight assigment."""

    v, w = nodes

    vw = Edge(v, w)

    assert vw.weight() == 1.0

    vw['weight'] = 4

    assert vw.weight() == 4.0
    assert vw.weight(weight=None) == 1.0
    assert vw.weight(weight=False) == 1.0

    vw['length'] = 5
    assert vw.weight('length') == 5.0


def test_self_loop():
    """Test self loop as an edge."""
    v = Node()

    vv = Edge(v, v)
    assert len(vv.nodes) == 1


def test_errors():
    """Test some errors user can make"""
    with pytest.raises(Exception):
        e = Edge('a', 'b')

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
