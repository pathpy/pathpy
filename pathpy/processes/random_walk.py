#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : randomwalk.py -- Class to simulate random walks
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Thu 2020-04-07 11:38 ingo>
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
import scipy as sp

from pathpy import config, logger, tqdm, adjacency_matrix
from pathpy.core.base import BaseNetwork
from pathpy.core.edge import Edge
from pathpy.core.network import Network

# create logger
LOG = logger(__name__)

class RandomWalk:

    def __init__(self, network: Network, weight: bool=False, start_node: str = None):
        """Initialises a random walk process in a given start node. The initial time t of 
        the random walk will be set to zero and the initial state is set to the given start 
        node. If start_node is omitted a node will be chosen uniformly at random.
        """
        self._network = network
        self._t = 0
        self._transition_matrix = RandomWalk.transition_matrix(network, weight)
        self._node_uids = [v for v in network.nodes]
        self._visitations = np.ravel(np.zeros(shape=(1, network.number_of_nodes())))

        if start_node == None:
            self._current_node = np.random.choice(self._node_uids)
        elif start_node not in network.nodes:
            LOG.warning('Invalid start node for random walk. Picking random node.')
            self._current_node = np.random.choice(self._node_uids)
        else:
            self._current_node = start_node

    def stationary_probabilities(self) -> np.array:
        """Computes stationary visitation probabilities of nodes
        """
        eigenvalues, eigenvectors = sp.sparse.linalg.eigs(self._transition_matrix.transpose(), k=1, which='LM')

        pi = eigenvectors.reshape(eigenvectors.size, )
        return np.real(pi/np.sum(pi))

    def visitation_probabilities(self) -> np.array:
        """Returns the visitation probabilities of nodes based on the current history of 
        the random walk.
        """
        return np.nan_to_num(self._visitations/self._t)

    def transition_probabilities(self, node: str) -> np.array:
        """Returns a vector that contains the transition probabilities from a given node 
        to all other nodes in the network.
        """
        return np.nan_to_num(np.ravel(self._transition_matrix[self._network.nodes.index[node],:].todense()))

    @staticmethod
    def transition_matrix(network: Network, weight: bool = False) -> sp.sparse.csr_matrix:
        A = adjacency_matrix(network, weight=weight)
        D = A.sum(axis=1)
        T = sp.sparse.csr_matrix((network.number_of_nodes(), network.number_of_nodes()))
        for i in range(network.number_of_nodes()):
            T[i,:] = A[i,:]/D[i]
        return T

    @property
    def t(self):
        return self._t

    @property
    def state(self):
        return self._current_node

    def walk(self, steps: int=1) -> str:
        """Generator function that generates a given number of random walk steps 
        starting from the current state of the random walk. 

        Parameters
        ----------

            steps: int
                The number of random walk steps to simulate

        Example
        -------
            >>> n = pp.Network('a-b-c-a-c-b')
            >>> rw = pp.processes.RandomWalk(n, start_node='a')
            >>> for v in rw.walk(10):
            >>>     print('Node visited at time {} is {}'.format(rw.t, rw.state))
            Node visited at time 1 is b
            Node visited at time 2 is c
            Node visited at time 3 is a
            Node visited at time 4 is c
            Node visited at time 5 is b
            Node visited at time 6 is c
            Node visited at time 7 is a
            Node visited at time 8 is c
            Node visited at time 9 is a
            Node visited at time 10 is b

            >>> pp.visitation_probabilities()
            array([0.3, 0.3, 0.4])
        """
        if self._current_node == None:
            return None
        for t in range(steps):
            prob = self.transition_probabilities(self._current_node)
            if prob.sum() == 0:
                self._current_node = None
                return None
            i = np.random.choice(a=self._network.number_of_nodes(), p=prob)
            self._current_node = self._node_uids[i]
            self._visitations[i] += 1
            self._t += 1
            yield self._current_node

    def transition(self) -> str: 
        return next(self.walk())
    