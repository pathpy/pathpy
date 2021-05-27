#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_algorithms.py -- Test environment for basic algorithms
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2021-05-27 09:46 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest
from pathpy import Network
import pathpy as pp
import numpy as np

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


def test_degree_sequence():
    """Test the degree sequence of a network."""
    net = pp.Network(directed=False)
    net.add_edge('a', 'b', weight=2.1)
    net.add_edge('a', 'c', weight=1.0)

    s = pp.statistics.degrees.degree_sequence(net)
    assert np.array_equal(s, np.array([2., 1., 1.]))

    s = pp.statistics.degrees.degree_sequence(net, weight=True)
    assert np.array_equal(s, np.array([3.1, 2.1, 1.]))


def test_degree_distribution():
    """Test the degree distribution of a network."""
    net = pp.Network(directed=False)
    net.add_edge('a', 'b', weight=2.1)
    net.add_edge('a', 'c', weight=1.0)

    s = pp.statistics.degrees.degree_distribution(net)
    assert s == {2: 1/3, 1: 2/3}

    s = pp.statistics.degrees.degree_distribution(net, weight=True)
    assert s == {3.1: 1/3, 2.1: 1/3, 1.: 1/3}


def test_degree_raw_moment():
    """Test the degree raw moment of a network."""
    net = pp.Network(directed=False)
    net.add_edge('a', 'b', weight=2.1)
    net.add_edge('a', 'c', weight=1.0)

    s = pp.statistics.degrees.degree_raw_moment(net)
    assert s == 4/3

    s = pp.statistics.degrees.degree_raw_moment(net, weight=True)


def test_degree_central_moment():
    """Test the degree central moment of a network."""
    net = pp.Network(directed=False)
    net.add_edge('a', 'b', weight=2.1)
    net.add_edge('a', 'c', weight=1.0)

    s = pp.statistics.degrees.degree_central_moment(net)
    # print(s)

    s = pp.statistics.degrees.degree_central_moment(net, weight=True)
    # print(s)


def test_degree_assortativity():
    """Test the degree assortativity of a network."""
    net = pp.Network(directed=False)
    net.add_edge('a', 'b', weight=2.1)
    net.add_edge('a', 'c', weight=1.0)

    s = pp.statistics.degrees.degree_assortativity(net)
    # print(s)

    # s = pp.statistics.degrees.degree_central_moment(net, weight=True)
    # # print(s)


def test_mean_degree():
    """Test the mean degree calculation."""
    # net = pp.generators.Molloy_Reed([2]*500)

    net = Network(directed=False)
    net.add_edges(('a', 'b'), ('b', 'c'), ('c', 'a'))

    mean_degree = pp.statistics.mean_degree(net)
    assert mean_degree == 2.0


def test_local_clustering_coefficient():
    """Test the degree assortativity of a network."""
    net = pp.Network(directed=False)
    net.add_edge('a', 'b', weight=2.1)
    net.add_edge('b', 'c', weight=1.0)
    net.add_edge('c', 'a', weight=1.0)
    net.add_edge('b', 'd', weight=1.0)
    net.add_edge('d', 'e', weight=1.0)
    net.add_edge('e', 'b', weight=1.0)

    s = pp.statistics.clustering.local_clustering_coefficient(net, 'b')
    # s = pp.statistics.degrees.degree_central_moment(net, weight=True)
    # # print(s)


# def test_avg_clustering_coefficient():
#     """Test the degree assortativity of a network."""
#     net = pp.Network(directed=False)
#     net.add_edge('a', 'b', weight=2.1)
#     net.add_edge('b', 'c', weight=1.0)
#     net.add_edge('b', 'd', weight=1.0)

#     s = pp.statistics.clustering.avg_clustering_coefficient(net)
#     print(s)
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
