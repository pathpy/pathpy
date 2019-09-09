#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_node.py -- Test environment for the Node class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2019-09-09 11:42 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest

from pathpy import Node


def test_id():
    """Test the id assigment."""

    u = Node('u')

    assert isinstance(u, Node)
    assert isinstance(u.id, str)
    assert u.id == 'u'

    v = Node(1)
    assert v.id == '1'


def test_setitem():
    """Test the assigment of attributes."""

    u = Node('u')
    u['color'] = 'blue'

    assert u['color'] == 'blue'


def test_getitem():
    """Test the extraction of attributes."""

    u = Node('u', color='blue')

    assert u['color'] == 'blue'
    with pytest.raises(KeyError):
        a = u['attribute not in dict']


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

    assert v.id == u.id == 'u'


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
