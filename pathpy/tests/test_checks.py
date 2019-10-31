#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_checks.py -- Test environment for the class checks
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-10-31 14:32 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest

from pathpy import Node, Edge, Path
import pathpy as pp


def test_check_node_correct():
    """Check a correct node assigment."""
    a = Node('a')
    b = Node('b')

    # correct assignment
    e = Edge(a, b)

    assert isinstance(e, Edge)
    assert len(e.nodes) == 2
    assert isinstance(e.v, Node) and isinstance(e.w, Node)
    assert e.v.uid == 'a'
    assert e.w.uid == 'b'


def test_check_node_double_1():
    """Check node assigment with double entries.

    Two different node objects are assigned with same uid and attributes.
    """
    a = Node('a', color='green')
    b = Node('a', color='green')

    # correct assignment
    e = Edge(a, b)

    assert isinstance(e, Edge)
    assert len(e.nodes) == 1
    assert isinstance(e.v, Node) and isinstance(e.w, Node)
    assert e.v.uid == e.w.uid == 'a'
    assert e.v['color'] == e.v['color'] == 'green'
    assert id(e.v) == id(e.w) == id(a)
    assert id(e.v) == id(e.w) != id(b)


def test_check_node_double_2():
    """Check node assigment with double entries.

    Two different node objects are assigned with same uid but different
    attributes.

    """
    a = Node('a', color='green')
    b = Node('a', color='red')

    e = Edge(a, b)

    assert isinstance(e, Edge)
    assert len(e.nodes) == 1
    assert isinstance(e.v, Node) and isinstance(e.w, Node)
    assert e.v.uid == e.w.uid == 'a'
    assert e.v['color'] == e.v['color'] == 'red'
    assert id(e.v) == id(e.w) == id(a)
    assert id(e.v) == id(e.w) != id(b)

    a['color'] = 'blue'

    assert e.v['color'] == e.v['color'] == 'blue'

    b['color'] = 'yellow'

    assert e.v['color'] == e.v['color'] == 'blue'


def test_check_node_from_str():
    """Check node assigment from strings."""

    e = Edge('a', 'b')

    assert len(e.nodes) == 2
    assert isinstance(e.v, Node) and isinstance(e.w, Node)
    assert e.v.uid == 'a'
    assert e.w.uid == 'b'

    e = Edge('a', 'a')

    assert len(e.nodes) == 1
    assert isinstance(e.v, Node) and isinstance(e.w, Node)
    assert e.v.uid == e.w.uid == 'a'
    assert id(e.v) == id(e.w)

    a = Node('a', color='green')

    e = Edge('a', a)

    assert isinstance(e, Edge)
    assert len(e.nodes) == 1
    assert isinstance(e.v, Node) and isinstance(e.w, Node)
    assert e.v.uid == e.w.uid == 'a'
    assert e.v['color'] == e.v['color'] == 'green'
    assert id(e.v) == id(e.w) != id(a)

    a['color'] = 'blue'

    assert e.v['color'] == e.v['color'] != 'blue'

    e.v['color'] = 'yellow'

    assert e.v['color'] == e.v['color'] == 'yellow'

    a = Node('a', color='green')

    e = Edge(a, 'a')

    assert isinstance(e, Edge)
    assert len(e.nodes) == 1
    assert isinstance(e.v, Node) and isinstance(e.w, Node)
    assert e.v.uid == e.w.uid == 'a'
    assert e.v['color'] == e.v['color'] == 'green'
    assert id(e.v) == id(e.w) == id(a)

    a['color'] = 'blue'

    assert e.v['color'] == e.v['color'] == 'blue'

    e.v['color'] = 'yellow'

    assert a['color'] == 'yellow'

    # print(a.attributes.data_frame(history=True))


def test_check_edge_in_path_with_edge_objects():
    """Test the the check_edge function for paths."""

    # create node objects
    a = Node('a', color='azur', shape='circle')
    b = Node('b', color='blue', shape='rectangle')
    c = Node('c', color='cyan', shape='triangle')

    # create empty path object
    p = Path()

    # test edge objects
    ab = Edge(a, b, street='major')
    bc = Edge(b, c, street='minor')

    p.add_edge(ab, foo='edge object 1')

    assert p.number_of_nodes() == 2
    assert p.as_nodes[0] == 'a'
    assert p.as_nodes[-1] == 'b'
    assert p.number_of_edges() == 1
    assert p.nodes['b']['color'] == 'blue'

    p.nodes['b']['color'] = 'black'

    p.add_edge(bc, foo='edge object 2')

    assert p.number_of_nodes() == 3
    assert p.as_nodes[0] == 'a'
    assert p.as_nodes[-1] == 'c'
    assert p.number_of_edges() == 2
    assert p.nodes['b']['color'] == 'black'

    ca = Edge(c, a, street='way')

    p.add_edge(ca)

    assert 'c-a' in p.nodes['a'].incoming
    assert 'c-a' in p.nodes['a'].incoming
    assert 'a-b' in p.nodes['a'].outgoing
    assert p.edges['c-a']['street'] == 'way'


