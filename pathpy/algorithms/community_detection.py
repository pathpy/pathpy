"""Algorithms to find community structures in networks."""
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
from typing import TYPE_CHECKING, Dict, Tuple, Set
import numpy as np
import random

from pathpy import logger, tqdm

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.models.api import Network

# create logger for the Plot class
LOG = logger(__name__)


def _Q_merge(network: Network, A, D, n: int, m: int, C: Dict, merge: Set = set()) -> float:
    """Helper function to compute modularity with merged partitions."""
    
    q = 0.0
    for v in network.nodes.uids:
        for w in network.nodes.uids:
            if C[v] == C[w] or (C[v] in merge and C[w] in merge):
                q += A[network.nodes.index[v], network.nodes.index[w]] - D[v]*D[w]/(2*m)
    q /= 2*m
    return q


def modularity_maximisation(network: Network,
                            iterations: int = 1000) -> Tuple[Dict, float]:
    """Modularity maximisation."""

    A = network.adjacency_matrix(weighted=False)    
    D = network.degrees()
    n = network.number_of_nodes()
    m = network.number_of_edges()

    C = {}
    num_communities = n
    community_to_nodes = {}
    c = 0
    for v in network.nodes.uids:
        C[v] = c
        community_to_nodes[c] = set([v])
        c += 1
    q = _Q_merge(network, A, D, n, m, C)
    
    for i in tqdm(range(iterations), desc='maximising modularity'):

        # randomly choose two communities
        x, y = random.sample(community_to_nodes.keys(), 2)

        # check Q of merged communities
        q_new = _Q_merge(network, A, D, n, m, C, merge=set([x, y]))

        if q_new > q:
            # merge communities
            for v in community_to_nodes[x]:
                C[v] = y
            community_to_nodes[y] = community_to_nodes[y].union(community_to_nodes[x])
            q = q_new
            num_communities -=1
            del community_to_nodes[x]
        
    return C, q
