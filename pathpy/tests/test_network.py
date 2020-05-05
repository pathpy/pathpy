#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_network.py -- Test environment for the Network class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2020-05-05 15:10 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest
from pathpy import Node, Edge, Network

# Test network
# ------------


# @pytest.fixture(params=[True, False])
# def net(request):
#     net = Network(directed=request.param)
#     net.add_edge('a', 'b')
#     net.add_edge('b', 'c')
#     net.add_edge('c', 'd')
#     net.add_edge('a', 'b')
#     return net

# # test magic methods
# # ------------------


# def test_setitem():
#     """Test the assignment of attributes."""

#     net = Network()
#     net['city'] = 'Zurich'

#     assert net['city'] == 'Zurich'


# def test_getitem():
#     """Test the extraction of attributes."""

#     net = Network(city='London')

#     assert net['city'] == 'London'
#     assert net['attribute not in dict'] == None


# def test_str():
#     """Test string representations of the network."""
#     net = Network()
#     assert isinstance(net.summary(), str)


# # Test properties
# # ---------------


# def test_uid():
#     """Test the uid assignment."""
#     net = Network(uid='test')

#     assert isinstance(net, Network)
#     assert isinstance(net.uid, str)
#     assert net.uid == 'test'

#     net = Network()

#     assert isinstance(net, Network)
#     assert isinstance(net.uid, str)


# def test_name():
#     """Test the name assignment."""

#     net = Network()

#     assert isinstance(net, Network)

#     assert net.name == ''

#     net.name = 'my network'

#     assert net.name == 'my network'

#     net = Network(name='an other network')

#     assert net.name == 'an other network'


# def test_directed():
#     """Test if a network is directed."""

#     net = Network()

#     assert net.directed is True

#     net = Network(directed=False)

#     assert net.directed is False


# def test_shape():
#     """Test the shape of the network."""
#     pass


# # # Test methods
# # # ------------


# def test_update():
#     """Test update network attributes."""

#     net = Network(city='London')

#     assert net['city'] == 'London'

#     net.update(city='Vienna', year='1850')

#     assert net['city'] == 'Vienna'
#     assert net['year'] == '1850'


# def test_add_path():
#     """Test the path assignment."""

#     p1 = Path('a', 'b', 'c', 'a', 'b')
#     p2 = Path('d', 'b', 'e')

#     net = Network()

#     net.add_path(p1)

#     assert net.number_of_nodes() == 3
#     assert net.number_of_nodes() == 3
#     assert net.number_of_paths() == 1

#     net.add_path(p2)

#     assert net.number_of_paths() == 2


# def test_number_of_nodes():
#     """Test the number of nodes."""

#     net = Network(Path('a', 'b', 'c', 'a', 'b'))

#     assert net.number_of_nodes() == 3

#     assert net.number_of_nodes(unique=False) == 5


# def test_number_of_edges():
#     """Test the number of edges."""
#     net = Network(Path('a', 'b', 'c', 'a', 'b'))

#     assert net.number_of_edges() == 3

#     assert net.number_of_edges(unique=False) == 4


# def test_number_of_paths():
#     """Test the number of edges."""
#     p1 = Path('a', 'b', 'c')
#     p2 = Path('d', 'b', 'e')
#     net = Network(p1, p2, p1)

#     assert net.number_of_paths() == 2

#     assert net.number_of_paths(unique=False) == 3


def test_add_node():
    """Test the node assignment."""

    # add string and create new node in the network
    net = Network()
    net.add_node('v', color='red')

    assert len(net.nodes) == 1
    assert 'v' in net.nodes.uids
    assert net.nodes['v']['color'] == 'red'
    assert net.nodes.index['v'] == 0
    assert net.number_of_nodes() == 1
    assert isinstance(net.nodes['v'], Node)
    assert net.nodes['v'].uid == 'v'

    w = Node('w', color='green')
    net.add_node(w)

    assert net.number_of_nodes() == 2
    assert isinstance(net.nodes['w'], Node)
    assert net.nodes['w'].uid == 'w'
    assert net.nodes['w']['color'] == 'green'

    v = Node('v', color='blue')
    with pytest.raises(Exception):
        net.add_node(v)


