#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_node.py -- Test environment for the Node class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-10-31 10:26 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest

from pathpy import Node


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
    assert u['attribute not in dict'] == None


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


def test_copy():
    """Test to make a copy of a node."""

    u = Node('u')
    v = u.copy()

    assert v.uid == u.uid == 'u'


def test_outgoing():
    """Test the outgoing edges."""
    pass


def test_incoming():
    """Test the incominb edges."""
    pass


def test_adjacent_edges():
    """Test the adjacent edges."""
    pass


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
