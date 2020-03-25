#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : shortest_paths.py -- Module to calculate shortest paths and diameter
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Wed 2020-03-25 11:48 scholtes>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List, Dict, Tuple, Optional
from functools import singledispatch
from collections import Counter
from collections import defaultdict
import datetime
import sys
from scipy.sparse import csgraph
import numpy as np


from .. import config, logger, tqdm
from ..core.base import BaseNetwork
from ..core import Path

# create logger
log = logger(__name__)


def distance_matrix(network, weighted: bool = False) -> np.ndarray:
    """Calculates shortest path distances between all pairs of nodes

    .. note::

        Shortest paths are calculated using the implementation 
        of the Floyd-Warshall algorithm provided in `scipy.csgraph`.

    Parameters
        ----------
        network : Network

            The :py:class:`Network` object that contains the network

        weighted : bool

            If True cheapest paths will be calculated.

        Examples
        --------
        Generate a path and add it to the network.

        >>> import pathpy as pp
        >>> net = pp.Network()
        >>> p = pp.Path('a', 'x', 'y', 'c')        
        >>> m = pp.algorithms.shortest_paths.distance_matrix(net)
        >>> m[0,3]
        3

        Add shorter path

        >>> p = pp.Path('a', 'x', 'c')
        >>> m = pp.algorithms.shortest_paths.distance_matrix(net)
        >>> m[0,3]
        2
    """

    A = network.adjacency_matrix(weighted=weighted)
    dist_matrix = csgraph.floyd_warshall(A, network.directed, unweighted=(not weighted), overwrite=False)

    return dist_matrix

def all_shortest_paths(network, weighted: bool = False) -> defaultdict:
    """Calculates shortest paths between all pairs of nodes.

    .. note::

        Shortest paths are calculated using a custom implementation of
        the Floyd-Warshall algorithm.

    Parameters
        ----------
        network : Network

            The :py:class:`Network` object that contains the network

        weighted : bool

            If True cheapest paths will be calculated.

        Examples
        --------
        Generate a path and add it to the network.

        >>> import pathpy as pp
        >>> net = pp.Network()
        >>> p = pp.Path('a', 'x', 'c')        
        >>> paths = pp.algorithms.shortest_paths.all_shortest_paths(net)
        >>> paths['a']['c']
        ('a', 'x', 'c')

        Add additional path

        >>> p = pp.Path('a', 'y', 'c')
        >>> paths = pp.algorithms.shortest_paths.all_shortest_paths(net)
        >>> paths['a']['c']
        ('a', 'x', 'c')
    """

    dist = defaultdict(lambda: defaultdict(lambda: np.inf))
    s_p = defaultdict(lambda: defaultdict(set))

    for e in network.edges:
        # set distances between neighbors to 1
        dist[network.edges[e].v.uid][network.edges[e].w.uid] = 1
        s_p[network.edges[e].v.uid][network.edges[e].w.uid].add((network.edges[e].v.uid, network.edges[e].w.uid))
        if not network.edges[e].directed:
            dist[network.edges[e].w.uid][network.edges[e].v.uid] = 1
            s_p[network.edges[e].w.uid][network.edges[e].v.uid].add((network.edges[e].w.uid, network.edges[e].v.uid))

    for k in tqdm(network.nodes, desc='all_shortest_paths'):
        for v in network.nodes:
            for w in network.nodes:
                if v != w:
                    if dist[v][w] > dist[v][k] + dist[k][w]:
                        # we have found a shorter path
                        dist[v][w] = dist[v][k] + dist[k][w]
                        s_p[v][w] = set()
                        for p in list(s_p[v][k]):
                            for q in list(s_p[k][w]):
                                s_p[v][w].add(p + q[1:])
                    elif dist[v][w] == dist[v][k] + dist[k][w]:
                        # we have found another shortest path
                        for p in list(s_p[v][k]):
                            for q in list(s_p[k][w]):
                                s_p[v][w].add(p + q[1:])

    for v in network.nodes:
        dist[v][v] = 0
        s_p[v][v].add((v,))

    return s_p

def diameter(network, weighted: bool = False) -> float:
    """Calculates the length of the longest shortest path

    .. note::

        Shortest path lengths are calculated using the implementation
        of the Floyd-Warshall algorithm in scipy.csgraph.

    Parameters
        ----------
        network : Network

            The :py:class:`Network` object that contains the network

        weighted : bool

            If True cheapest paths will be calculated.

        Examples
        --------
        Generate simple network

        >>> import pathpy as pp
        >>> net = pp.Network(directed=False)
        >>> net.add_edge('a', 'x')
        >>> net.add_edge('x', 'c')
        >>> pp.algorithms.shortest_paths.diameter(net)
        2

        Add additional path

        >>> net.add_edge('a', 'c')
        >>> pp.algorithms.shortest_paths.diameter(net)
        1
    """
    return np.max(distance_matrix(network, weighted))

def avg_path_length(network, weighted: bool = False) -> float:
    """Calculates the average shortest path length

    .. note::

        Shortest path lengths are calculated using the implementation
        of the Floyd-Warshall algorithm in scipy.csgraph.

    Parameters
        ----------
        network : Network

            The :py:class:`Network` object that contains the network

        weighted : bool

            If True cheapest paths will be calculated.

        Examples
        --------
        Generate simple network

        >>> import pathpy as pp
        >>> net = pp.Network(directed=False)
        >>> net.add_edge('a', 'x')
        >>> net.add_edge('x', 'c')
        >>> pp.algorithms.shortest_paths.avg_path_length(net)
        0.6667
    """
    return np.mean(distance_matrix(network, weighted))
