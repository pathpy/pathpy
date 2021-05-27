#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_network.py -- Test environment for the Network class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2021-05-27 12:26 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest
import pathpy as pp
import numpy as np
import random
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

# test magic methods
# ------------------


def test_setitem():
    """Test the assignment of attributes."""

    net = Network()
    net['city'] = 'Zurich'

    assert net['city'] == 'Zurich'


def test_getitem():
    """Test the extraction of attributes."""

    net = Network(city='London')

    assert net['city'] == 'London'
    assert net['attribute not in dict'] == None


def test_str():
    """Test string representations of the network."""
    net = Network()
    assert isinstance(net.summary(), str)


# Test properties
# ---------------


def test_uid():
    """Test the uid assignment."""
    net = Network(uid='test')

    assert isinstance(net, Network)
    assert isinstance(net.uid, str)
    assert net.uid == 'test'

    net = Network()

    assert isinstance(net, Network)
    assert isinstance(net.uid, str)


def test_directed():
    """Test if a network is directed."""

    net = Network()

    assert net.directed is True

    net = Network(directed=False)

    assert net.directed is False


def test_shape():
    """Test the shape of the network."""
    net = Network()
    assert net.shape == (0, 0)


# Test methods
# ------------


def test_update():
    """Test update network attributes."""

    net = Network(city='London')

    assert net['city'] == 'London'

    net.update(city='Vienna', year='1850')

    assert net['city'] == 'Vienna'
    assert net['year'] == '1850'


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
    # with pytest.raises(Exception):
    #     net.add_node(v)


def test_add_nodes():
    """Test assigning notes form a list."""
    net = Network()
    u = Node('u', color='blue')
    net.add_nodes(u, 'v', 'w', color='green')

    assert net.number_of_nodes() == 3
    assert net.nodes['u']['color'] == 'green'
    assert net.nodes['v']['color'] == 'green'
    assert net.nodes['w']['color'] == 'green'


def test_add_edge():
    """Test the edge assignment."""

    a = Node('a')
    b = Node('b')
    c = Node('c')

    # add edges with no uids
    e = Edge(a, b, uid='ab')
    f = Edge(b, c, uid='bc')
    g = Edge(a, b, uid='ab')

    net = Network()
    net.add_edge(e)
    net.add_edge(f)

    # with pytest.raises(Exception):
    #     net.add_edge(g)

    assert len(net.edges) == 2
    assert len(net.nodes) == 3

    # with pytest.raises(Exception):
    #     net.add_node(a)

    # with pytest.raises(Exception):
    #     net.add_edge(e)

    # add edges with uids
    e = Edge(a, b, uid='a-b')
    f = Edge(b, c, uid='b-c')
    g = Edge(a, b, uid='a-b')
    h = Edge(a, b, uid='ab')

    net = Network()
    net.add_edge(e)
    net.add_edge(f)

    # with pytest.raises(Exception):
    #     net.add_edge(h)

    assert len(net.edges) == 2
    assert len(net.nodes) == 3

    # with pytest.raises(Exception):
    #     net.add_edge(g)

    # with pytest.raises(Exception):
    #     net.add_edge(e)

    # add edges and nodes
    net = Network()
    net.add_edge(e)

    # # add new node with same uid
    # with pytest.raises(Exception):
    #     net.add_node('a')

    # # add same node
    # with pytest.raises(Exception):
    #     net.add_node(a)

    # add node and edge with the node
    a1 = Node('a')
    a2 = Node('a')
    b = Node('b')
    e1 = Edge(a2, b)
    net = Network()
    net.add_node(a1)

    # with pytest.raises(Exception):
    #     net.add_edge(e1)

    e2 = Edge(net.nodes['a'], b)
    net.add_edge(e2)

    # net add edge via string and nodes
    net = Network()
    net.add_node('a')
    net.add_node('b')
    net.add_edge('a', 'b')

    assert len(net.nodes) == 2
    assert len(net.edges) == 1

    # with pytest.raises(Exception):
    #     net.add_edge('a', 'b')

    net = Network(multiedges=True)
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

    # with pytest.raises(Exception):
    #     net.add_edge(a, 'b')

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
    assert net.edges['c-2-d'].v == 'c'

    net.add_edge('a', 'd', uid='a-d')
    assert net.edges['a-d'].uid == 'a-d'

    ab = Edge(Node('a'), Node('b'), uid='a-b')
    net = Network()
    net.add_edge(ab, color='blue')

    assert net.edges['a-b']['color'] == 'blue'

    net = Network()
    net.add_node("A")
    net.add_edge("A", "B")

    assert net.number_of_edges() == 1
    assert net.number_of_nodes() == 2

    net = Network()
    edges = [("A", "B"), ("B", "C")]
    for edge in edges:
        net.add_edge(edge)

    assert net.number_of_edges() == 2
    assert net.number_of_nodes() == 3