def test_add_nodes():
    """Test assigning notes form a list."""
    net = Network()
    u = Node('u', color='blue')
    net.add_nodes(u, 'v', 'w', color='green')

    assert net.number_of_nodes() == 3
    assert net.nodes['u']['color'] == 'blue'
    assert net.nodes['v']['color'] == 'green'
    assert net.nodes['w']['color'] == 'green'


def test_add_edge():
    """Test the edge assignment."""

    a = Node('a')
    b = Node('b')
    c = Node('c')

    # add edges with no uids
    e = Edge(a, b)
    f = Edge(b, c)
    g = Edge(a, b)

    net = Network()
    net.add_edge(e)
    net.add_edge(f)
    net.add_edge(g)

    assert len(net.edges) == 3
    assert len(net.nodes) == 3

    with pytest.raises(Exception):
        net.add_node(a)

    with pytest.raises(Exception):
        net.add_edge(e)

    # add edges with uids
    e = Edge(a, b, uid='a-b')
    f = Edge(b, c, uid='b-c')
    g = Edge(a, b, uid='a-b')
    h = Edge(a, b, uid='ab')

    net = Network()
    net.add_edge(e)
    net.add_edge(f)
    net.add_edge(h)

    assert len(net.edges) == 3
    assert len(net.nodes) == 3

    with pytest.raises(Exception):
        net.add_edge(g)

    with pytest.raises(Exception):
        net.add_edge(e)

    # add edges and nodes
    net = Network()
    net.add_edge(e)

    # add new node with same uid
    with pytest.raises(Exception):
        net.add_node('a')

    # add same node
    with pytest.raises(Exception):
        net.add_node(a)

    # add node and edge with the node
    a1 = Node('a')
    a2 = Node('a')
    b = Node('b')
    e1 = Edge(a2, b)
    net = Network()
    net.add_node(a1)

    with pytest.raises(Exception):
        net.add_edge(e1)

    e2 = Edge(net.nodes['a'], b)
    net.add_edge(e2)

    # net add edge via string and nodes
    net = Network()
    net.add_node('a')
    net.add_node('b')
    net.add_edge('a', 'b')

    assert len(net.nodes) == 2
    assert len(net.edges) == 1

    net.add_edge('a', 'b')

    assert len(net.nodes) == 2
    assert len(net.edges) == 2

    c = Node('c')

    net.add_edge('b', c)

    assert len(net.nodes) == 3
    assert len(net.edges) == 3

    a = Node('a')

    with pytest.raises(Exception):
        net.add_edge(a, 'b')

    with pytest.raises(Exception):
        net.add_edge(None)

    net = Network()
    net.add_edge('a', 'b', uid='a-b', length=10)

    assert net.number_of_nodes() == 2
    assert net.number_of_edges() == 1
    assert isinstance(net.edges['a-b'], Edge)
    assert net.edges['a-b'].uid == 'a-b'
    assert net.edges['a-b']['length'] == 10
    assert net.nodes['a'].uid == 'a'
    assert net.nodes['b'].uid == 'b'

    b = net.nodes['b']
    c = Node('c')
    net.add_edge(b, c, uid='c-d', length=5)

    assert net.number_of_edges() == 2

    net.add_edge('c', 'd', uid='c-2-d')

    assert net.number_of_edges() == 3
    assert net.edges['c-2-d'].v.uid == 'c'

    net.add_edge('a', 'd', uid='a-d')
    assert net.edges['a-d'].uid == 'a-d'

    ab = Edge(Node('a'), Node('b'), uid='a-b')
    net = Network()
    net.add_edge(ab, color='blue')

    # TODO: Should attribute be updated?
    with pytest.raises(Exception):
        assert net.edges['a-b']['color'] == 'blue'


