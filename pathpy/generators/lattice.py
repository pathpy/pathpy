"""Methods to generate regular lattice networks with different dimensions"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : lattice.py -- Module to generate lattice graphs
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Mon 2021-03-29 17:07 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from functools import singledispatch

from typing import Optional, Union, Dict

import numpy as np

from pathpy import logger, tqdm

from pathpy.core.edge import Edge
from pathpy.core.node import Node
from pathpy.models.network import Network

# create logger
LOG = logger(__name__)


def _multi_dim_range(start, stop, dims):
    if not dims:
        yield ()
        return
    for outer in _multi_dim_range(start, stop, dims - 1):
        for inner in range(start, stop):
            yield outer + (inner,)


def lattice_network(start: int=0, stop: int=10, dims: int=2):
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
