#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_path.py -- Test environment for the Path class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2019-09-30 16:31 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest
from pathpy import Node, Edge, Path


# Test properties
# ---------------

def test_path():
    """ Test basic functionalists of the path class."""
    p = Path()

    assert isinstance(p, Path)
    assert len(p) == 0

    p = Path(name='my path')

    assert p.name == 'my path'

    p = Path(['a', 'b', 'c'])
    assert len(p) == 3

    p1 = Path(['a', 'b'])
    p2 = Path(['a', 'b'])

    assert p1 == p2

    s = set()

    s.add(p1)
    s.add(p2)

    assert len(s) == 1
    assert list(s)[0].name == 'a-b'

# Test methods
# ------------


# def test_weight():
#     p = Path()

#     assert p.weight() == 1

#     p['weight'] = 4

#     assert p.weight() == 4
#     assert p.weight(False) == 1

#     p['length'] = 5

#     assert p.weight('length') == 5


def test_add_node():
    """Test the node assignment."""
    p = Path()
    p.add_node('a', color='red')

    assert len(p) == 1
    assert p.path_nodes[0] == 'a'
    assert p.nodes['a'].id == 'a'
    assert p.nodes['a']['color'] == 'red'

    b = Node('b', color='green')
    p.add_node(b)

    assert len(p) == 2
    assert p.path_nodes[-1] == 'b'
    assert p.nodes['b'].id == 'b'
    assert p.nodes['b']['color'] == 'green'

    assert p.name == 'a-b'
    assert p.edges['a-b'].id == 'a-b'
    assert p.path_edges[0] == 'a-b'

    p.add_node(b)

    assert len(p) == 3


def test_add_edge():
    """Test the edge assignment."""
    p = Path()
    p.add_edge('ab', 'a', 'b', length=10)

    assert len(p) == 2
    assert p.path_edges[0] == p.edges['ab'].id
    assert p.path_nodes == ['a', 'b']

    bc = Edge('bc', 'b', 'c', length=5)
    p.add_edge(bc)

    assert len(p) == 3
    assert p.path_edges[1] == p.edges['bc'].id
    assert p.path_nodes == ['a', 'b', 'c']

    with pytest.raises(Exception):
        p.add_edge('de')

    with pytest.raises(Exception):
        p.add_edge('de', 'd', 'e')


def test_has_subpath():
    """Test to find a suppath."""
    p = Path()
    p.add_nodes_from(['a', 'b', 'c', 'd'])

    assert p.has_subpath(['a', 'b']) is True
    assert p.has_subpath(['a', 'c']) is False

    q = Path()
    q.add_nodes_from(['c', 'd'])

    assert p.has_subpath(q) is True

    q.add_node('e')

    assert p.has_subpath(q) is False

    p.add_nodes_from(['a', 'e', 'f'])

    assert p.has_subpath(['a', 'b', 'c']) is True
    assert p.has_subpath(['a', 'e', 'f']) is True

    assert p.has_subpath(['a-b', 'b-c'], mode='edges') is True
    assert p.has_subpath(['a-b', 'x-y'], mode='edges') is False


def test_subpath():
    """Test to get a subpath."""
    p = Path(color='red')
    p.add_nodes_from(['a', 'b', 'c', 'd'])

    q = p.subpath(['a', 'b', 'c'])

    assert q.name == 'a-b-c'
    assert q['color'] == 'red'

    with pytest.raises(Exception):
        assert p.subpath(['a', 'c'])

    r = p.subpath(['c-d'], mode='edges')

    assert len(r) == 2


def test_subpaths():
    """Test to get all subpaths."""
    p = Path(color='red')
    p.add_nodes_from(['a', 'b', 'c', 'd', 'e'])

    P = p.subpaths()
    assert len(P) == 9
    assert isinstance(P[0], str)
    assert len(p.subpaths(min_length=-5)) == 9
    assert len(p.subpaths(max_length=100)) == 9
    assert len(p.subpaths(min_length=3, max_length=3)) == 3

    with pytest.raises(Exception):
        assert p.subpaths(min_length=100, max_length=0)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