def test_call_edges():
    """Test to call edges"""

    net = Network()
    net.add_edge('a', 'b', uid='a-b')

    assert isinstance(net.edges['a-b'], Edge)

    assert net.edges['a-b'].uid == 'a-b'

    assert net.edges['a', 'b'].uid == 'a-b'

    net = Network(multiedges=True)
    net.add_edge('a', 'b')
    net.add_edge('a', 'b')
    net.add_edge('a', 'b', uid='a-b')

    assert net.number_of_edges() == 3
    assert len(net.edges['a', 'b']) == 3

    net = Network()
    net.add_edge('a', 'b')
    net.add_edge('b', 'a')

    assert net.number_of_edges() == 2

    net = Network(directed=False)
    net.add_edge('a', 'b')

    # with pytest.raises(Exception):
    #     net.add_edge('b', 'a')


def test_add_edges():
    """Test assigning edges form a list."""
    net = Network()
    ab = Edge(Node('a'), Node('b'))

    net.add_edges(ab, ('b', 'c'))

    assert net.number_of_edges() == 2

    net = Network()
    edges = [("A", "B"), ("B", "C")]
    net.add_edges(edges)

    assert net.number_of_edges() == 2
    assert net.number_of_nodes() == 3

    net = Network()
    edges = [("a", "b"),
             ("b", "c"),
             ("c", "d"),
             ("c", "e")]
    edges = [tuple(Node(x) for x in e) for e in edges]
    # with pytest.raises(Exception):
    #     net.add_edges(edges)


def test_properties():
    """Test network properties."""
    net = Network(directed=False)
    net.add_edge('a', 'b', uid='a-b')

    net.edges['a-b']['color'] = 'red'

    assert net.edges['a-b']['color'] == 'red'


def test_remove_edge():
    """Test to remove an edge from the network."""

    net = Network()
    a = Node('a')
    b = Node('b')
    c = Node('c')
    e = Edge(a, b, uid='e')
    f = Edge(b, a, uid='f')
    g = Edge(b, c, uid='g')
    net.add_edge(e)
    net.add_edge(f)

    net.remove_edge(g)

    assert net.number_of_edges() == 2
    assert isinstance(net.edges['e'], Edge)
    assert g not in net.edges
    assert net.edges['a', 'b'] in net.edges

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

    net = Network(multiedges=True)
    net.add_edges(e, f, g)

    assert net.number_of_edges() == 3
    assert e and f and g in net.edges['a', 'b']

    net.remove_edge('a', 'b', uid='g')
    assert net.number_of_edges() == 2
    assert g not in net.edges['a', 'b']

    net.remove_edge('a', 'b')
    assert net.number_of_edges() == 0
    assert len(net.edges['a', 'b']) == 0


def test_remove_node():
    """Test to remove a node from the network."""

    net = Network(directed=True)
    net.add_edge('a', 'b')
    net.add_edge('a', 'c')
    net.add_edge('b', 'd')
    net.add_edge('b', 'e')
    net.add_edge('d', 'b')
    net.add_edge('d', 'e')
    net.add_edge('e', 'd')

    assert net.shape == (5, 7)

    net.remove_node('b')
    assert net.shape == (4, 3)


