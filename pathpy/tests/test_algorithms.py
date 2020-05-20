#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_algorithms.py -- Test environment for basic algorithms
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2020-05-14 15:44 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest
from pathpy import Network
import pathpy as pp


# @pytest.mark.parametrize('directed', (True, False))
# @pytest.mark.parametrize('weighted', (True, False))
@pytest.fixture(params=[True, False])
def net(request):
    net = pp.Network(directed=False)
    net.add_edge('a', 'b')
    net.add_edge('b', 'c')
    net.add_edge('c', 'a')
    net.add_edge('b', 'd')
    # net.add_edge('d','b')
    net.add_edge('d', 'e')
    net.add_edge('e', 'f')
    net.add_edge('f', 'd')
    # net.add_edge('f','e')
    net.add_edge('f', 'g')
    net.add_edge('g', 'd')

    return net


def test_adjacency_matrix():
    """Test the adjacency matrix of a network."""
    net = Network()
    net.add_edges(('a', 'b'), ('b', 'c'))

    A1 = net.adjacency_matrix()
    assert A1[0, 1] == 1.0
    assert A1[1, 2] == 1.0

    A2 = pp.algorithms.matrices.adjacency_matrix(net)
    assert A2[0, 1] == 1.0
    assert A2[1, 2] == 1.0


def test_distance_matrix():
    """Test the disance matrix of a network."""
    net = pp.Network()
    net.add_edges(('a', 'x'), ('x', 'y'), ('y', 'c'))
    m = pp.algorithms.shortest_paths.distance_matrix(net)

    assert m[0, 3] == 3
    assert net.distance_matrix()[0, 3] == 3

    net.add_edges(('x', 'c'))
    m = pp.algorithms.shortest_paths.distance_matrix(net)

    assert m[0, 3] == 2
    assert net.distance_matrix()[0, 3] == 2


def test_all_shortest_paths():
    """Test all shortest paths in a network."""
    net = pp.Network()
    net.add_edges(('a', 'x'), ('x', 'c'))
    paths, m = pp.algorithms.shortest_paths.all_shortest_paths(net)

    assert paths['a']['c'] == {('a', 'x', 'c')}

    net.add_edges(('a', 'y'), ('y', 'c'))
    paths, m = pp.algorithms.shortest_paths.all_shortest_paths(net)

    assert paths['a']['c'] == {('a', 'x', 'c'), ('a', 'y', 'c')}


def test_diameter():
    """Test the diameter of the network."""
    net = pp.Network(directed=False)
    net.add_edge('a', 'x')
    net.add_edge('x', 'c')
    assert pp.algorithms.shortest_paths.diameter(net) == 2
    assert net.diameter() == 2

    net.add_edge('a', 'c')
    assert pp.algorithms.shortest_paths.diameter(net) == 1
    assert net.diameter() == 1


def test_avg_path_length():
    """Test the average path length of the network."""
    net = pp.Network(directed=False)
    net.add_edge('a', 'x')
    net.add_edge('x', 'c')
    assert pp.algorithms.shortest_paths.avg_path_length(net) == 8/6


def test_betweenness_centrality(net):
    """Test the betweenness centrality of a network."""
    net = pp.Network(directed=False)
    net.add_edge('a', 'x')
    net.add_edge('x', 'b')
    c = pp.algorithms.centralities.betweenness_centrality(net)
    assert c['x'] == 2

    # print(net.adjacency_matrix().todense())
    # c = pp.algorithms.centralities.betweenness_centrality(net)
    # print(c['b'])


def test_closeness_centrality():
    """Test the betweenness centrality of a network."""
    net = pp.Network(directed=False)
    net.add_edge('a', 'x')
    net.add_edge('x', 'b')
    c = pp.algorithms.centralities.closeness_centrality(net)
    assert c['a'] == 1/3


def test_degree_centrality():
    """Test the betweenness centrality of a network."""
    net = pp.Network(directed=True)
    net.add_edge('a', 'x')
    net.add_edge('x', 'b')
    c = pp.algorithms.centralities.degree_centrality(net)
    assert c['a'] == 1

    c = pp.algorithms.centralities.degree_centrality(net, mode='indegree')
    assert c['a'] == 0


def test_rank_centralities():
    """Test the betweenness centrality of a network."""
    centralities = {'a': .2, 'b': .8, 'c': .5}
    rc = pp.algorithms.centralities.rank_centralities(centralities)
    assert rc == [('b', 0.8), ('c', 0.5), ('a', 0.2)]


def test_find_connected_components():
    """Test to find the connected components."""
    net = Network(directed=False)
    net.add_edge('a', 'b')
    net.add_edge('b', 'c')
    net.add_edge('x', 'y')
    cn = pp.algorithms.components.find_connected_components(net)
    # print(cn)


def test_largest_connected_component():
    """Test to find the largest connected component."""
    net = Network(directed=False)
    net.add_edge('a', 'b')
    net.add_edge('b', 'c')
    net.add_edge('x', 'y')
    lcc = pp.algorithms.components.largest_connected_component(net)
    # print(lcc)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