def test_call_edges():
    """Test to call edges"""

    net = Network()
    net.add_edge('a', 'b', uid='a-b')

    assert isinstance(net.edges['a-b'], Edge)

    assert net.edges['a-b'].uid == 'a-b'

    # TODO make this nicer
    assert list(net.edges['a', 'b'])[0].uid == 'a-b'

    net = Network()
    net.add_edge('a', 'b')
    net.add_edge('a', 'b')
    net.add_edge('a', 'b', uid='a-b')

    assert net.number_of_edges() == 3
    assert len(net.edges['a', 'b']) == 3

    net = Network()
    net.add_edge('a', 'b')
    net.add_edge('b', 'a')

    assert net.number_of_edges() == 2
    assert len(net.edges['a', 'b']) == 1
    assert len(net.edges['b', 'a']) == 1

    net = Network(directed=False)
    net.add_edge('a', 'b')
    net.add_edge('b', 'a')

    assert net.number_of_edges() == 2
    assert len(net.edges['a', 'b']) == 2
    assert len(net.edges['b', 'a']) == 2


def test_add_edges():
    """Test assigning edges form a list."""
    net = Network()
    ab = Edge(Node('a'), Node('b'))

    net.add_edges(ab, ('b', 'c'))

    assert net.number_of_edges() == 2


def test_properties():
    """Test network properties."""
    net = Network(directed=False)
    net.add_edge('a', 'b', uid='a-b')

    net.edges['a-b']['color'] = 'red'

    # print(net._properties._neighbors)
    # s = {'a', 'b'}
    # s.discard('c')
    # print(net.nodes.successors['a'])
    # print(net.indegrees())
# def test_add_args():
#     """Test various input args for path generation."""

#     a = Node('a', color='blue')
#     b = Node('b', color='red')
#     c = Node('c', color='cyan')

#     ab = Edge(a, b, capacity=5)
#     bc = Edge(b, c, capacity=10)

#     # edge object
#     p1 = Path(ab)
#     p2 = Path(bc)
#     p3 = Path(ab, bc)

#     # node objects
#     net = Network(a, b, c)
#     assert list(net.nodes) == ['a', 'b', 'c']

#     # edge object
#     net = Network(ab, bc)
#     assert list(net.nodes) == ['a', 'b', 'c']
#     assert list(net.edges) == ['a-b', 'b-c']

#     # path object
#     net = Network(p1, p2, p3)
#     assert list(net.nodes) == ['a', 'b', 'c']
#     assert list(net.edges) == ['a-b', 'b-c']
#     assert list(net.paths) == ['a-b', 'b-c', 'a-b|b-c']

#     # mixed objectes
#     net = Network(a, bc, p3)
#     assert list(net.nodes) == ['a', 'b', 'c']
#     assert list(net.edges) == ['b-c', 'a-b']
#     assert list(net.paths) == ['a-b|b-c']

#     # singel node as string
#     net = Network('a')
#     assert list(net.nodes) == ['a']
#     assert list(net.edges) == []
#     assert list(net.paths) == []

#     # node as seperate strings
#     net = Network('a', 'b', 'c')
#     assert list(net.nodes) == ['a', 'b', 'c']
#     assert list(net.edges) == []
#     assert list(net.paths) == []

#     # nodes as single string
#     net = Network('a,b,c')
#     assert list(net.nodes) == ['a', 'b', 'c']
#     assert list(net.edges) == []
#     assert list(net.paths) == []

#     # singe edge as string
#     net = Network('a-b')
#     assert list(net.nodes) == ['a', 'b']
#     assert list(net.edges) == ['a-b']
#     assert list(net.paths) == []

