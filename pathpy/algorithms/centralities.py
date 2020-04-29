"""Algorithms for centrality calculations."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : centralities.py -- Module to calculate node centrality measures
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Sun 2020-04-19 09:21 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List, Tuple
from collections import defaultdict
import operator
import numpy as np

from pathpy import logger
from pathpy.algorithms import shortest_paths

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.core.network import Network

# create logger
LOG = logger(__name__)


def betweenness_centrality(network: Network, normalized: bool = False) -> Dict:
    """Calculates the betweenness centrality of all nodes.
    .. note::

        If `normalized=False` (default) for each node v the betweenness
        centrality is given as $N_{st}[v]/N_{st}$, where $N_{st}[v]$ is the
        number of shortest paths between nodes s and t passing through v and
        $N_{st}$ is the number of all shortest paths from s to t. Shortest paths
        are calculated using the function `shortest_paths.all_shortest_paths`.

    Parameters
    ----------
    network : Network

        The :py:class:`Network` object that contains the network

    normalized : bool

        If True the resulting centralities will be normalized such that the
        minimum centrality is zero and the maximum centrality is one.

    Examples
    --------
    Compute betweenness centrality in a simple network

    >>> import pathpy as pp
    >>> net = pp.Network(directed=False)
    >>> net.add_edge('a', 'x')
    >>> net.add_edge('x', 'b')
    >>> c = pp.algorithms.centralities.betweenness_centrality(net)
    >>> c['x']
    2.0

    """
    all_paths = shortest_paths.all_shortest_paths(network, weight=False, return_distance_matrix=False)
    bw: defaultdict = defaultdict(float)

    for s in all_paths:
        for t in all_paths[s]:
            for p in all_paths[s][t]:
                for x in p[1:-1]:
                    if s != t != x:
                        bw[x] += 1.0 / len(all_paths[s][t])

    if normalized:
        max_centr = max(bw.values())
        min_centr = min(bw.values())
        for v in bw:
            bw[v] = (bw[v] - min_centr) / (max_centr - min_centr)

    # assign zero values to nodes not occurring on shortest paths
    for v in network.nodes.uids:
        bw[v] += 0

    return bw


def closeness_centrality(network: Network, normalized: bool = False) -> Dict:
    """Calculates the closeness centrality of all nodes.

    .. note::

        If `normalized=False` (Default) for each node v the closeness centrality
        is given as 1/sum_w(dist(v,w)) where dist(v,w) is the shortest path
        distance between v and w. For `normalized=True` the counter is
        multiplied by n-1 where n is the number of nodes in the
        network. Shortest path distances are calculated using the function
        `shortest_paths.distance_matrix`.

    Parameters
    ----------
    network : Network

        The :py:class:`Network` object that contains the network

    normalized : bool

        If True the resulting centralities will be normalized based on the
        average shortest path length.

    Examples
    --------
    Compute closeness centrality in a simple network

    >>> import pathpy as pp
    >>> net = pp.Network(directed=False)
    >>> net.add_edge('a', 'x')
    >>> net.add_edge('x', 'b')
    >>> c = pp.algorithms.centralities.closeness_centrality(net)
    >>> c['a']
    0.3333333333333333

    """
    distances = shortest_paths.distance_matrix(network)
    cl: defaultdict = defaultdict(float)

    mapping = {v: k for k, v in network.nodes.index.items()}

    n = network.number_of_nodes()
    # calculate closeness values
    for d in range(n):
        for x in range(n):
            if d != x and distances[d, x] < np.inf:
                cl[mapping[x]] += distances[d, x]

    # assign centrality zero to nodes not occurring
    # on higher-order shortest paths
    for v in network.nodes.uids:
        cl[v] += 0.0
        if cl[v] > 0.0:
            cl[v] = 1.0 / cl[v]
        if normalized:
            cl[v] *= n-1

    return cl


def degree_centrality(network: Network, mode: str = 'degree') -> dict:
    """Calculates the degree centrality of all nodes.

    Parameters
    ----------
    network : Network

        The :py:class:`Network` object that contains the network

    mode : str

        Can be chose nas 'degree', 'indegree', or 'outdegree'. Determines
        whether to calculate undirected/total degrees, indegrees, or degrees

    Examples
    --------
    Compute degree centrality in a simple network

    >>> import pathpy as pp
    >>> net = pp.Network(directed=True)
    >>> net.add_edge('a', 'x')
    >>> net.add_edge('x', 'b')
    >>> c = pp.algorithms.centralities.degree_centrality(net)
    >>> c['a']
    1

    >>> c = pp.algorithms.centralities.degree_centrality(net, mode='indegree')
    >>> c['a']
    0

    """
    d: dict = dict()
    if mode not in set(['degree', 'indegree', 'outdegree']):
        LOG.error('Mode must be \'degree\', \'indegree\' or \'outdegree\'')
        raise KeyError

    for v in network.nodes.keys():
        if mode == 'indegree':
            d[v] = network.indegrees()[v]
        elif mode == 'outdegree':
            d[v] = network.outdegrees()[v]
        else:
            d[v] = network.degrees()[v]

    return d


def rank_centralities(centralities: Dict[str, float]) -> List[Tuple[str, float]]:
    """Returns a list of (node, centrality) tuples in which tuples are ordered
    by centrality in descending order

    Parameters
    ----------
    centralities: dict

        dictionary of centralities, e.g. generated by `closeness_centralities`,
        `betweenness_centralities`, or `degree_centralities`.

    Examples
    --------
    >>> import pathpy as pp
    >>> centralities = {'a': .2, 'b': .8, 'c': .5}
    >>> pp.algorithms.centralities.rank_centralities(centralities)
    [('b', 0.8), ('c', 0.5), ('a', 0.2)]

    Returns
    -------
    list
        list of (node,centrality) tuples

    """
    ranked_nodes = sorted(centralities.items(), key=operator.itemgetter(1))
    ranked_nodes.reverse()
    return ranked_nodes
