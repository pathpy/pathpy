#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : random_graphs.py -- Module to generate random graphs
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Thu 2020-04-02 16:53 juergen>
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

from pathpy import config, logger, tqdm
from pathpy.core.base import BaseNetwork
from pathpy.core.edge import Edge
from pathpy.core.network import Network

# create logger
LOG = logger(__name__)


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
    while edges < m:
        v = np.random.choice(n)
        w = np.random.choice(n)
        if not loops and v == w:
            continue
        e = Edge(str(v), str(w), directed=directed)
        if not multi_edge and e.uid in network.edges:
            continue
        network.add_edge(e)
        edges += 1
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

    for s in tqdm(range(n)):
        if directed:
            x = n
        else:
            x = s+1
        for t in range(x):
            if t == s and not loops:
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
        for j in range(1, s+1):
            e = Edge(str(i), str((i+j) % n), directed=False)
            network.add_edge(e)

    if p == 0:
        # nothing to do here
        return network

    # Rewire each link with probability p
    for e in network.edges:
        if np.random.rand() < p:
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
                if not x is v and not x in network.nodes.successors[v]:
                    new_target = x
            network.add_edge(v, new_target)
    return network


def is_graphic_Erdos_Gallai(degrees):
    """Checks whether the condition by Erdös and Gallai (1967) for 
    a graphic degree sequence is fulfilled.

    Parameters
        ----------
        degrees : list

            List of integer node degrees to be tested.       

        Examples
        --------
        Test non-graphic degree sequence:

        >>> import pathpy as pp
        >>> pp.algorithms.random_graphs.is_graphic_Erdos_Gallai([1,0])
        False

        Test graphic degree sequence:

        >>> import pathpy as pp
        >>> pp.algorithms.random_graphs.is_graphic_Erdos_Gallai([1,1])
        True
    """
    degree_sequence = sorted(degrees, reverse=True)
    S = sum(degree_sequence)
    n = len(degree_sequence)
    if S % 2 != 0:
        return False
    for r in range(1, n):
        M = 0
        S = 0
        for i in range(1, r+1):
            S += degree_sequence[i-1]
        for i in range(r+1, n+1):
            M += min(r, degree_sequence[i-1])
        if S > r * (r-1) + M:
            return False
    return True


def Molloy_Reed(degrees: list, relax: bool = False):
    """Generates a random undirected network with 
    given degree sequence based on the Molloy-Reed algorithm.

    .. note::

        The condition proposed by Erdös and Gallai (1967) is used 
        to test whether the degree sequence is graphic, i.e. whether 
        a network with the given degree sequence exists.

    Parameters
        ----------
        degrees : list

            List of integer node degrees. The number of nodes of the 
            generated network corresponds to len(degrees).

        relax : bool

            If True, we conceptually allow self-loops and multi-edges, 
            but do not add them to the network This implies that the 
            generated network may not have exactly sum(degrees)/2 links, 
            but it ensures that the algorithm always finishes.

        Examples
        --------
        Generate random undirected network with given degree sequence

        >>> import pathpy as pp
        >>> random_network = pp.algorithms.random_graphs.Molloy_Reed([1,0])
        >>> print(random_network.summary())
        ...

        Network generation fails for non-graphic sequences

        >>> import pathpy as pp
        >>> random_network = pp.algorithms.random_graphs.Molloy_Reed([1,0])
        >>> print(random_network)
        None
    """
    # assume that we are given a graphical degree sequence
    if not is_graphic_Erdos_Gallai(degrees):
        return

    # create empty network with n nodes
    n = len(degrees)
    network = Network(directed=False)

    # generate link stubs based on degree sequence
    stubs = []
    for i in range(n):
        for k in range(degrees[i]):
            stubs.append(str(i))

    # connect randomly chosen pairs of link stubs
    # note: if relax is True, we conceptually allow self-loops
    # and multi-edges, but do not add them to the network/
    # This implies that the generated network may not have
    # exactly sum(degrees)/2 links, but it ensures that the algorithm
    # always finishes.
    while(len(stubs) > 0):
        v, w = np.random.choice(stubs, 2, replace=False)
        e = Edge(v, w, directed=False)
        if relax or (v != w and (e.uid not in network.edges)):
            # do not add self-loops and multi-edges
            if (v != w and e not in network.edges):
                network.add_edge(e)
            stubs.remove(v)
            stubs.remove(w)
    return network