#     # edge as seperate strings
#     net = Network('a-b', 'b-c')
#     assert list(net.nodes) == ['a', 'b', 'c']
#     assert list(net.edges) == ['a-b', 'b-c']
#     assert list(net.paths) == []

#     # edges as single string
#     net = Network('a-b,b-c')
#     assert list(net.nodes) == ['a', 'b', 'c']
#     assert list(net.edges) == ['a-b', 'b-c']
#     assert list(net.paths) == []

#     # nodes as simple path
#     net = Network('a-b-c')
#     assert list(net.nodes) == ['a', 'b', 'c']
#     assert list(net.edges) == ['a-b', 'b-c']
#     assert list(net.paths) == ['a-b|b-c']

#     # simple path uid
#     net = Network('a-b|b-c')
#     assert list(net.nodes) == ['a', 'b', 'c']
#     assert list(net.edges) == ['a-b', 'b-c']
#     assert list(net.paths) == ['a-b|b-c']

#     # mixed strings
#     net = Network('a', 'b-c', 'a-b-c')
#     assert list(net.nodes) == ['a', 'b', 'c']
#     assert list(net.edges) == ['b-c', 'a-b']
#     assert list(net.paths) == ['a-b|b-c']


# def test_check_class():
#     """Test the class assignment"""
#     # cb = Edge('c', 'b', directed=True, start=10)
#     # a = Node('a', start=5)
#     # net = Network(a, cb)
#     # #net = Network('a')
#     # net._check_class()

#     # net.summary()
#     pass


# def test_remove_path():
#     """Test to remove a path from the network."""
#     net = Network()
#     net.add_paths_from(['a-b-c-d', 'b-c-d'], frequency=10)

#     net.remove_path('b-c-d', frequency=3)
#     assert net.paths.counter()['b-c|c-d'] == 7
#     assert net.nodes.counter()['b'] == 17
#     assert net.edges.counter()['b-c'] == 17

#     net.remove_path('b-c|c-d')
#     assert net.number_of_paths() == 1
#     assert net.nodes.counter()['b'] == 10
#     assert net.edges.counter()['b-c'] == 10

#     net.remove_path('a-b-c-d')
#     assert net.number_of_paths() == 0
#     assert net.nodes.counter()['b'] == 0
#     assert net.edges.counter()['b-c'] == 0

#     net = Network()
#     net.add_paths_from(['a-b-c-d', 'b-c-d'], frequency=10)

#     net.remove_path('b-c-d', frequency=30)
#     assert net.number_of_paths() == 1
#     assert net.nodes.counter()['b'] == 10
#     assert net.edges.counter()['b-c'] == 10


def test_remove_edge():
    """Test to remove an edge from the network."""

    net = Network()
    a = Node('a')
    b = Node('b')
    c = Node('c')
    e = Edge(a, b, uid='e')
    f = Edge(b, a, uid='f')
    g = Edge(b, c, uid='g')
    net.add_edges(e)
    net.add_edges(f)

    net.remove_edge(g)

    assert net.number_of_edges() == 2
    assert isinstance(net.edges['e'], Edge)
    assert len(net.edges['a', 'b']) == 1
    assert net.successors['a'] == {b}
    assert net.outgoing['a'] == {e}
    assert net.incident_edges['a'] == {e, f}
    net.remove_edge(e)

    assert net.number_of_edges() == 1
    assert net.successors['a'] == set()
    assert net.outgoing['a'] == set()
    assert net.incident_edges['a'] == {f}

    net.remove_edge('f')

    assert net.number_of_edges() == 0
    assert net.incident_edges['a'] == set()

    a = Node('a')
    b = Node('b')
    e = Edge(a, b, uid='e')
    f = Edge(a, b, uid='f')
    g = Edge(a, b, uid='g')

    net = Network()
    net.add_edges(e, f, g)

    assert net.number_of_edges() == 3
    assert net.edges['a', 'b'] == {e, f, g}

    net.remove_edge('a', 'b', uid='g')
    assert net.number_of_edges() == 2
    assert net.edges['a', 'b'] == {e, f}

    net.remove_edge('a', 'b')
    assert net.number_of_edges() == 0
    assert net.edges['a', 'b'] == set()

    # net = Network()
    # net.add_edges_from(['a-b', 'b-c', 'c-d'])
    # net.add_path('a-b-c-d')

    # net.remove_edge('b-c')
    # assert net.number_of_paths() == 0


