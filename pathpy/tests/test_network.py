#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_network.py -- Test environment for the Network class
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2019-09-10 16:56 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest

from pathpy import Node, Edge, Network

# Test network
# ------------


@pytest.fixture(params=[True, False])
def net(request):
    net = Network(directed=request.param)
    net.add_edge('ab', 'a', 'b')
    net.add_edge('bc', 'b', 'c')
    net.add_edge('cd', 'c', 'd')
    net.add_edge('ab2', 'a', 'b')
    return net

# Test magic methods
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
    with pytest.raises(KeyError):
        net['attribute not in dict']

# Test properties
# ---------------


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

# Test methods
# ------------


def test_update():
    """Test update network attributes."""

    net = Network(city='London')

    assert net['city'] == 'London'

    net.update(city='Vienna', year='1850')

    assert net['city'] == 'Vienna'
    assert net['year'] == '1850'


def test_number_of_edges():
    """Test the number of edges."""
    pass


def test_number_of_nodes():
    """Test the number of nodes."""
    pass


def test_add_node():
    """Test the node assignment."""

    net = Network()
    net.add_node('v', color='red')

    assert net.number_of_nodes() == 1
    assert isinstance(net.nodes['v'], Node)
    assert net.nodes['v'].id == 'v'
    assert net.nodes['v']['color'] == 'red'

    w = Node('w', color='green')
    net.add_node(w)

    assert net.number_of_nodes() == 2
    assert isinstance(net.nodes['w'], Node)
    assert net.nodes['w'].id == 'w'
    assert net.nodes['w']['color'] == 'green'


def test_add_nodes_from():
    """Test assigning notes form a list."""
    net = Network()
    u = Node('u')
    net.add_nodes_from([u, 'v', 'w'], color='green')

    assert net.number_of_nodes() == 3
    assert net.nodes['u']['color'] == 'green'


def test_add_edge():
    """Test the edge assignment."""

    net = Network()
    net.add_edge('ab', 'a', 'b', length=10)

    assert net.number_of_nodes() == 2
    assert net.number_of_edges() == 1
    assert isinstance(net.edges['ab'], Edge)
    assert net.edges['ab'].id == 'ab'
    assert net.edges['ab'].directed is True
    assert net.edges['ab']['length'] == 10
    assert net.nodes['a'].id == 'a'
    assert net.nodes['b'].id == 'b'

    c = Node('c')
    net.add_edge('bc', 'b', c, length=5)

    assert net.number_of_edges() == 2

    with pytest.raises(ValueError):
        cd = Edge('cd', c, 'd', directed=False)
        net.add_edge(cd)

    cd = Edge('cd', c, 'd')
    net.add_edge(cd)

    assert net.number_of_edges() == 3
    assert net.edges['cd'].v.id == 'c'

    with pytest.raises(Exception):
        net.add_edge('de')

    with pytest.raises(Exception):
        net.add_edge(cd, 'd')

    net.add_edge('a', 'd')
    assert net.edges['a-d'].id == 'a-d'

    net.add_edge('b', 'd', separator='=')
    assert net.edges['b=d'].id == 'b=d'


def test_add_edges_from():
    """Test assigning edges form a list."""
    pass


def test_remove_node(net):
    """Test to remove node from a network."""

    non = net.number_of_nodes()
    noe = net.number_of_edges()

    # number of edges sharing the node b
    n2e = len(net.nodes['b'].adjacent_edges)

    print(net.nodes)
    print(net.edges)
    net.remove_node('b')

    print(net.nodes)
    print(net.edges)

    assert net.number_of_nodes() == non - 1
    assert net.number_of_edges() == noe - n2e

    net.remove_node('not a node')


def test_remove_nodes_from(net):
    """Test to remove multiple nodes."""

    non = net.number_of_nodes()
    noe = net.number_of_edges()

    # number of edges sharing node a and b
    a2e = net.nodes['a'].adjacent_edges
    b2e = net.nodes['b'].adjacent_edges
    n2e = len(a2e.union(b2e))

    # net.remove_nodes_from(['a', 'b'])

    # assert net.number_of_nodes() == non - 2
    # assert net.number_of_edges() == noe - n2e


def test_add_edges_from():
    net = Network()
    ab = Edge('ab', 'a', 'b')

    net.add_edges_from([ab, ('bc', 'b', 'c')])

    assert net.number_of_edges() == 2
    assert net.edges['ab'].id == 'ab'

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
