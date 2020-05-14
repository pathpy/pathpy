#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_node.py -- Test environment for the Node class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2020-05-13 14:40 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest

from pathpy import Node
from pathpy.core.node import NodeCollection


def test_hash():
    """Test the hash of a node"""
    a = Node()
    b = Node('b')
    c = Node('b')

    # different objects
    assert a.__hash__() != b.__hash__()

    # different objects but same uid
    assert b.__hash__() != c.__hash__()


def test_uid():
    """Test the uid assignment."""

    u = Node('u')

    assert isinstance(u, Node)
    assert isinstance(u.uid, str)
    assert u.uid == 'u'

    v = Node(1)

    assert v.uid == '1'

    w = Node()

    assert isinstance(w, Node)
    assert isinstance(w.uid, str)
    assert w.uid == hex(id(w))


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

    v = Node()

    assert v.__repr__().replace('>', '').split(' ')[-1] == v.uid


def test_update():
    """Test update node attributes."""

    u = Node('u', color='red')

    assert u['color'] == 'red'

    u.update(color='green', shape='rectangle')

    assert u['color'] == 'green'
    assert u['shape'] == 'rectangle'


def test_copy():
    """Test to make a copy of a node."""

    u = Node('u', color='blue')
    v = u.copy()

    # same uid and attribtes
    assert v.uid == u.uid == 'u'
    assert v['color'] == 'blue'

    # different objects
    assert u != v


def test_NodeCollection():
    """Test node collection"""
    nodes = NodeCollection()

    assert len(nodes) == 0

    a = Node('a')
    nodes.add(a)

    assert len(nodes) == 1
    assert nodes['a'] == a
    assert nodes[a] == a
    assert 'a' in nodes
    assert a in nodes
    assert 'a' in nodes.uids
    assert 'a' in nodes.keys()
    assert a in nodes.values()
    assert ('a', a) in nodes.items()
    assert {'a': a} == nodes.dict

    nodes.add('b', 'c')

    print(nodes)
    assert len(nodes) == 3

    with pytest.raises(Exception):
        nodes.add('a')

    with pytest.raises(Exception):
        nodes.add(a)

    d = Node('d', color='blue')
    nodes.add(d)

    assert nodes['d']['color'] == 'blue'

    d['color'] = 'red'
    assert nodes['d']['color'] == 'red'

    nodes.add('e', ('f', 'g'), ['h', 'i'])

    assert len(nodes) == 9

    nodes.remove(('e', 'f', 'g'), 'h', ['i'])

    assert len(nodes) == 4

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
