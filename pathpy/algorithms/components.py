#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : shortest_paths.py -- Module to calculate connected components
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Thu 2020-04-02 17:49 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Dict
from collections import defaultdict

from pathpy import logger, tqdm

from pathpy.core.network import Network

LOG = logger(__name__)


def find_connected_components(network: Network) -> Dict:
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
    def tarjan(v: str):
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
    LOG.debug('Computing connected components')
    for v in tqdm(network.nodes, desc='component calculation'):
        if indices[v] is None:
            tarjan(v)

    LOG.debug('Mapping component sizes')
    return dict(zip(range(len(components)), components.values()))


def largest_connected_component(network: Network) -> Network:
    """Returns the largest connected component of the network as a new 
    network
    """

    LOG.debug('Computing connected components')
    components = find_connected_components(network)
    max_size = 0
    max_comp = None
    for i in components:
        if len(components[i]) > max_size:
            max_size = len(components[i])
            max_comp = components[i]

    LOG.debug('Copying network')
    lcc = network.copy()

    LOG.debug('Removing nodes outside largest component')
    for v in list(lcc.nodes):
        if v not in max_comp:
            lcc.remove_node(v)
    return lcc


def largest_component_size(network: Network) -> int:
    LOG.debug('Computing connected components')
    components = find_connected_components(network)
    return max(map(len, components.values()))
