#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : shortest_paths.py -- Module to calculate connected components
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Wed 2020-03-31 16:40 scholtes>
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
import numpy as np

from .. import config, logger, tqdm
from ..core.base import BaseNetwork
from .. import core

# create logger
log = logger(__name__)

def find_connected_components(network) -> dict:
    """Computes connected components of a network.

    Parameters
    ----------

        network: Network

            Network instance

    Returns
    -------

        dict

            dictionary mapping node uids to components (represented as integer IDs)
    """

    # these are used as nonlocal variables in tarjan
    index = 0
    S = []
    indices = defaultdict(lambda: None)
    low_link = defaultdict(lambda: None)
    on_stack = defaultdict(lambda: False)
    components = {}

    # Tarjan's algorithm
    def tarjan(v):
        nonlocal index
        nonlocal S
        nonlocal indices
        nonlocal low_link
        nonlocal on_stack
        nonlocal components

        indices[v] = index
        low_link[v] = index
        index += 1
        S.append(v)
        on_stack[v] = True

        for w in network.successors[v]:
            if indices[w] is None:
                tarjan(w)
                low_link[v] = min(low_link[v], low_link[w])
            elif on_stack[w]:
                low_link[v] = min(low_link[v], indices[w])

        # create component of node v
        if low_link[v] == indices[v]:
            components[v] = set()
            while True:
                w = S.pop()
                on_stack[w] = False
                components[v].add(w)
                if v == w:
                    break

    # compute strongly connected components
    for v in network.nodes:
        if indices[v] is None:
            tarjan(v)

    return dict(zip(range(len(components)), components.values()))


def largest_connected_component(network: core.Network) -> core.Network:
    """Returns the largest connected component of the network as a new 
    network
    """

    components = find_connected_components(network)
    max_size = 0
    max_comp = None
    for i in components:
        if len(components[i]) > max_size:
            max_size = len(components[i])
            max_comp = components[i]

    lcc = core.Network(directed = network.directed)
    for v in max_comp:
        lcc.add_node(network.nodes[v])
    for e in network.edges:
        edge = network.edges[e]
        if edge.v.uid in max_comp and edge.v.uid in max_comp:
            lcc.add_edge(edge)
    return lcc
