#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_algorithms.py -- Test environment for basic algorithms
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-03-29 16:18 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import pytest
import pathpy as pp

@pytest.fixture(params=[True, False])
def net(request):
    n = pp.generators.ER_nm(100, 400, directed=request.param)

    return n

@pytest.fixture
def temp_net(request):
    n = pp.TemporalNetwork(directed=True)
    n.add_edge('a', 'b', color='red', timestamp=1)
    n.add_edge('b', 'c', color='green', timestamp=2)
    n.add_edge('c', 'd', color='yellow', timestamp=3)

    return n


def test_train_test_split_network(net):
    """
    Test train test split in static network
    """
    train, test = pp.algorithms.evaluation.train_test_split(net, split='node', test_size=0.25)
    assert train.number_of_nodes() == 75
    assert test.number_of_nodes() == 25

    train, test = pp.algorithms.evaluation.train_test_split(net, split='edge')
    assert train.number_of_edges() == 300
    assert test.number_of_edges() == 100



def test_shuffle_temporal_network(temp_net):
    """
    Test shuffle method in temporal networks
    """
    t = pp.algorithms.evaluation.shuffle_temporal_network(temp_net)

    assert t.number_of_nodes() == temp_net.number_of_nodes()
    assert t.number_of_edges() == temp_net.number_of_edges()