def test_check_edge_in_path_with_node_objects():
    """Test the the check_edge function for paths."""

    # create node objects
    a = Node('a', color='azur', shape='circle')
    b = Node('b', color='blue', shape='rectangle')
    c = Node('c', color='cyan', shape='triangle')

    # create empty path object
    p = Path()

    # test node objects
    p.add_edge(a, b, foo='edge object 1')

    assert p.number_of_nodes() == 2
    assert p.as_nodes[0] == 'a'
    assert p.as_nodes[-1] == 'b'
    assert p.number_of_edges() == 1
    assert p.nodes['b']['color'] == 'blue'

    p.nodes['b']['color'] = 'black'

    p.add_edge(b, c, foo='edge object 2')

    assert p.number_of_nodes() == 3
    assert p.as_nodes[0] == 'a'
    assert p.as_nodes[-1] == 'c'
    assert p.number_of_edges() == 2
    assert p.nodes['b']['color'] == 'black'

    p.add_edge(c, a, street='way')

    assert 'c-a' in p.nodes['a'].incoming
    assert 'a-b' in p.nodes['a'].outgoing
    assert p.edges['c-a']['street'] == 'way'

    # TODO:
    # p.add_edge(a, b, 'ab', foo='node objects with edge uid')


def test_check_edge_in_path_with_node_str():
    """Test the the check_edge function for paths."""

    # create empty path object
    p = Path()

    # test node defined as str
    p.add_edge('a', 'b', foo='edge object 1')

    assert p.number_of_nodes() == 2
    assert p.as_nodes[0] == 'a'
    assert p.as_nodes[-1] == 'b'
    assert p.number_of_edges() == 1

    p.nodes['b']['color'] = 'black'

    p.add_edge('b', 'c', foo='edge object 2')

    assert p.number_of_nodes() == 3
    assert p.as_nodes[0] == 'a'
    assert p.as_nodes[-1] == 'c'
    assert p.number_of_edges() == 2
    assert p.nodes['b']['color'] == 'black'

    p.add_edge('c', 'a', street='way')

    assert 'c-a' in p.nodes['a'].incoming
    assert 'a-b' in p.nodes['a'].outgoing
    assert p.edges['c-a']['street'] == 'way'

    # TODO:
    # p.add_edge('a', 'b', 'ab', foo='node strings and edge uid')


def test_check_edge_in_path_with_edge_str():
    """Test the the check_edge function for paths."""

    # create empty path object
    p = Path()

    # test node defined as str
    p.add_edge('a-b', foo='edge object 1')

    assert p.number_of_nodes() == 2
    assert p.as_nodes[0] == 'a'
    assert p.as_nodes[-1] == 'b'
    assert p.number_of_edges() == 1

    p.nodes['b']['color'] = 'black'

    p.add_edge('b-c', foo='edge object 2')

    assert p.number_of_nodes() == 3
    assert p.as_nodes[0] == 'a'
    assert p.as_nodes[-1] == 'c'
    assert p.number_of_edges() == 2
    assert p.nodes['b']['color'] == 'black'

    p.add_edge('c-a', street='way')

    assert 'c-a' in p.nodes['a'].incoming
    assert 'a-b' in p.nodes['a'].outgoing
    assert p.edges['c-a']['street'] == 'way'

    # TODO:
    # p.add_edge('ab', foo='edge string')


def test_check_edge_in_path():
    """Test the check"""

    a = Node('a', color='azur', shape='circle', number=1)
    b = Node('b', color='blue', shape='rectangle')
    c = Node('c', color='cyan', shape='star')
    d = Node('d', color='dark', shape='moon')

    e1 = Edge(a, b, foo='A')
    e2 = Edge(b, c, foo='B')
    e3 = Edge(c, a, foo='C')

    p = Path()

    p.add_edge(e1)
    p.nodes['a']['number'] = 2
    p.add_edge(e2)
    p.nodes['a']['number'] = 3
    p.add_edge(e3)
    p.nodes['a']['number'] = 4

    e4 = Edge(a, b, foo='D')

    p.add_edge(e4)

    d = p.edges['a-b'].attributes.data

    assert d[0]['foo'] == 'A'
    assert d[1]['foo'] == 'D'

    assert 'c-a' in p.nodes['a'].incoming
    assert 'a-b' in p.nodes['a'].outgoing

    assert p.nodes['a'].attributes.data[3]['number'] == 4

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
