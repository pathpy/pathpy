#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_network.py -- Test environment for the Network class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-10-31 14:18 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest
from pathpy import Node, Edge, Path, Network

# Test network
# ------------


# @pytest.fixture(params=[True, False])
# def net(request):
#     net = Network(directed=request.param)
#     net.add_edge('ab', 'a', 'b')
#     net.add_edge('bc', 'b', 'c')
#     net.add_edge('cd', 'c', 'd')
#     net.add_edge('ab2', 'a', 'b')
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


def test_name():
    """Test the name assignment."""

    net = Network()

    assert isinstance(net, Network)

    assert net.name == ''

    net.name = 'my network'

    assert net.name == 'my network'

    net = Network(name='an other network')

    assert net.name == 'an other network'


def test_directed():
    """Test if a network is directed."""

    net = Network()

    assert net.directed is True

    net = Network(directed=False)

    assert net.directed is False


def test_shape():
    """Test the shape of the network."""
    pass


# # Test methods
# # ------------


def test_update():
    """Test update network attributes."""

    net = Network(city='London')

    assert net['city'] == 'London'

    net.update(city='Vienna', year='1850')

    assert net['city'] == 'Vienna'
    assert net['year'] == '1850'


def test_add_path():
    """Test the path assignment."""

    p1 = Path('a', 'b', 'c', 'a', 'b')
    p2 = Path('d', 'b', 'e')

    net = Network()

    net.add_path(p1)

    assert net.number_of_nodes() == 3
    assert net.number_of_nodes() == 3
    assert net.number_of_paths() == 1

    net.add_path(p2)

    assert net.number_of_paths() == 2


def test_number_of_nodes():
    """Test the number of nodes."""

    net = Network(Path('a', 'b', 'c', 'a', 'b'))

    assert net.number_of_nodes() == 3

    assert net.number_of_nodes(unique=False) == 5


def test_number_of_edges():
    """Test the number of edges."""
    net = Network(Path('a', 'b', 'c', 'a', 'b'))

    assert net.number_of_edges() == 3

    assert net.number_of_edges(unique=False) == 4


def test_number_of_paths():
    """Test the number of edges."""
    p1 = Path('a', 'b', 'c')
    p2 = Path('d', 'b', 'e')
    net = Network(p1, p2, p1)

    assert net.number_of_paths() == 2

    assert net.number_of_paths(unique=False) == 3


def test_add_node():
    """Test the node assignment."""

    net = Network()
    net.add_node('v', color='red')

    assert net.number_of_nodes() == 1
    assert isinstance(net.nodes['v'], Node)
    assert net.nodes['v'].uid == 'v'
    assert net.nodes['v']['color'] == 'red'

    w = Node('w', color='green')
    net.add_node(w)

    assert net.number_of_nodes() == 2
    assert isinstance(net.nodes['w'], Node)
    assert net.nodes['w'].uid == 'w'
    assert net.nodes['w']['color'] == 'green'

    v = Node('v', color='blue')
    net.add_node(v)

    assert net.number_of_nodes() == 2
    assert net.number_of_nodes(unique=False) == 3
    assert net.nodes['v']['color'] == 'blue'


def test_add_nodes_from():
    """Test assigning notes form a list."""
    net = Network()
    u = Node('u')
    net.add_nodes_from([u, 'v', 'w'], color='green')

    assert net.number_of_nodes() == 3
    assert net.nodes['u']['color'] == 'green'
    assert net.nodes['v']['color'] == 'green'
    assert net.nodes['w']['color'] == 'green'


