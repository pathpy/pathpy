""""Algorithms for shortest paths calculations."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : shortest_paths.py -- Module to calculate shortest paths and diameter
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Sun 2020-04-19 07:38 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Any, List, Dict, Tuple, Optional, Union
from collections import defaultdict
import numpy as np
from scipy.sparse import csgraph  # pylint: disable=import-error


from pathpy import logger, tqdm

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.core.network import Network

# from pathpy.core.path import Path

# create logger
LOG = logger(__name__)


def distance_matrix(network: Network,
                    weight: Union[str, bool, None] = None) -> np.ndarray:
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
    >>> net.add_edges(('a', 'x'), ('x', 'y'), ('y', 'c'))
    >>> m = pp.algorithms.shortest_paths.distance_matrix(net)
    >>> m[0,3]
    3

    Add shorter path

    >>> net.add_edges(('a', 'x'), ('x', 'c'))
    >>> m = pp.algorithms.shortest_paths.distance_matrix(net)
    >>> m[0,3]
    2
    """

    A = network.adjacency_matrix(weight=weight)
    dist_matrix = csgraph.floyd_warshall(
        A, network.directed, unweighted=(not weight), overwrite=False)

    return dist_matrix


def all_shortest_paths(network: Network,
                       weight: Union[str, bool, None] = None) -> defaultdict:
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
    >>> net.add_edges(('a', 'x'), ('x', 'c'))
    >>> paths = pp.algorithms.shortest_paths.all_shortest_paths(net)
    >>> paths['a']['c']
    {('a', 'x', 'c')}

    Add additional path

    >>> net.add_edges(('a', 'y'), ('y', 'c'))
    >>> paths = pp.algorithms.shortest_paths.all_shortest_paths(net)
    >>> paths['a']['c']
    {('a', 'x', 'c'), ('a', 'y', 'c')}

    """

    dist: defaultdict = defaultdict(lambda: defaultdict(lambda: np.inf))
    s_p: defaultdict = defaultdict(lambda: defaultdict(set))

    for e in network.edges:
        # set distances between neighbors to 1
        dist[e.v.uid][e.w.uid] = 1
        s_p[e.v.uid][e.w.uid].add((e.v.uid, e.w.uid))
        if not network.directed:
            dist[e.w.uid][e.v.uid] = 1
            s_p[e.w.uid][e.v.uid].add((e.w.uid, e.v.uid))

    for k in tqdm(network.nodes.keys(), desc='all_shortest_paths'):
        for v in network.nodes.keys():
            for w in network.nodes.keys():
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

    for v in network.nodes.keys():
        dist[v][v] = 0
        s_p[v][v].add((v,))

    return s_p


def diameter(network: Network,
             weight: Union[str, bool, None] = None) -> float:
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
    return np.max(distance_matrix(network, weight=weight))


def avg_path_length(network: Network,
                    weight: Union[str, bool, None] = None) -> float:
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
    0.6667 # TODO is this correct or shoudl it be 0.888888?
    """
    return np.mean(distance_matrix(network, weight=weight))
