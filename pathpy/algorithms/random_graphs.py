#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : random_graphs.py -- Module to generate random graphs
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Wed 2020-03-25 14:54 scholtes>
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
from scipy.sparse import csgraph
import numpy as np


from .. import config, logger, tqdm
from ..core.base import BaseNetwork
from ..core import Network, Edge
from . import shortest_paths

# create logger
log = logger(__name__)

def ER_nm(n: int, m: int, directed: bool = False, loops: bool = False, multi_edge: bool = False) -> Network:
    """Generates a random graph with a fixed number of n nodes 
    and m edges based on the Erdös-Renyi model.

    Parameters
        ----------
        n : int

            The number of nodes in the generated network

        m : int

            The number of randomly generated edges in the network

        directed : bool

            Whether a directed network should be generated

        loops : bool

            Whether or not the generated network may contain 
            loops.

        multi_edge : bool

            Whether or not the same edge can be added multiple times

        Examples
        --------
        Generate random undirected network with 10 nodes and 25 edges

        >>> import pathpy as pp
        >>> random_graph = pp.algorithms.random_graphs.ER_nm(n=10, m=25)
        >>> print(random_graph.summary())
        ...
    """
    network = Network(directed=directed)

    for i in range(n):
        network.add_node(str(i))

    edges = 0
    while edges<m:
        v = np.random.choice(n)
        w = np.random.choice(n)
        if not loops and v==w:
            continue
        e = Edge(str(v), str(w), directed=directed)
        if not multi_edge and e.uid in network.edges:
            continue
        network.add_edge(e)
        edges +=1
    return network


def ER_np(n: int, p: float, directed: bool = False, loops: bool = False) -> Network:
    """Generates a random graph with a fixed number of n nodes and edge 
    probability p based on the Erdös-Renyi model.

    Parameters
        ----------
        n : int

            The number of nodes in the generated network

        p : float

            The probability with which an edge will be created 
            between each pair of nodes

        directed : bool

            Whether a directed network should be generated

        loops : bool

            Whether or not the generated network may contain 
            loops.

        Examples
        --------
        Generate random undirected network with 10 nodes

        >>> import pathpy as pp
        >>> random_graph = pp.algorithms.random_graphs.ER_np(n=10, p=0.03)
        >>> print(random_graph.summary())
        ...
    """
    network = Network(directed=directed)

    for i in range(n):
        network.add_node(str(i))

    for s in range(n):
        if directed:
            x = n
        else:
            x = s+1
        for t in range(x):
            if t==s and not loops:
                continue
            if np.random.random() < p:
                e = Edge(str(s), str(t), directed=directed)
                network.add_edge(e)
    return network

def Watts_Strogatz(n: int, s: int, p: int) -> Network:
    """Generates an undirected Watts-Strogatz lattice 
    network with lattice dimensionality one.

    Parameters
        ----------
        n : int

            The number of nodes in the generated network

        s : float

            The number of nearest neighbors that will be connected
            in the ring lattice

        p : float

            The rewiring probability

        Examples
        --------
        Generate a Watts-Strogatz network with 100 nodes

        >>> import pathpy as pp
        >>> small_world = pp.algorithms.random_graphs.Watts_Strogatz(n=100, s=2, p=0.1)
        >>> print(small_world.summary())
        ...
    """
    network = Network(directed=False)
    for i in range(n):
        network.add_node(str(i))
    
    # construct a ring lattice (dimension 1)
    for i in range(n):
        for j in range(1,s+1):
            e = Edge(str(i),str((i+j)%n), directed=False)
            network.add_edge(e)

    if p==0:
        # nothing to do here
        return network
    
    # Rewire each link with probability p
    for e in network.edges:
        if np.random.rand()<p:
            # Delete original link and remember source node
            v = network.edges[e].v.uid
            network.remove_edge(e)

            # Find new random tgt, which is not yet connected to src
            new_target = None
            
            # This loop repeatedly chooses a random target until we find 
            # a target not yet connected to src. Note that this could potentially
            # result in an infinite loop depending on parameters.
            while new_target == None:
                x = str(np.random.randint(n))
                if not x is v and not x in network.successors(v):
                    new_target = x
            network.add_edge(v, new_target)
    return network
