#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_node.py -- Test environment for the Node class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2020-03-17 15:34 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest

from pathpy import Node, Edge


def test_uid():
    """Test the uid assignment."""

    u = Node('u')

    assert isinstance(u, Node)
    assert isinstance(u.uid, str)
    assert u.uid == 'u'

    v = Node(1)
    assert v.uid == '1'


def test_setitem():
    """Test the assignment of attributes."""

    u = Node('u')
    u['color'] = 'blue'

    assert u['color'] == 'blue'


def test_getitem():
    """Test the extraction of attributes."""

    u = Node('u', color='blue')

    assert u['color'] == 'blue'
    assert u['attribute not in dict'] is None


def test_repr():
    """Test printing the node."""

    u = Node('u')

    assert u.__repr__() == 'Node u'


def test_update():
    """Test update node attributes."""

    u = Node('u', color='red')

    assert u['color'] == 'red'

    u.update(color='green', shape='rectangle')

    assert u['color'] == 'green'
    assert u['shape'] == 'rectangle'

    v = Node('v', shape='circle', size=30)
    u.update(v)

    assert u['size'] == 30
    assert u['shape'] == 'circle'
    assert u.attributes.to_dict() == {'color': 'green',
                                      'shape': 'circle', 'size': 30}


def test_copy():
    """Test to make a copy of a node."""

    u = Node('u')
    v = u.copy()

    assert v.uid == u.uid == 'u'


def test_outgoing():
    """Test the outgoing edges."""
    u = Node('u')
    v = Node('v')
    w = Node('w')

    uv = Edge(u, v)
    assert u.outgoing == {'u-v'}

    uw = Edge(u, w)
    assert u.outgoing == {'u-v', 'u-w'}


def test_incoming():
    """Test the incominb edges."""

    u = Node('u')
    v = Node('v')
    w = Node('w')

    uv = Edge(u, v)
    assert u.incoming == set()

    wu = Edge(w, u)
    assert u.incoming == {'w-u'}


def test_adjacent_edges():
    """Test the adjacent edges."""

    u = Node('u')
    v = Node('v')
    w = Node('w')

    uv = Edge(u, v)
    vw = Edge(v, w)

    assert u.adjacent_edges == {'u-v'}
    assert v.adjacent_edges == {'v-w', 'u-v'}
    assert w.adjacent_edges == {'v-w'}


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
