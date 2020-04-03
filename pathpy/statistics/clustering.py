#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : clustering.py -- Module to calculate clustering statistics
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Fri 2020-04-03 10:44 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List, Dict, Tuple, Optional, Set
from functools import singledispatch
from collections import Counter
import datetime
import sys
import numpy as np

from pathpy import config, logger, tqdm


def local_clustering_coefficient(network, v: str) -> float:
    """Calculates the local clustering coefficient of a node in a network.


    The local clustering coefficient of any node with an (out-)degree smaller than two is defined
    as zero. For all other nodes, it is defined as:

        cc(c) := 2*k(i)/(d_i(d_i-1))

        or

        cc(c) := k(i)/(d_out_i(d_out_i-1))

        in undirected and directed networks respectively.

    Parameters
    ----------
    network : Network

        The network in which to calculate the local clustering coefficient

    node : str

        The node for which the local clustering coefficient shall be calculated
    """

    if network.directed and network.nodes.degrees()[v] < 2:
        return 0.
    if not network.directed and network.nodes.degrees()[v] < 2:
        return 0.
    k = 0
    for e in network.edges:
        edge = network.edges[e]
        if edge.v.uid in network.successors[v] and edge.w.uid in network.successors[v]:
            k += 1
    if network.directed:
        return k/(network.nodes.outdegrees()[v]*(network.nodes.outdegrees()[v]-1))
    else:
        return 2*k/(network.nodes.degrees()[v]*(network.nodes.degrees()[v]-1))


def avg_clustering_coefficient(network) -> float:
    """Calculates the average (global) clustering coefficient of a directed or undirected network.

    Parameters
    ----------

    network : Network

        The network in which to calculate the local clustering coefficient.

    """
    return np.mean([local_clustering_coefficient(network, v) for v in network.nodes])


def closed_triads(network, v: str) -> Set:
    """Calculates the set of edges that represent a closed triad around a given node v.

    Parameters
    ----------

    network : Network

        The network in which to calculate the list of closed triads

    """
    closed_triads = set()
    for e in network.edges:
        edge = network.edges[e]
        if edge.v.uid in network.successors[v] and edge.w.uid in network.successors[v]:
            closed_triads.add(edge)
    return closed_triads
