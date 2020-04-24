#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : modularity.py -- Methods to calculate modularity of networks
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Thu 2020-04-24 16:44 ingo>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List, Dict, Tuple, Optional
from scipy import sparse
import numpy as np

from pathpy import config, logger, tqdm
from pathpy.core.base.classes import BaseNetwork

def Q_modularity(network: BaseNetwork, cluster_mapping: Dict) -> float:
    """Computes the Q-modularity of a network for a given cluster mapping
    """    
    A = network.adjacency_matrix()
    m = network.number_of_edges()

    q = 0.0
    for v in network.nodes.uids:
        for w in network.nodes.uids:
            if cluster_mapping[v] == cluster_mapping[w]:
                q += A[network.nodes.index[v], network.nodes.index[w]] - network.degrees()[v] * network.degrees()[w]/(2*m)
    return q/(2*m)


def Q_max_modularity(network: BaseNetwork, cluster_mapping: Dict) -> float:
    """Computes the maximum theoretically possible Q-modularity for a given network and cluster mapping
    """
    m = network.number_of_edges()
    qmax = 2*m
    for v in network.nodes.uids:
        for w in network.nodes.uids:
            if cluster_mapping[v] == cluster_mapping[w]:
                qmax -= network.degrees()[v]*network.degrees()[w]/(2*m)
    
    return qmax/(2*m)


def Q_assortativity_coefficient(network: BaseNetwork, cluster_mapping) -> float:
    """Returns the modularity assortative coefficient for a given network and cluster mapping
    """
    return Q_modularity(network, cluster_mapping) / Q_max_modularity(network, cluster_mapping)