def test_get_edge():
    """Test to get edges."""
    net = Network(directed=False)
    net.add_edge('a', 'b')
    assert (('a', 'b') in net.edges) is True
    assert (('b', 'a') in net.edges) is True
    assert (('a', 'c') in net.edges) is False

    a = Node('a')
    b = Node('b')
    e = Edge(a, b)
    net = Network(directed=True)
    net.add_edge(e)
    assert ((a, b) in net.edges) is True
    assert (e in net.edges) is True
    assert (('a', b) in net.edges) is True
    assert ((b, a) in net.edges) is False


def test_network_properties():
    """Test network properties."""
    net = Network()
    net.add_edge('a', 'b', uid='a-b')
    net.add_edge('b', 'c', uid='b-c')
    net.add_edge('c', 'a', uid='c-a')

    assert net.successors['c'] == {net.nodes['a']}
    assert net.incoming['a'] == {net.edges['c-a']}

    net.remove_edge('c-a')

    assert net.successors['c'] == set()
    assert net.incoming['a'] == set()


def test_add_networks():
    """Test to add networks together"""
    net_1 = Network()
    net_1.add_edges(('a', 'b'), ('b', 'c'))

    net_2 = Network()
    net_2.add_edges(('x', 'y'), ('y', 'z'))

    # print(net_1)
    # print(net_2)

    net_3 = net_1 + net_2
    assert net_1.number_of_nodes() == 3
    assert net_1.number_of_edges() == 2
    assert net_2.number_of_nodes() == 3
    assert net_2.number_of_edges() == 2
    assert net_3.number_of_nodes() == 6
    assert net_3.number_of_edges() == 4

    # test same node objects
    a = Node('a')
    b = Node('b')
    c = Node('c')

    net_1 = Network()
    net_2 = Network()
    net_1.add_edge(a, b)
    net_2.add_edge(b, c)

    net_3 = net_1+net_2
    assert net_1.number_of_nodes() == 2
    assert net_1.number_of_edges() == 1
    assert net_2.number_of_nodes() == 2
    assert net_2.number_of_edges() == 1
    assert net_3.number_of_nodes() == 3
    assert net_3.number_of_edges() == 2

    # nodes with same uids but different objects
    net_1 = Network()
    net_2 = Network()
    net_1.add_edge(a, b)
    net_2.add_edge('b', c)

    # with pytest.raises(Exception):
    #     net_3 = net_1+net_2

    # test same edge objects

    a = Node('a')
    b = Node('b')
    c = Node('c')

    net_1 = Network()
    net_2 = Network()
    net_1.add_edge(a, b, uid='e1')
    net_2.add_edge(a, b, uid='e2')

    # with pytest.raises(Exception):
    #     net_3 = net_1+net_2
    # assert net_3.number_of_edges() == 2
    # assert net_3.number_of_nodes() == 2
    # assert 'e1' in net_3.edges and 'e2' in net_3.edges

    # edges with same uids but different objects
    net_1 = Network()
    net_2 = Network()
    net_1.add_edge(a, b, uid='e1')
    net_2.add_edge(a, b, uid='e1')

    # with pytest.raises(Exception):
    #     net_3 = net_1+net_2

    # add multiple networks
    net_1 = Network()
    net_2 = Network()
    net_3 = Network()
    net_1.add_edge('a', 'b')
    net_2.add_edge('c', 'd')
    net_3.add_edge('e', 'f')
    net_4 = net_1 + net_2 + net_3

    assert net_4.number_of_edges() == 3
    assert net_4.number_of_nodes() == 6

    # with pytest.raises(Exception):
    #     net_4 = net_1 + net_2 + net_3 + net_1


