"""Algorithms for model evaluation."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : centralities.py -- Module to calculate node centrality measures
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Sun 2021-04-17 01:07 ingo>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union
from functools import singledispatch

from numpy.random import choice

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.models.api import Network
    from pathpy.models.api import TemporalNetwork

from pathpy import logger
from pathpy.models.network import Network
from pathpy.models.temporal_network import TemporalNetwork

# create logger
LOG = logger(__name__)

@singledispatch
def train_test_split(network: Union[Network, TemporalNetwork], test_size: Optional[float]=0.25, train_size: Optional[float]=None, split: Optional[str]='node') -> tuple(Union[Network,TemporalNetwork], Union[Network, TemporalNetwork]):
    """Returns a train/test split of a network object. This method is implemented for instances of Network and TemporalNetwork. The train/test split is non-destructive and based on object references, i.e. this function will return copies of the Network instance that contain references to the same node/edge objects.

    Parameters
    ----------

    network: Union[Network, TemporalNetwork]

        The network or temporal network for which the train/test split shall be performed.

    test_size: Optional[float] = 0.25

        Fraction of the network to include in the test network

    train_size: Optional[float] = 0.25

        Fraction of the network to include in the training network

    split: Optional['str'] = 'node'

        Specifies how the train/test split shall be performed. For 'node' a random subset of nodes is selected, while for 'edge' a random subset of edges is selected.

    Returns
    -------

    Tuple (n1, n2) where n1 is the test network and n2 is the training network

    Examples
    --------

    >>> n = pp.Network() 
    >>> n.add_edge('a', 'b')
    >>> n.add_edge('b', 'c')
    >>> n.add_edge('c', 'd')
    >>> n.add_edge('d', 'a')
    >>> test, train = train_test_split(n, test_size=0.25)
    >>> print(test)    
    >>> print(train)
    Network with one node
    Network with three nodes

    """
    raise NotImplementedError


@train_test_split.register(Network)
def _split_network(network: Network, test_size: Optional[float]=0.25, train_size: Optional[float]=None, split: Optional[str]='node') -> tuple(Network, Network):
    """
    Performs a random split of a static network into a training and test network. The split can be performed along nodes or edges.
    """
    test_network = Network(directed=network.directed, multiedges=network.multiedges, uid=network.uid+'_test')
    train_network = Network(directed=network.directed, multiedges=network.multiedges, uid=network.uid+'_train')

    if train_size == None:
        ts = test_size
    else:
        ts = 1.0 - train_size

    if split == 'node':
        test_nodes = choice([v for v in network.nodes], size=int(ts*network.number_of_nodes()), replace=False)
        for v in test_nodes:
            test_network.add_node(v)
        train_nodes = [v for v in network.nodes if v.uid not in test_network.nodes.uids]
        for v in train_nodes:
            train_network.add_node(v)
        for e in network.edges:
            if e.v.uid in test_network.nodes.uids and e.w.uid in test_network.nodes.uids:
                test_network.add_edge(e)
            if e.v.uid in train_network.nodes.uids and e.w.uid in train_network.nodes.uids:
                train_network.add_edge(e)
    
    elif split == 'edge':
        for v in network.nodes:
            test_network.add_node(v)
            train_network.add_node(v)
        test_edges = choice([e for e in network.edges], size=int(ts*network.number_of_edges()), replace=False)
        for e in test_edges:
            test_network.add_edge(e)
        train_edges = [e for e in network.edges if e.uid not in test_network.edges.uids]
        for e in train_edges:
            train_network.add_edges(e)
    else:
        raise AttributeError('Unknown split method "{0}"'.format(split))

    return test_network, train_network


@train_test_split.register(TemporalNetwork)
def _split_temporal_network(network: TemporalNetwork, test_size: Optional[float]=0.25, train_size: Optional[float]=None, split: Optional[str]='time') -> tuple(TemporalNetwork, TemporalNetwork):
    """
    Performs a random split of a temporal network into a training and test network. The split can be performed along nodes, interactions, or time
    """
    test_network = TemporalNetwork(directed=network.directed, multiedges=network.multiedges, uid=network.uid+'_test')
    train_network = TemporalNetwork(directed=network.directed, multiedges=network.multiedges, uid=network.uid+'_train')

    return test_network, train_network


def adjusted_mutual_information(clustering_1: dict, clustering_2: dict):
    raise NotImplementedError()