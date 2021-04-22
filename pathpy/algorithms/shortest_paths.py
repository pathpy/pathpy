""""Algorithms for shortest paths calculations."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : shortest_paths.py -- Module to calculate shortest paths and diameter
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Mon 2021-03-29 16:33 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, Union
from collections import defaultdict
import numpy as np
from scipy.sparse import csgraph  # pylint: disable=import-error
# from queue import PriorityQueue

from pathpy import logger, tqdm

from pathpy.models import network as net

# pseudo load class for type checking
if TYPE_CHECKING:
    # from pathpy.core.node import Node
    from pathpy.models.network import Network

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
                       weight: Union[str, bool, None] = None,
                       return_distance_matrix: bool = True
                       ) -> Union[defaultdict, Tuple[defaultdict, np.ndarray]]:
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
        cost = 1

        if weight is True:
            cost = e.attributes['weight']
        elif weight is not False and weight is not None:
            cost = e.attributes[weight]

        dist[e.v.uid][e.w.uid] = cost
        s_p[e.v.uid][e.w.uid].add((e.v.uid, e.w.uid))
        if not network.directed:
            dist[e.w.uid][e.v.uid] = cost
            s_p[e.w.uid][e.v.uid].add((e.w.uid, e.v.uid))

    for k in tqdm(network.nodes.keys(),
                  desc='calculating shortest paths between all nodes'):
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

    if return_distance_matrix:
        dist_arr = np.ndarray(
            shape=(network.number_of_nodes(), network.number_of_nodes()))
        for v in network.nodes:
            for w in network.nodes:
                dist_arr[network.nodes.index[v.uid],
                         network.nodes.index[w.uid]] = dist[v.uid][w.uid]
        return s_p, dist_arr
    else:
        return s_p


def single_source_shortest_paths(network: Network,
                                 source: str, weight: Union[bool, str, None] = None
                                 ) -> Union[dict, np.array]:
    """Calculates all shortest paths from a single given source node using a
    custom implementation of Dijkstra's algorithm based on a priority queue.
    """
    Q: dict = dict()
    dist = dict()
    prev = dict()
    dist[source] = 0

    for v in network.nodes.uids:
        if v != source:
            dist[v] = np.inf
            prev[v] = None
        Q[v] = dist[v]

    while Q:
        # TODO: Do this more efficiently with a proper priority queue
        u = min(Q.keys(), key=(lambda k: Q[k]))
        del Q[u]
        for v in network.successors[u]:

            # for networks with no edge costs, edges have constant cost
            cost = 1

            if weight is True:
                cost = list(network.edges[u, v])[0].attributes['weight']
            elif weight is not False and weight is not None:
                cost = list(network.edges[u, v])[0].attributes[weight]

            new_dist = dist[u] + cost

            if new_dist < dist[v.uid]:
                dist[v.uid] = new_dist
                prev[v.uid] = u
                if v.uid in Q:
                    Q[v.uid] = new_dist

    # calculate distance vector
    dist_arr = np.zeros(network.number_of_nodes())
    for v in network.nodes:
        dist_arr[network.nodes.index[v.uid]] = dist[v.uid]

    # construct shortest paths
    s_p: dict = dict()
    for dest in network.nodes:
        if dest.uid != source:
            path = [dest.uid]
            x = dest.uid
            while x is not source and x is not None:
                x = prev[x]
                path.append(x)
            if x is None:
                s_p[dest.uid] = None
            else:
                path.reverse()
                s_p[dest.uid] = tuple(path)
    return dist_arr, s_p


def shortest_path_tree(network: Network,
                       source: str, weight: Union[bool, str, None] = None
                       ) -> Network:
    """Computes a shortest path tree rooted at the node with the
    given source uid."""

    n_tree = net.Network(directed=True)

    Q: dict = dict()
    dist = dict()
    prev = dict()
    dist[source] = 0

    for v in network.nodes.uids:
        if v != source:
            dist[v] = np.inf
            prev[v] = None
        Q[v] = dist[v]

    while Q:
        # TODO: Do this more efficiently with a proper priority queue
        u = min(Q.keys(), key=(lambda k: Q[k]))
        del Q[u]
        for v in network.successors[u]:
            # for networks with no edge costs, edges have constant cost
            cost = 1

            if weight is True:
                cost = list(network.edges[u, v])[0].attributes['weight']
            elif weight is not False and weight is not None:
                cost = list(network.edges[u, v])[0].attributes[weight]

            new_dist = dist[u] + cost

            if new_dist < dist[v.uid]:
                dist[v.uid] = new_dist
                prev[v.uid] = u
                if v.uid in Q:
                    Q[v.uid] = new_dist

    for k, v in prev.items():
        if v is not None:
            n_tree.add_edge(v, k)

    return n_tree


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


def all_longest_paths(network: Network,
                      weight: Union[str, bool, None] = None) -> defaultdict:
    """Returns a dictionary containing all longest shortest paths, i.e. shortest paths
    that correspond to the diameter of the network, between all pairs of nodes

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

    ....


    """
    l_p: defaultdict = defaultdict(lambda: defaultdict(set))
    s_p, dist = all_shortest_paths(network, weight=weight)

    diameter = np.max(dist)

    for v in network.nodes.uids:
        for w in network.nodes.uids:
            if dist[network.nodes.index[v], network.nodes.index[w]] == diameter:
                l_p[v][w] = s_p[v][w]
    return l_p


def avg_path_length(network: Network,
                    weight: Union[str, bool, None] = None,
                    exclude_zero: bool = True) -> float:
    """Calculates the average shortest path length in directed or undirected
    networks, according to the definition

        <l> := \\sum_{i \neq j} D[i,j]/(n (n-1))

    where n is the number of nodes and D is a matrix containing shortest pair
    distances for all node pairs i,j. The above definition holds for the
    default case where paths between node pairs (i,i) are excluded.

    .. note::

        Shortest path lengths are calculated using the implementation
        of the Floyd-Warshall algorithm in scipy.csgraph.

    Parameters
    ----------
    network : Network

        The :py:class:`Network` object that contains the network

    weighted : bool

        If True cheapest paths will be calculated based on the given weight property.

    exclude_zero : bool

        If True, (zero) diagonal entries in the distance matrix will be excluded
        in the average shortest path length calculation.

    Examples
    --------
    Generate a simple network with two edges.
    Shortest path distance matrix in this network is

        [   a x c ]
        [ a 0 1 2 ]
    D = [ x 1 0 1 ]
        [ c 2 1 0 ]

    yielding an average shortest path length of 8/6 = 1.33

    >>> import pathpy as pp
    >>> net = pp.Network(directed=False)
    >>> net.add_edge('a', 'x')
    >>> net.add_edge('x', 'c')
    >>> pp.algorithms.shortest_paths.avg_path_length(net)
    1.3333
    >>> pp.algorithms.shortest_paths.avg_path_length(net, exclude_zero=False)
    0.8888

    """
    D = distance_matrix(network, weight=weight)

    if exclude_zero:
        D = D[np.nonzero(D)]
    return np.sum(D)/np.size(D)