def test_remove_node():
    """Test to remove a node from the network."""

#     net = Network()
#     net.add_edges_from(['a-b', 'b-c', 'c-d'])
#     net.add_path('a-b-c-d')

#     net.remove_node('b')
#     assert net.shape == (3, 1, 0)
#     assert net.nodes.counter()['a'] == 0
#     assert net.nodes.counter()['c'] == 1
#     assert net.nodes.counter()['d'] == 1
#     assert net.nodes.adjacent_edges['a'] == {}
#     assert list(net.nodes.adjacent_edges['c']) == ['c-d']

    net = Network(directed=True)
    net.add_edge('a', 'b')
    net.add_edge('a', 'c')
    net.add_edge('b', 'd')
    net.add_edge('b', 'e')
    net.add_edge('d', 'b')
    net.add_edge('d', 'e')
    net.add_edge('e', 'd')

    assert net.shape == (5, 7, 0)

    net.remove_node('b')
    assert net.shape == (4, 3, 0)


# def test_add_undirected_edge():
#     """Test to add undirected path to the network."""
#     e1 = Edge('a', 'b', directed=False)
#     e2 = Edge('b', 'c', directed=True)

#     net = Network()
#     net.add_edge(e1)
#     assert net.directed is False

#     net = Network()
#     net.add_edge(e2)
#     assert net.directed is True

#     with pytest.raises(Exception):
#         net = Network()
#         net.add_edge(e2)
#         net.add_edge(e1)

#     net = Network()
#     net.add_edge('a', 'b')
#     assert net.directed is True

#     net = Network()
#     net.add_edge('a', 'b', directed=False)
#     assert net.directed is False

#     with pytest.raises(Exception):
#         net = Network()
#         net.add_edge('a', 'b', directed=False)
#         net.add_edge('b', 'c', directed=True)

#     net = Network(directed=False)
#     net.add_edge('a', 'b')
#     net.add_edge('b', 'c')
#     assert net.directed is False

#     net = Network(directed=False)
#     e = Edge('a', 'b')
#     net.add_edge(e)
#     assert net.directed is False

#     net = Network()
#     e = Edge('a', 'b', directed=False)
#     net.add_edge(e)
#     assert net.directed is False


# def test_add_undirected_path():
#     """Test to add undirected path to the network."""

#     p1 = Path('a-b-c', directed=False)
#     p2 = Path('c-d-e', directed=True)

#     net = Network()
#     net.add_path(p1)
#     assert net.directed is False

#     net = Network()
#     net.add_path(p2)
#     assert net.directed is True

#     with pytest.raises(Exception):
#         net = Network()
#         net.add_path(p2)
#         net.add_path(p1)

#     net = Network()
#     net.add_path('a-b-c')
#     assert net.directed is True

#     net = Network()
#     net.add_path('a-b-c', directed=False)
#     assert net.directed is False

#     with pytest.raises(Exception):
#         net = Network()
#         net.add_path('a-b-c', directed=False)
#         net.add_path('c-d-e', directed=True)

#     net = Network(directed=False)
#     net.add_path('a-b-c')
#     net.add_path('b-c')
#     assert net.directed is False

def test_get_edge():
    """Test to get edges."""
    net = Network(directed=False)
    net.add_edge('a', 'b')
    assert (('a', 'b') in net.edges.nodes) is True
    assert (('b', 'a') in net.edges.nodes) is True
    assert (('a', 'c') in net.edges.nodes) is False

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
