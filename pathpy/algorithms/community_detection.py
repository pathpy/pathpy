"""Methods to find community structures in networks."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : community_detection.py -- Methods to find community structures
#                                       in networks
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Tue 2020-04-28 09:53 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Tuple
import numpy as np

from pathpy import logger, tqdm

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.core.network import Network

# create logger for the Plot class
LOG = logger(__name__)


def _Q_merge(network: Network, cluster_mapping: Dict, merge=set()) -> float:
    """Helper function to mearge."""
    m = network.number_of_edges()
    A = network.adjacency_matrix(weighted=False)

    q = 0.0
    for v in network.nodes.uids:
        for w in network.nodes.uids:
            if (cluster_mapping[v] == cluster_mapping[w] or
                    (cluster_mapping[v] in merge and
                     cluster_mapping[w] in merge)):
                q += A[network.nodes.index[v], network.nodes.index[w]] - \
                    network.degrees()[v]*network.degrees()[w]/(2*m)
    q /= 2*m
    return q


def color_map(network: Network, cluster_mapping: Dict) -> Dict:
    """Returns a dictionary that maps nodes to colors based on their communities.

    Currently, a maximum of 20 different communities is supported.
    """
    colors = ['red', 'green', 'blue', 'orange', 'yellow', 'cyan', 'blueviolet',
              'chocolate', 'magenta', 'navy', 'plum', 'thistle', 'wheat',
              'turquoise', 'steelblue', 'grey', 'powderblue', 'orchid',
              'mintcream', 'maroon']
    node_colors = {}
    community_color_map: Dict = {}
    i = 0
    for v in network.nodes.uids:
        if cluster_mapping[v] not in community_color_map:
            community_color_map[cluster_mapping[v]] = i % len(colors)
            i += 1
            if i > 20:
                LOG.warning('Exceeded 20 different communities, '
                            'some communities are assigned the same color.')
        node_colors[v] = colors[community_color_map[cluster_mapping[v]]]
    return node_colors


def modularity_maximisation(network: Network,
                            iterations: int = 1000) -> Tuple[Dict, float]:
    """Modularity maximisation."""
    # start with each node being in a separate cluster
    cluster_mapping = {}
    community_to_nodes = {}

    c = 0
    for n in network.nodes.uids:
        cluster_mapping[n] = c
        community_to_nodes[c] = set([n])
        c += 1
    q = _Q_merge(network, cluster_mapping)
    communities = list(cluster_mapping.values())

    for i in tqdm(range(iterations), desc='maximising modularity'):

        # randomly choose two communities
        x, y = np.random.choice(communities, size=2)

        # check Q of merged communities
        q_new = _Q_merge(network, cluster_mapping, merge=set([x, y]))
        if q_new > q:
            # merge the communities
            for n in community_to_nodes[x]:
                cluster_mapping[n] = y
            community_to_nodes[y] = community_to_nodes[y] | community_to_nodes[x]
            q = q_new
            communities.remove(x)
            del community_to_nodes[x]
    return cluster_mapping, q
