#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : centralities.py -- Module to calculate node centrality measures
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Thu 2020-04-02 16:35 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Dict, Union
from functools import singledispatch
from collections import Counter
from collections import defaultdict
import datetime
import sys
import numpy as np


from pathpy import config, logger, tqdm
from pathpy.core.network import Network
from pathpy.algorithms import shortest_paths

# create logger
log = logger(__name__)


def betweenness_centrality(network: Network, normalized: bool = False) -> Counter:
    """Calculates the betweenness centrality of all nodes.
    .. note::

        If `normalized=False` (default) for each node v the betweenness
        centrality is given as $N_{st}[v]/N_{st}$, where $N_{st}[v]$ is the 
        number of shortest paths between nodes s and t passing through v and 
        $N_{st}$ is the number of all shortest paths from s to t. Shortest 
        paths are calculated using the function `shortest_paths.all_shortest_paths`.

    Parameters
        ----------
        network : Network

            The :py:class:`Network` object that contains the network

        normalized : bool

            If True the resulting centralities will be normalized such 
            that the minimum centrality is zero and the maximum centrality
            is one.

        Examples
        --------
        Compute betweenness centrality in a simple network

        >>> import pathpy as pp
        >>> net = pp.Network(directed=False)
        >>> net.add_edge('a', 'x')
        >>> net.add_edge('x', 'b')        
        >>> c = pp.algorithms.centralities.betweenness_centrality(net)
        >>> c['x']
        1.0
    """
    all_paths = shortest_paths.all_shortest_paths(network, weighted=False)
    bw = Counter()

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
    for v in network.nodes:
        bw[v] += 0

    return bw


def closeness_centrality(network: Network, normalized: bool = False) -> Counter:
    """Calculates the closeness centrality of all nodes.

    .. note::

        If `normalized=False` (Default) for each node v the closess 
        centrality is given as  $\frac{1}{\sum_w(dist(v,w))}$ where 
        dist(v,w) is the shortest path distance between v and w. For 
        `normalized=True` the counter is multiplied by n-1 where n
        is the number of nodes in the network. Shortest path 
        distances are calculated using the function `shortest_paths.distance_matrix`.

    Parameters
        ----------
        network : Network

            The :py:class:`Network` object that contains the network

        normalized : bool

            If True the resulting centralities will be normalized based
            on the average shortest path length.

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
    cl = Counter()

    mapping = {idx: v for idx, v in enumerate(network.nodes)}

    n = network.number_of_nodes()
    # calculate closeness values
    for d in range(n):
        for x in range(n):
            if d != x and distances[d, x] < np.inf:
                cl[mapping[x]] += distances[d, x]

    # assign centrality zero to nodes not occurring on higher-order shortest paths
    for v in network.nodes:
        cl[v] += 0.0
        if cl[v] > 0.0:
            cl[v] = 1.0 / cl[v]
        if normalized:
            cl[v] *= n-1

    return cl

def degree_centrality(network: Network, mode: str='degree') -> Union[Dict, None]:
    """Calculates the degree centrality of all nodes.

    Parameters
        ----------
        network : Network

            The :py:class:`Network` object that contains the network

        normalized : bool

            If True the resulting centralities will be normalized based
            on the average shortest path length.

        Examples
        --------
        Compute closeness centrality in a simple network

        >>> import pathpy as pp
        >>> net = pp.Network(directed=True)
        >>> net.add_edge('a', 'x')
        >>> net.add_edge('x', 'b')        
        >>> c = pp.algorithms.centralities.degree_centrality(net)
        >>> c['a']
        1.

        >>> c = pp.algorithms.centralities.degree_centrality(net, mode='indegree')
        >>> c['a']
        0.
    """
    d = dict()
    if mode not in set(['degree', 'indegree', 'outdegree']):
        log.error('Mode must be \'degree\', \'indegree\' or \'outdegree\'')
        return None

    for v in network.nodes:
        if mode == 'indegree':
            d[v] = network.nodes.indegrees()[v]
        elif mode == 'outdegree':
            d[v] = network.nodes.outdegrees()[v]
        else:
            d[v] = network.nodes.degrees()[v]

    return d
