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
from typing import TYPE_CHECKING, Any, Optional

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.core.network import Network

from numpy.random import choice
from pathpy import logger, tqdm

from ..core import edge as edge
from ..core import network as net
from ..core import node as node

# create logger
LOG = logger(__name__)


def train_test_split(network: Network, test_size: Optional[float]=0.25, train_size: Optional[float]=None, split: Optional[str]='node') -> tuple(Network, Network):
    """
    Performs a random split of a network into a training and test network. The split can be performed along nodes or edges
    """
    test_network = net.Network(directed=network.directed, multiedges=network.multiedges, uid=network.uid+'_test')
    train_network = net.Network(directed=network.directed, multiedges=network.multiedges, uid=network.uid+'_train')

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


def adjusted_mutual_information(clustering_1: dict, clustering_2: dict):
    raise NotImplementedError()