def test_iadd_networks():
    """Test to add networks together"""
    net_1 = Network()
    net_1.add_edges(('a', 'b'), ('b', 'c'))

    net_2 = Network()
    net_2.add_edges(('x', 'y'), ('y', 'z'))

    net_1 += net_2

    assert net_1.number_of_nodes() == 6
    assert net_1.number_of_edges() == 4
    assert net_2.number_of_nodes() == 3
    assert net_2.number_of_edges() == 2

    # test same node objects
    a = Node('a')
    b = Node('b')
    c = Node('c')

    net_1 = Network()
    net_2 = Network()
    net_1.add_edge(a, b)
    net_2.add_edge(b, c)

    net_1 += net_2
    assert net_1.number_of_nodes() == 3
    assert net_1.number_of_edges() == 2
    assert net_2.number_of_nodes() == 2
    assert net_2.number_of_edges() == 1

    # nodes with same uids but different objects
    net_1 = Network()
    net_2 = Network()
    net_1.add_edge(a, b)
    net_2.add_edge('b', c)

    # with pytest.raises(Exception):
    #     net_1 += net_2

    # test same edge objects
    a = Node('a')
    b = Node('b')
    c = Node('c')

    net_1 = Network()
    net_2 = Network()
    net_1.add_edge(a, b, uid='e1')
    net_2.add_edge(a, b, uid='e2')

    # with pytest.raises(Exception):
    #     net_1 += net_2
    # assert net_1.number_of_edges() == 2
    # assert net_1.number_of_nodes() == 2
    # assert 'e1' in net_1.edges and 'e2' in net_1.edges

    # edges with same uids but different objects
    net_1 = Network()
    net_2 = Network()
    net_1.add_edge(a, b, uid='e1')
    net_2.add_edge(a, b, uid='e1')

    # with pytest.raises(Exception):
    #     net_1 += net_2

    # add multiple networks
    net_1 = Network()
    net_2 = Network()
    net_3 = Network()
    net_1.add_edge('a', 'b')
    net_2.add_edge('c', 'd')
    net_3.add_edge('e', 'f')
    net_1 += net_2 + net_3

    assert net_1.number_of_edges() == 3
    assert net_1.number_of_nodes() == 6


def test_sub_networks():
    """Test to remove a network"""
    net_1 = Network()
    net_2 = Network()
    net_1.add_edge('a', 'b', uid='a-b')
    net_2.add_edge('c', 'd', uid='c-d')
    net_1 += net_2
    net_2.add_edge('d', 'e', uid='d-e')

    net_3 = net_1 - net_2

    assert net_3.number_of_nodes() == 2
    assert net_3.number_of_edges() == 1
    assert 'a' and 'b' in net_3.nodes
    assert 'a-b' in net_3.edges
    assert net_1.number_of_nodes() == 4
    assert net_1.number_of_edges() == 2
    assert net_2.number_of_nodes() == 3
    assert net_2.number_of_edges() == 2

    net_4 = Network()
    net_4.add_edge('x', 'y', uid='x-y')

    net_5 = net_3 - net_4

    assert net_5.number_of_nodes() == 2
    assert net_5.number_of_edges() == 1
    assert 'a' and 'b' in net_5.nodes
    assert 'a-b' in net_5.edges


def test_isub_networks():
    """Test to remove a network with isub"""
    net_1 = Network()
    net_2 = Network()
    net_1.add_edge('a', 'b', uid='a-b')
    net_2.add_edge('c', 'd', uid='c-d')
    net_1 += net_2
    net_2.add_edge('d', 'e', uid='d-e')

    net_1 -= net_2

    assert net_1.number_of_nodes() == 2
    assert net_1.number_of_edges() == 1
    assert 'a' and 'b' in net_1.nodes
    assert 'a-b' in net_1.edges
    assert net_2.number_of_nodes() == 3
    assert net_2.number_of_edges() == 2


def test_network_edges():
    """Test the edges of a network"""

    net = Network(directed=False)
    net.add_edges(('a', 'b'), ('b', 'c'), ('c', 'd'))
    assert net.number_of_edges() == 3
    assert isinstance(list(net.edges), list)

    # np does not allow to sample from iterables
    # edge = np.random.choice(list(net.edges.values()))
    edge = random.choice(list(net.edges))
    assert edge in net.edges


def test_network_degrees():
    """Test node degrees of a network"""

    a = Node('a')
    net = Network(directed=False)
    net.add_edges((a, 'b'), ('b', 'c'), ('c', 'a'))
    assert isinstance(list(net.nodes.keys())[0], (str, int))


def test_network_undirected():
    """Test undirected networks"""
    net = Network(directed=False)
    net.add_edge('a', 'b', timestamp=1, color='red', size=4)
    net.add_edge('b', 'a', timestamp=3, color='blue', frequency=30)

    assert net.number_of_edges() == 1

    print(net.edges['a', 'b'].attributes)
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
