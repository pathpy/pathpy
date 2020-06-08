"""Random walker in pathpy."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : random_walk.py -- Class to simulate random walks
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Mon 2020-04-20 11:02 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
import abc
from typing import Any, Optional, Union

import numpy as np
import scipy as sp  # pylint: disable=import-error
from scipy.sparse import linalg as spl

from pathpy import logger, tqdm
# from pathpy.core.path import Path
from pathpy.core.network import Network
from pathpy.algorithms.matrices import adjacency_matrix

# create custom types
Weight = Union[str, bool, None]

# create logger
LOG = logger(__name__)


class BaseWalk:
    """Abstract base class for all implementations of walk processes.
    """
    @abc.abstractmethod
    def walk(self, steps: int):
        """Abstract walk property."""

    @abc.abstractproperty
    def t(self) -> int:
        """Abstract time property."""

    @abc.abstractproperty
    def state(self):
        """Abstract state property."""


class RandomWalk(BaseWalk):
    """Class for a random walker

    Instances of this class represent the state of a random walk in a
    network.

    """

    def __init__(self, network: Network, weight: Weight = None,
                 start_node: Optional[str] = None, restart_prob = 0) -> None:
        """Initialises a random walk process in a given start node.

        The initial time t of the random walk will be set to zero and the
        initial state is set to the given start node. If start_node is omitted a
        node will be chosen uniformly at random.

        """
        # initialize variables

        # network in which the random walk is simulated
        self._network: Network = network

        # time of the random walk
        self._t: int = 0

        # transition matrix for the random walk
        self._transition_matrix = RandomWalk.transition_matrix(network, weight, restart_prob)

        # uids of the nodes
        self._node_uids: list = list(network.nodes.keys())

        self._visitations = np.ravel(
            np.zeros(shape=(1, network.number_of_nodes())))        

        # path of the random walker
        # TODO: implement new path class
        # self._path = Path()

        # eigenvectors and eigenvalues
        _, eigenvectors = spl.eigs(
            self._transition_matrix.transpose(), k=1, which='LM')
        pi = eigenvectors.reshape(eigenvectors.size, )

        # stationary probabilities
        self._stationary_probabilities = np.real(pi/np.sum(pi))

        if start_node is None:
            self._current_node = np.random.choice(self._node_uids)
        elif start_node not in network.nodes:
            LOG.warning('Invalid start node for random walk. '
                        'Picking random node.')
            self._current_node = np.random.choice(self._node_uids)
        else:
            self._current_node = start_node

        # TODO: implement new path class
        # self._path.add_node(self._network.nodes[self._current_node])

    def stationary_probabilities(self, **kwargs: Any) -> np.array:
        """Computes stationary visitation probabilities.

        Computes stationary visitation probabilities of nodes based on the
        leading eigenvector of the transition matrix.

        Parameters
        ----------

        **kwargs: Any

            Arbitrary key-value pairs that will be passed to the
            scipy.sparse.linalg.eigs function.

        """
        _p = self._stationary_probabilities
        if kwargs:
            _, eigenvectors = sp.sparse.linalg.eigs(
                self._transition_matrix.transpose(), k=1, which='LM', **kwargs)
            pi = eigenvectors.reshape(eigenvectors.size, )
            _p = np.real(pi/np.sum(pi))
        return _p

    def visitation_probabilities(self) -> np.array:
        """Returns the visitation probabilities of nodes.

        Returns the visitation probabilities of nodes based on the history of
        the random walk. Initially, all visitation probabilities are zero.

        """
        return np.nan_to_num(self._visitations/self._t)

    @property
    def total_variation_distance(self) -> float:
        """Computes the total variation distance.

        Computes the total variation distance between the current visitation
        probabilities and the stationary probabilities. This quantity converges
        to zero for RandomWalk.t -> np.infty and its magnitude indicates the
        current relaxation of the random walk process.

        """
        return np.abs(self._stationary_probabilities
                      - self.visitation_probabilities()).sum()/2.0

    def transition_probabilities(self, node: str) -> np.array:
        """Returns a vector that contains transition probabilities.

        Returns a vector that contains transition probabilities from a given
        node to all other nodes in the network.

        """
        return np.nan_to_num(np.ravel(
            self._transition_matrix[
                self._network.nodes.index[node], :].todense()))

    @staticmethod
    def transition_matrix(network: Network,
                          weight: Weight = None, restart_prob: float = 0) -> sp.sparse.csr_matrix:
        """Returns a transition matrix of the random walker.

        Returns a transition matrix that describes a random walk process in the
        given network.

        Parameters
        ----------
        network: Network

            The network for which the transition matrix will be created.

        weight: bool

            Whether to account for edge weights when computing transition
            probabilities.

        """
        A = adjacency_matrix(network, weight=weight)
        D = A.sum(axis=1)
        n = network.number_of_nodes()
        T = sp.sparse.csr_matrix((n, n))
        for i in range(n):
            if D[i]>0:
                LOG.warning('Computing transition matrix for node with zero out-degree')
            for j in range(n):
                if D[i]>0:
                    T[i,j] = restart_prob*(1./n) + (1-restart_prob)*A[i,j]/D[i]
                else:                    
                    if restart_prob>0:
                        T[i,j] = 1./n 
                    else:     
                        T[i,j] = 0.0
        return T

    @property
    def matrix(self) -> sp.sparse.csr_matrix:
        """Returns the transition matrix of the random walk
        """
        return self._transition_matrix

    @property
    def t(self) -> int:
        """Returns the current `time` of the random walker

        i.e. the number of random walk steps since the initial state.  The
        initial time is set to zero and the initial state does not count as a
        step.

        """
        return self._t

    @property
    def state(self) -> str:
        """Returns the current state of the random walk process
        """
        return self._current_node

    def walk(self, steps: int = 1):
        """Generator object that yields a sequence of `steps` visited nodes.

        Returns a generator object that yields a sequence of `steps` visited
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
        if self._current_node is None:
            # Terminate the iteration
            return None
        for t in tqdm(range(steps)):
            prob = self.transition_probabilities(self._current_node)
            if prob.sum() == 0:
                self._current_node = None
                # Terminate the iteration
                return None
            i = np.random.choice(a=self._network.number_of_nodes(), p=prob)
            self._current_node = self._node_uids[i]
            self._visitations[i] += 1
            self._t += 1

            # TODO: implement new path class
            # self._path.add_node(self._network.nodes[self._current_node])

            # yield the next visited node
            yield self._current_node

    def transition(self) -> str:
        """Transition of the random walk.

        Performs a single transition of the random walk and returns the visited
        node

        """
        return next(self.walk())

    # TODO: implement new path class
    # @property
    # def path(self) -> Path:
    #     return self._path
