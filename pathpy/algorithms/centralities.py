"""Algorithms for centrality calculations."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : centralities.py -- Module to calculate node centrality measures
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Mon 2021-03-29 17:15 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List, Tuple, Union, Any
from functools import singledispatch
from collections import defaultdict

import operator
import numpy as np
from scipy.sparse import linalg as spl

from pathpy import logger
from pathpy.algorithms import shortest_paths
from pathpy.algorithms.matrices import adjacency_matrix

from pathpy.core.collecions import BaseCollection
from pathpy.models.classes import BaseModel
from pathpy.models.models import ABCHigherOrderNetwork


# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.core.path import PathCollection
    from pathpy.core.network import Network
    from pathpy.models.higher_order_network import HigherOrderNetwork

# create logger
LOG = logger(__name__)


@singledispatch
def betweenness_centrality(self, normalized: bool = False) -> Dict:
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

    raise NotImplementedError


@betweenness_centrality.register(BaseCollection)
def _bw_paths(self: PathCollection, normalized: bool = False) -> Dict:
    """Betweenness Centrality for Paths."""

    # TODO: Move sp calculation to shortest_paths
    from pathpy.statistics.subpaths import SubPathCollection

    s_p: defaultdict = defaultdict(lambda: defaultdict(set))
    s_p_lengths: defaultdict = defaultdict(lambda: defaultdict(lambda: np.inf))

    bw: defaultdict = defaultdict(float)

    paths = SubPathCollection(self)

    for path in paths(include_path=True):
        s = path.start
        d = path.end
        if len(path) < s_p_lengths[s][d]:
            s_p_lengths[s][d] = len(path)
            s_p[s][d] = set()
            s_p[s][d].add(tuple(path.nodes))
        elif len(path) == s_p_lengths[s][d]:
            s_p[s][d].add(tuple(path.nodes))

    for s in s_p:
        for d in s_p[s]:
            for p in s_p[s][d]:
                for x in p[1:-1]:
                    if s != d != x:
                        bw[x.uid] += 1.0 / len(s_p[s][d])

    # assign zero values to nodes not occurring on shortest paths
    for v in self.nodes.uids:
        bw[v] += 0

    if normalized:
        max_centr = max(bw.values())
        min_centr = min(bw.values())
        for v in bw:
            bw[v] = (bw[v] - min_centr) / (max_centr - min_centr)

    return bw


@betweenness_centrality.register(BaseModel)
def _bw_network(self: Network, normalized: bool = False) -> Dict:
    """Betweenness Centrality for Networks."""

    all_paths = shortest_paths.all_shortest_paths(
        self, weight=False, return_distance_matrix=False)

    bw: defaultdict = defaultdict(float)

    for s in all_paths:
        for t in all_paths[s]:
            for p in all_paths[s][t]:
                for x in p[1:-1]:
                    if s != t != x:
                        bw[x] += 1.0 / len(all_paths[s][t])

    # assign zero values to nodes not occurring on shortest paths
    for v in self.nodes.uids:
        bw[v] += 0

    if normalized:
        max_centr = max(bw.values())
        min_centr = min(bw.values())
        for v in bw:
            bw[v] = (bw[v] - min_centr) / (max_centr - min_centr)

    return bw


@betweenness_centrality.register(ABCHigherOrderNetwork)
def _bw_hon(self: HigherOrderNetwork, normalized: bool = False) -> Dict:
    """Betweenness Centrality for Networks."""

    from pathpy.core.edge import Edge
    from pathpy.core.path import Path

    LOG.debug('Calculating betweenness (order k = %s) ...', self.order)

    all_paths = shortest_paths.all_shortest_paths(
        self, weight=False, return_distance_matrix=False)

    bw: defaultdict = defaultdict(float)

    lengths: defaultdict = defaultdict(
        lambda: defaultdict(lambda: float('inf')))
    paths: defaultdict = defaultdict(lambda: defaultdict(set))

    for path_1_order_k in all_paths:
        for path_2_order_k in all_paths:
            for path_order_k in all_paths[path_1_order_k][path_2_order_k]:
                nodes = []
                for node in path_order_k:
                    nodes.append(self.nodes[node].nodes)

                path = nodes[0]
                for node in nodes[1:]:
                    path.append(node[-1])

                edges = []
                for _v, _w in zip(path[:-1], path[1:]):
                    edges.append(Edge(_v, _w))

                if edges:
                    path = Path(*edges)
                    s1 = path.start
                    t1 = path.end

                    if len(path) < lengths[s1][t1]:
                        lengths[s1][t1] = len(path)
                        paths[s1][t1] = set()
                        paths[s1][t1].add(path)
                    elif len(path) == lengths[s1][t1]:
                        paths[s1][t1].add(path)

    for s_order_1 in paths:
        for t_order_1 in paths[s_order_1]:
            for path_order_1 in paths[s_order_1][t_order_1]:
                for node in path_order_1.nodes[1:-1]:
                    if s_order_1 != node != t_order_1:
                        bw[node.uid] += 1.0 / len(paths[s_order_1][t_order_1])

    # assign zero values to nodes not occurring on shortest paths
    for v in self.nodes.nodes.keys():
        bw[v] += 0

    if normalized:
        max_centr = max(bw.values())
        min_centr = min(bw.values())
        for v in bw:
            bw[v] = (bw[v] - min_centr) / (max_centr - min_centr)

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


def eigenvector_centrality(network: Network,
                           weight: Union[str, bool, None] = None,
                           **kwargs: Any) -> dict:
    """Calculates the eigenvector centrality of all nodes.

    Parameters
    ----------
    network : Network

        The :py:class:`Network` object that contains the network

    Examples
    --------
    Compute eigenvector centrality in a simple network

    >>> import pathpy as pp
    >>> net = pp.Network(directed=True)
    >>> net.add_edge('a', 'x')
    >>> net.add_edge('x', 'b')
    >>> c = pp.algorithms.centralities.eigenvector_centrality(net)
    >>> c['a']
    1
    """
    evcent: dict = dict()

    A = adjacency_matrix(network, weight=weight).transpose()
    if kwargs:
        _, ev = spl.eigs(A, k=1, which='LM', **kwargs)
    else:
        _, ev = spl.eigs(A, k=1, which='LM')
    ev = ev.reshape(ev.size, )
    S = np.sum(ev)
    for v in network.nodes:
        evcent[v.uid] = np.real(ev[network.nodes.index[v.uid]]/S)
    return evcent


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
