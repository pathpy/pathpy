"""Algorithms for component calculations."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : shortest_paths.py -- Module to calculate connected components
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Mon 2021-05-10 16:26 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Dict
from collections import defaultdict

from pathpy import logger, tqdm

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.models.api import Network

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

    if network.number_of_nodes() == 0 or network.number_of_edges() == 0:
        return dict()

    # these are used as nonlocal variables in tarjan
    index: int = 0
    S: list = []
    indices: defaultdict = defaultdict(lambda: None)
    low_link: defaultdict = defaultdict(lambda: None)
    on_stack: defaultdict = defaultdict(lambda: False)
    components: dict = {}

    def tarjan(v: str):
        """Tarjan's algorithm"""
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

        for node in network.successors[v]:
            w = node
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
    for v in tqdm(network.nodes.keys(), desc='component calculation'):
        if indices[v] is None:
            tarjan(v)

    LOG.debug('Mapping component sizes')
    return dict(zip(range(len(components)), components.values()))


def mean_component_size(network: Network) -> float:
    """Returns the mean connected component size of the network.
    """
    components = find_connected_components(network)
    component_sizes = [len(nodes) for comp, nodes in components.items()]
    return np.mean(component_sizes)


def largest_connected_component(network: Network) -> Network:
    """Returns the largest connected component of the network.
    """

    LOG.debug('Computing connected components')
    components = find_connected_components(network)
    max_size = 0
    max_comp: dict = {}
    for i in components:
        if len(components[i]) > max_size:
            max_size = len(components[i])
            max_comp = components[i]

    LOG.debug('Copying network')
    lcc = network.copy()

    LOG.debug('Removing nodes outside largest component')
    for v in list(lcc.nodes.keys()):
        if v not in max_comp:
            lcc.remove_node(v)
    return lcc


@property
def is_connected(network: Network) -> bool:
    """Returns whether the network is (strongly) connected
    """
    return largest_component_size(network) == network.number_of_nodes()


def largest_component_size(network: Network) -> int:
    """Largest component size of the network."""
    LOG.debug('Computing connected components')
    components = find_connected_components(network)
    if len(components):
        return max(map(len, components.values()))
    else:
        return 0