def test_add_edge():
    """Test the edge assignment."""

    net = Network()
    net.add_edge('a', 'b', length=10)

    assert net.number_of_nodes() == 2
    assert net.number_of_edges() == 1
    assert isinstance(net.edges['a-b'], Edge)
    assert net.edges['a-b'].uid == 'a-b'
    assert net.edges['a-b'].directed is True
    assert net.edges['a-b']['length'] == 10
    assert net.nodes['a'].uid == 'a'
    assert net.nodes['b'].uid == 'b'

    b = Node('b')
    c = Node('c')
    net.add_edge(b, c, length=5)

    assert net.number_of_edges() == 2

    net.add_edge('c-d')

    assert net.number_of_edges() == 3
    assert net.edges['c-d'].v.uid == 'c'

    net.add_edge('a', 'd')
    assert net.edges['a-d'].uid == 'a-d'

    net.add_edge('b', 'd', separator='=')
    assert net.edges['b=d'].uid == 'b=d'

    ab = Edge('a', 'b')
    net = Network()
    net.add_edge(ab, color='blue')

    assert net.edges['a-b']['color'] == 'blue'

    net.add_edge(ab, color='blue')
    assert sum(net.edges.counter().values()) == 2

    bc = Edge('b', 'c')
    net.add_edge(bc, color='red')

    assert sum(net.edges.counter().values()) == 3
    assert net.nodes.counter()['b'] == 3

# def test_add_edges_from():
#     """Test assigning edges form a list."""
#     net = Network()
#     ab = Edge('ab', 'a', 'b')

#     net.add_edges_from([ab, ('bc', 'b', 'c')])

#     assert net.number_of_edges() == 2
#     assert net.edges['ab'].id == 'ab'


# def test_remove_node(net):
#     """Test to remove node from a network."""

#     non = net.number_of_nodes()
#     noe = net.number_of_edges()

#     # number of edges sharing the node b
#     n2e = len(net.nodes['b'].adjacent_edges)

#     net.remove_node('b')

#     assert net.number_of_nodes() == non - 1
#     assert net.number_of_edges() == noe - n2e

#     net.remove_node('not a node')


# def test_remove_nodes_from(net):
#     """Test to remove multiple nodes."""

#     non = net.number_of_nodes()
#     noe = net.number_of_edges()

#     # number of edges sharing node a and b
#     a2e = net.nodes['a'].adjacent_edges
#     b2e = net.nodes['b'].adjacent_edges
#     n2e = len(a2e.union(b2e))

#     net.remove_nodes_from(['a', 'b'])

#     assert net.number_of_nodes() == non - 2
#     assert net.number_of_edges() == noe - n2e


# def test_remove_edge(net):
#     """Test to remve a single edge."""

#     noe = net.number_of_edges()

#     net.remove_edge('cd')

#     assert net.number_of_edges() == noe - 1

#     with pytest.raises(ValueError):
#         net.remove_edge('a', 'b')

#     n2e = net.node_to_edges_map

#     assert len(n2e[('a', 'b')]) == 2
#     assert 'ab' in n2e[('a', 'b')] and 'ab2' in n2e[('a', 'b')]

#     net.remove_edge('ab')
#     n2e = net.node_to_edges_map

#     assert len(n2e[('a', 'b')]) == 1
#     assert 'ab' not in n2e[('a', 'b')] and 'ab2' in n2e[('a', 'b')]
#     assert net.number_of_edges() == noe - 2

#     net.remove_edge('a', 'b')
#     assert net.number_of_edges() == noe - 3


# def test_remove_edges_from(net):
#     """Test to remove edges from a list."""
#     noe = net.number_of_edges()

#     net.remove_edges_from(['ab', 'ab2', ('b', 'c')])

#     assert net.number_of_edges() == noe - 3


# def test_has_edge(net):
#     """Test if an edge is in the network."""

#     assert net.has_edge('ab') is True
#     assert net.has_edge('not an edge') is False
#     assert net.has_edge('a', 'b') is True

# # Test external methods
# # ---------------------


# def test_adjacency_matrix():
#     """Test the adjacency matrix."""
#     net = Network()
#     net.add_edges_from([('a', 'b'), ('b', 'c')])

#     A = net.adjacency_matrix()

#     assert A[0, 1] == 1.
#     # print('')
#     # print(type(A.todense()))
#     # print(A[0, 1])
#     # assert A == _A

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
