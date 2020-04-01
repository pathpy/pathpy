#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_checks.py -- Test environment for the class checks
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2019-11-22 12:05 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest

from pathpy import Node, Edge, Path, Network
from pathpy.core.utils._check_str import _check_str


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


def test_check_path_attributes():
    """Test path with different attributes."""
    a = Node('a', color='azur', shape='circle', number=1)
    b = Node('b', color='blue', shape='rectangle')
    c = Node('c', color='cyan', shape='star')
    d = Node('d', color='dark', shape='moon')

    e1 = Edge(a, b, foo='A')
    e2 = Edge(b, c, foo='B')
    e3 = Edge(b, d, foo='C')

    p1 = Path(e1, e2, bar='1')

    net = Network()

    net.add_path(p1)

    assert list(net.paths.values())[0] == p1
    assert net.nodes['b']['color'] == 'blue'
    assert net.edges['a-b']['foo'] == 'A'
    assert net.paths[p1.uid]['bar'] == '1'

    b['color'] = 'black'
    e1['foo'] = 'D'
    p1['bar'] = '3'

    assert net.nodes['b']['color'] == 'black'
    assert net.edges['a-b']['foo'] == 'D'
    assert net.paths[p1.uid]['bar'] == '3'

    e1['foo'] = 'F'
    p2 = Path(e1, e3, bar='2')

    net.add_path(p2)

    assert net.edges['a-b']['foo'] == 'F'
    assert 'b-c' and 'b-d' in net.nodes['b'].outgoing
    assert 'a-b' in net.nodes['b'].incoming
    assert net.edges.counter()['a-b'] == 2


def test_check_path():
    """Test the path"""

    a = Node('a', color='azur')
    b = Node('b', color='blue')
    c = Node('c', color='cyan')

    e1 = Edge(a, b, foo='A')
    e2 = Edge(b, c, foo='B')
    e3 = Edge(c, a, foo='C')

    p1 = Path(e1, e2, bar='1')

    net = Network()
    net.add_path(p1)

    assert list(net.paths['a-b|b-c'].nodes) == ['a', 'b', 'c']
    assert list(net.paths['a-b|b-c'].edges) == ['a-b', 'b-c']

    net = Network()
    net.add_path(e1)

    assert list(net.paths['a-b'].nodes) == ['a', 'b']
    assert list(net.paths['a-b'].edges) == ['a-b']

    net = Network()
    net.add_path(e1, e2)

    assert list(net.paths['a-b|b-c'].nodes) == ['a', 'b', 'c']
    assert list(net.paths['a-b|b-c'].edges) == ['a-b', 'b-c']

    net = Network()
    net.add_path(a, b, c)

    assert list(net.paths['a-b|b-c'].nodes) == ['a', 'b', 'c']
    assert list(net.paths['a-b|b-c'].edges) == ['a-b', 'b-c']

    net = Network()
    net.add_path('a', 'b', 'c')

    assert list(net.paths['a-b|b-c'].nodes) == ['a', 'b', 'c']
    assert list(net.paths['a-b|b-c'].edges) == ['a-b', 'b-c']

    net = Network()
    net.add_path('a-b-c')

    assert list(net.paths['a-b|b-c'].nodes) == ['a', 'b', 'c']
    assert list(net.paths['a-b|b-c'].edges) == ['a-b', 'b-c']

    net = Network()
    net.add_path('a-b', 'b-c')

    assert list(net.paths['a-b|b-c'].nodes) == ['a', 'b', 'c']
    assert list(net.paths['a-b|b-c'].edges) == ['a-b', 'b-c']

    net = Network()
    net.add_path('a-b|b-c')

    assert list(net.paths['a-b|b-c'].nodes) == ['a', 'b', 'c']
    assert list(net.paths['a-b|b-c'].edges) == ['a-b', 'b-c']

    net = Network()
    with pytest.raises(Exception):
        net.add_path('a', 'b-c')


def test_check_str():
    """Test input strings"""

    obj = Path()
    # singel node as string
    s = _check_str(obj, 'a')
    assert s == [(['a'], 'node')]

    # node as seperate strings
    s = _check_str(obj, 'a', 'b')
    assert s == [(['a'], 'node'), (['b'], 'node')]

    # node as seperate strings
    s = _check_str(obj, 'a', 'b', 'c')
    assert s == [(['a'], 'node'), (['b'], 'node'), (['c'], 'node')]

    # singe edge as string
    s = _check_str(obj, 'a-b')
    assert s == [(['a-b'], 'edge')]

    # edge as seperate strings
    s = _check_str(obj, 'a-b', 'b-c')
    assert s == [(['a-b'], 'edge'), (['b-c'], 'edge')]

    # nodes as single string
    s = _check_str(obj, 'a,b,c')
    assert s == [(['a'], 'node'), (['b'], 'node'), (['c'], 'node')]

    # edges as single string
    s = _check_str(obj, 'a-b,b-c')
    assert s == [(['a-b'], 'edge'), (['b-c'], 'edge')]

    # nodes as simple path
    s = _check_str(obj, 'a-b-c', expected='edge')
    assert s == [(['a', 'b', 'c'], 'node')]

    # path uid as string
    s = _check_str(obj, 'a-b|b-c')
    assert s == [(['a-b|b-c'], 'path')]

    # # path uids as single string using edge uids
    s = _check_str(obj, 'a-b|b-c,a-b|b-c')
    assert s == [(['a-b|b-c'], 'path'), (['a-b|b-c'], 'path')]

    # path uids as single string using node uids
    s = _check_str(obj, 'a-b-c,b-e,f')
    assert s == [(['a-b-c'], 'path'), (['b-e'], 'edge'), (['f'], 'node')]

    # path uids as single string using edge uids
    s = _check_str(obj, 'ab|bc,ab|bc')
    assert s == [(['ab|bc'], 'path'), (['ab|bc'], 'path')]

    # path uids as single string using edge uids
    s = _check_str(obj, 'ab|bc', expected='edge')
    assert s == [(['ab', 'bc'], 'edge')]

    # path uids as single string using edge uids
    s = _check_str(obj, 'a-b|b-c=c-b|b-c')
    assert s == [(['a-b|b-c=c-b|b-c'], 'hon')]

    # path uids as single string using edge uids
    s = _check_str(obj, 'a=b,c=d')
    assert s == [(['a=b'], 'hon'), (['c=d'], 'hon')]

    # path uids as single string using edge uids
    s = _check_str(obj, 'a-b=b-c', 'u-v=v-w')
    assert s == [(['a-b=b-c'], 'hon'), (['u-v=v-w'], 'hon')]


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
