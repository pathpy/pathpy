#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_path.py -- Test environment for the Path class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2019-10-11 09:17 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest
from pathpy import Node, Edge, Path


@pytest.fixture()
def edges(request):
    """Generate node and edge objects."""
    a = Node('a')
    b = Node('b')
    c = Node('c')
    ab = Edge(a, b)
    bc = Edge(b, c)
    return ab, bc


# Test properties
# ---------------

def test_basic(edges):
    """ Test basic functionalists of the path class."""
    p = Path()

    assert isinstance(p, Path)
    assert len(p) == 0

    p = Path(name='my path')

    assert p.name == 'my path'

    ab, bc = edges

    p = Path(ab, bc)
    assert len(p) == 2

    p1 = Path(ab)
    p2 = Path(ab)

    assert p1 == p2

    s = set()

    s.add(p1)
    s.add(p2)

    assert len(s) == 1
    assert list(s)[0].name == 'a-b'


def test_uid(edges):
    """Test the uid assignment."""

    ab, bc = edges
    p = Path(ab, bc)

    assert p.uid == 'a-b|b-c'

    p = Path('a', 'b', 'c')

    assert p.uid == 'a-b|b-c'

    p = Path('a', 'a', 'a')

    assert p.uid == 'a-a|a-a'


def test_attributes(edges):
    """Test the attributes assignment."""

    p = Path('v', 'w', color='red')

    assert isinstance(p.attributes, dict)

    assert p.attributes['color'] == 'red'


def test_setitem():
    """Test the assignment of attributes."""

    p = Path('a', 'b', 'c')
    p['capacity'] = 5.5

    assert p['capacity'] == 5.5


def test_getitem():
    """Test the extraction of attributes."""

    p = Path('a', 'b', 'c', length=10)

    assert p['length'] == 10
    with pytest.raises(KeyError):
        p['attribute not in dict']


def test_name():
    """Test the name assigment of the path."""

    p = Path('a', 'b', 'c')

    assert p.name == 'a-b|b-c'

    p = Path('a', 'b', 'c', 'd', 'e', 'f', 'g')

    assert p.name == 'a-b|b-c|c-d|d-e|...|f-g'


def test_nodes():
    """Test the node dict."""

    p = Path('a', 'b', 'c')

    assert isinstance(p.nodes['a'], Node)
    assert len(p.nodes) == 3


def test_edges():
    """Test the edge dict."""

    p = Path('a', 'b', 'c')

    assert isinstance(p.edges['a-b'], Edge)
    assert len(p.edges) == 2


def test_path():
    """Test the path list."""

    p = Path('a', 'b', 'c', 'a', 'b',)

    assert p.path == ['a-b', 'b-c', 'c-a', 'a-b']


def test_node_counter():
    """Test the node Counter."""

    p = Path('a', 'b', 'c', 'a', 'b',)

    assert p.node_counter['a'] == 2
    assert p.node_counter['b'] == 2
    assert p.node_counter['c'] == 1


def test_edge_counter():
    """Test the edge Counter."""

    p = Path('a', 'b', 'c', 'a', 'b',)

    assert p.edge_counter['a-b'] == 2
    assert p.edge_counter['b-c'] == 1
    assert p.edge_counter['c-a'] == 1

# Test methods
# ------------


def test_update():
    """Test update of the attributes"""
    p = Path(street='High Street')

    assert p.attributes['street'] == 'High Street'

    print(p.attributes)

    p.update(street='Market Street', toll=False)

    assert p.attributes['street'] == 'Market Street'
    assert p.attributes['toll'] is False

    print(p.attributes)


def test_number_of_nodes():
    """Test the number of nodes."""

    p = Path('a', 'b', 'c', 'a', 'b',)

    assert p.number_of_nodes() == 3
    assert p.number_of_nodes(unique=False) == 5


def test_number_of_edges():
    """Test the number of edges."""

    p = Path('a', 'b', 'c', 'a', 'b',)

    assert p.number_of_edges() == 3
    assert p.number_of_edges(unique=False) == 4


def test_weight():
    p = Path()

    assert p.weight() == 1

    p['weight'] = 4

    assert p.weight() == 4
    assert p.weight(False) == 1

    p['length'] = 5

    assert p.weight('length') == 5


def test_add_node():
    """Test the node assignment."""
    p = Path()
    p.add_node('a', color='red')

    assert len(p) == 0
    assert p.number_of_nodes() == 1
    assert p.nodes['a'].uid == 'a'
    assert p.nodes['a']['color'] == 'red'

    b = Node('b', color='green')
    p.add_node(b)

    assert len(p) == 1
    assert p.number_of_nodes() == 2
    assert p.nodes['b'].uid == 'b'
    assert p.nodes['b']['color'] == 'green'

    assert p.name == 'a-b'
    assert p.edges['a-b'].uid == 'a-b'
    assert p.path[0] == 'a-b'

    p.add_node(b)

    assert len(p) == 2
    assert p.path[-1] == 'b-b'


def test_add_edge():
    """Test the edge assignment."""

    p = Path()
    ab = Edge('a', 'b', length=10)
    p.add_edge(ab)

    assert len(p) == 1
    assert p.edges['a-b'].uid == 'a-b'
    assert p.nodes['a'].uid == 'a'
    assert p.nodes['b'].uid == 'b'
    assert p.path[0] == 'a-b'

    bc = Edge('b', 'c', length=5)
    p.add_edge(bc)

    assert len(p) == 2
    assert p.path[-1] == p.edges['b-c'].uid
    assert list(p.nodes.keys()) == ['a', 'b', 'c']


def test_has_subpath():
    """Test to find a suppath."""
    pass


def test_subpath():
    """Test to get a subpath."""
    pass


def test_subpaths():
    """Test to get all subpaths."""
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
