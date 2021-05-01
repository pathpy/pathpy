"""Methods to generate regular lattice networks with different dimensions"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : lattice.py -- Module to generate lattice graphs
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Mon 2021-04-27 01:07 ingo>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

from pathpy import logger
from pathpy.core.api import Node
from pathpy.models.api import Network

# create logger
LOG = logger(__name__)


def _multi_dim_range(start, stop, dims) -> Tuple:
    if not dims:
        yield ()
        return
    for outer in _multi_dim_range(start, stop, dims - 1):
        for inner in range(start, stop):
            yield outer + (inner,)


def lattice_network(start: Optional[int]=0, stop: Optional[int]=10, dims: Optional[int]=2) -> Network:
    """
    Generates a n-dimensional lattice network with coordinates in each dimension 
    ranging from start (inclusive) to stop (exclusive)
    """
    network = Network(directed=False)

    for pos in _multi_dim_range(start, stop, dims):
        network.add_node(Node("".join(str(i)+'-' for i in pos).strip('-'), pos=np.array(pos)))
    
    for v in network.nodes:
        for w in network.nodes:
            if np.sum(np.abs(v['pos']-w['pos']))==1 and (v.uid, w.uid) not in network.edges:
                network.add_edge(v, w)
    return network
