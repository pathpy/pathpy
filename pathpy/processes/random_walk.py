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
import abc
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


class BaseWalk:
    """Abstract base class for all implementations of walk processes.
    """
    @abc.abstractmethod
    def walk(self):
        pass

    @abc.abstractproperty
    def t(self):
        pass

    @abc.abstractproperty
    def state(self):
        pass


class RandomWalk(BaseWalk):
    """Instances of this class represent the state of a random walk in a network."""

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

        eigenvalues, eigenvectors = sp.sparse.linalg.eigs(self._transition_matrix.transpose(), k=1, which='LM')
        pi = eigenvectors.reshape(eigenvectors.size, )
        self._stationary_probabilities = np.real(pi/np.sum(pi))

        if start_node == None:
            self._current_node = np.random.choice(self._node_uids)
        elif start_node not in network.nodes:
            LOG.warning('Invalid start node for random walk. Picking random node.')
            self._current_node = np.random.choice(self._node_uids)
        else:
            self._current_node = start_node

    def stationary_probabilities(self, **kwargs: Any) -> np.array:
        """Computes stationary visitation probabilities of nodes based on the leading
        eigenvector of the transition matrix.

        Parameters
        ----------

        **kwargs: Any
            Arbitrary key-value pairs that will be passed to the scipy.sparse.linalg.eigs function.
        """
        if kwargs == {}:
            return self._stationary_probabilities
        else:
            eigenvalues, eigenvectors = sp.sparse.linalg.eigs(self._transition_matrix.transpose(), k=1, which='LM', **kwargs)
            pi = eigenvectors.reshape(eigenvectors.size, )
            return np.real(pi/np.sum(pi))

    def visitation_probabilities(self) -> np.array:
        """Returns the visitation probabilities of nodes based on the history of 
        the random walk. Initially, all visitation probabilities are zero.
        """
        return np.nan_to_num(self._visitations/self._t)

    @property
    def total_variation_distance(self) -> float:
        """Computes the total variation distance between the current 
        visitation probabilies and the stationary probabilities.
        """
        return np.abs(self._stationary_probabilities - self.visitation_probabilities()).sum()/2.0

    def transition_probabilities(self, node: str) -> np.array:
        """Returns a vector that contains transition probabilities from a given node 
        to all other nodes in the network.
        """
        return np.nan_to_num(np.ravel(self._transition_matrix[self._network.nodes.index[node],:].todense()))

    @staticmethod
    def transition_matrix(network: Network, weight: bool = False) -> sp.sparse.csr_matrix:
        """Returns a transition matrix that describes a random walk process in the given network.

        Parameters
        ----------
            network: Network
            The network for which the transition matrix will be created. 
        
            weight: bool
            Whether to account for edge weights when computing transition probabilities.
        """
        A = adjacency_matrix(network, weight=weight)
        D = A.sum(axis=1)
        T = sp.sparse.csr_matrix((network.number_of_nodes(), network.number_of_nodes()))
        for i in range(network.number_of_nodes()):
            T[i,:] = A[i,:]/D[i]
        return T

    @property
    def matrix(self) -> sp.sparse.csr_matrix:
        """Returns the transition matrix of the random walk
        """
        return self._transition_matrix

    @property
    def t(self):
        """Returns the current `time` of the random walker, i.e. 
        the number of random walk steps since the initial state.
        The initial time is set to zero and the initial state does not 
        count as a step.
        """
        return self._t

    @property
    def state(self) -> str:
        """Returns the current state of the random walk process
        """
        return self._current_node

    def walk(self, steps: int=1) -> str:
        """Returns a generator object that yields a sequence of `steps` visited
        nodes, starting from the current state of the random walk process.

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

            >>> s = rw.transition()
            >>> print(s)
            b

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
        """Performs a single transition of the random walk 
        and returns the visited node"""
        return next(self.walk())
