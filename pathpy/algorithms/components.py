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

# create logger
log = logger(__name__)

# TODO: replace this by a function that returns a new network
def reduce_to_gcc(network) -> None:
    """Reduces the network to the largest connected component.
    """

    # these are used as nonlocal variables (!)
    index = 0
    S = []
    indices = defaultdict(lambda: None)
    low_link = defaultdict(lambda: None)
    on_stack = defaultdict(lambda: False)
    components = {}

    # Tarjan's algorithm
    def strong_connect(v):
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

        for w in network.successors(v):
            if indices[w] is None:
                strong_connect(w)
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
            strong_connect(v)
            # print('node {v}, size = {n}, component = {component}'.format(v=v, component=components[v], n = len(components[v]) ))

    max_size = 0
    for v in components:
        if len(components[v]) > max_size:            
            scc = components[v]
            max_size = len(components[v])

    # Reduce network to SCC
    for v in list(network.nodes):
        if v not in scc:
            network.remove_node(v)
