"""Random walker in pathpy."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : random_walk.py -- Class to simulate random walks in (higher-order) networks
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Mon 2020-04-20 11:02 ingo>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
import abc

from scipy.sparse.construct import random
from pathpy.models.higher_order_network import HigherOrderNetwork

from pathpy.core.node import NodeCollection
from typing import Any, Optional, Union, overload

import numpy as np
import scipy as sp  # pylint: disable=import-error
from scipy.sparse import linalg as spl
from scipy import linalg as spla
from pandas import DataFrame

from pathpy import logger, tqdm

from pathpy.core.path import Path
from pathpy.core.path import PathCollection
from pathpy.models.network import Network
from pathpy.models.network import Node
from pathpy.models.network import Edge

from pathpy.algorithms.matrices import adjacency_matrix

# create custom types
Weight = Union[str, bool, None]

# create logger
LOG = logger(__name__)


class BaseWalk:
    """Abstract base class for all implementations of a walk processes.
    """
    @abc.abstractmethod
    def walk_step(self):
        """Abstract walk step method."""

    @abc.abstractmethod
    def generate_walk(self, steps: int, start_node: Node):
        """Abstract method to generate a single walk."""

    @abc.abstractmethod
    def generate_walks(self, steps_per_walk: int, start_nodes: NodeCollection):
        """Abstract method to generate multiple walks from different start nodes."""

    @abc.abstractmethod
    def walk(self, steps: int, start_node: Node):
        """Abstract generator method to perform random walk."""

    @abc.abstractproperty
    def t(self) -> int:
        """Abstract time property."""

    @abc.abstractproperty
    def state(self):
        """Abstract state property."""


class VoseAliasSampling:    
    """
    Implementation of fast biased sampling from discrete distributions following https://www.keithschwarz.com/darts-dice-coins/
    """

    def __init__(self, weights):
        """
        Initialize probability and alias tables
        """
        self.n = len(weights)
        self.probs = dict()
        self.scaled_probs = dict()
        self.aliases = dict()

        small = list()
        large = list()

        for i in range(1, self.n+1):
            self.probs[i] = weights[i-1]
            self.scaled_probs[i] = self.n*weights[i-1]
            if self.scaled_probs[i]>1:
                large.append(i)
            elif self.scaled_probs[i]<=1:
                small.append(i)

        while small and large:
            l = small.pop()
            g = large.pop()

            self.probs[l] = self.scaled_probs[l]
            self.aliases[l] = g
            self.scaled_probs[g] = self.scaled_probs[l] + self.scaled_probs[g] -1

            if self.scaled_probs[g] < 1:
                small.append(g)
            else:
                large.append(g)
        while large:
            g = large.pop()
            self.probs[g] = 1
        while small:
            l = small.pop()
            self.probs[l] = 1

    def sample(self):
        """
        Biased sampling of discrete value in O(1)
        """
        i = np.random.randint(1, self.n+1)
        x = np.random.rand()
        if x < self.probs[i]:
            return i-1
        else:
            return self.aliases[i]-1




class RandomWalk(BaseWalk):
    """Random Walk Process in a Network"""

    def __init__(self, network: Network, weight: Weight = None, restart_prob = 0) -> None:
        """Initialises a random walk process in a given start node.

        The initial time t of the random walk will be set to zero and the
        initial state is set to the given start node. If start_node is omitted a
        node will be chosen uniformly at random.
        """
        # initialize variables

        # network (or higher-order network) in which we perform the random walk
        self._network: Network = network

        # current time of the random walk
        self._t: int = -1

        # currently visited node (or higher-order node)
        self._current_node = None

        # transition matrix for the random walk
        self._transition_matrix = RandomWalk.transition_matrix(network, weight, restart_prob)

        # initialize Vose Alias Samplers
        self.reverse_index = { v:k for k,v in network.nodes.index.items() }
        self.samplers = { v:VoseAliasSampling(self.transition_probabilities(v)) for v in network.nodes.uids }

        # number of times each node has been visited
        self._visitations = np.ravel(
            np.zeros(shape=(1, network.number_of_nodes())))        

        # compute eigenvectors and eigenvalues of transition matrix
        if network.number_of_nodes()>2:
            _, eigenvectors = spl.eigs(            
                    self._transition_matrix.transpose(), k=1, which='LM')
            pi = eigenvectors.reshape(eigenvectors.size, )
        else:
            eigenvals, eigenvectors = spla.eig(self._transition_matrix.transpose().toarray())
            x = np.argsort(-eigenvals)
            pi = eigenvectors[x][:,0]

        # calculate stationary visitation probabilities
        self._stationary_probabilities = np.real(pi/np.sum(pi))


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

    def visitation_frequencies(self) -> np.array:
        """Returns current normalized visitation frequencies of nodes in the sequence of visited nodes.

        Returns the visitation probabilities of nodes based on the history of
        the random walk. Initially, all visitation probabilities are zero except for the start node.

        """
        return np.nan_to_num(self._visitations/(self._t+1))

    def visitation_probabilities(self, t, start_node) -> np.array:
        """Calculates visitation probabilities of nodes after t steps for a given start node

        Initially, all visitation probabilities are zero except for the start node.
        """
        assert start_node in self._network.nodes.uids

        initial_dist = np.zeros(self._network.number_of_nodes())
        initial_dist[self._network.nodes.index[start_node]] = 1.0
        return np.dot(initial_dist, (self._transition_matrix**t).todense())

    @property
    def total_variation_distance(self) -> float:
        """Computes the total variation distance between stationary 
        visitation probabilities and the current visitation frequencies

        Computes the total variation distance between the current visitation
        probabilities and the stationary probabilities. This quantity converges
        to zero for RandomWalk.t -> np.infty and its magnitude indicates the
        current relaxation of the random walk process.

        """
        return self.TVD(self._stationary_probabilities, self.visitation_frequencies())

    def transition_probabilities(self, node: str) -> np.array:
        """Returns a vector that contains transition probabilities.

        Returns a vector that contains transition probabilities from a given
        node to all other nodes in the network.

        """
        return np.nan_to_num(np.ravel(
            self._transition_matrix[
                self._network.nodes.index[node], :].todense()))

    @staticmethod
    def TVD(a ,b) -> float:        
        return np.abs(a - b).sum()/2.0

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
        T = sp.sparse.lil_matrix((n, n))
        zero_deg = 0
        for i in range(n):
            if D[i]==0:
                zero_deg += 1
            for j in range(n):
                if D[i]>0:
                    T[i,j] = restart_prob*(1./n) + (1-restart_prob)*A[i,j]/D[i]
                else:
                    if restart_prob>0:
                        T[i,j] = 1./n 
                    else:     
                        T[i,j] = 0.0
        if zero_deg > 0:
            LOG.warning('Network contains {0} nodes with zero out-degree'.format(zero_deg))
        return T.tocsr()

    @property
    def matrix(self) -> sp.sparse.csr_matrix:
        """Returns the transition matrix of the random walk
        """
        return self._transition_matrix

    def matrix_pretty(self) -> DatFrame:
        """
        """
        return DataFrame(self.matrix.todense(), columns=[v for v in self._network.nodes.index], index=[v for v in self._network.nodes.index])

    @property
    def t(self) -> int:
        """Returns the current `time` of the random walker, i.e. the number of random
        walk steps since the initial state. The initial time is zero and the initial 
        state does not count as a step.
        """
        return self._t

    @property
    def network(self) -> Network:
        """Returns the network in which the random walk is performed
        """
        return self._network

    @property
    def state(self) -> str:
        """Returns the current state of the random walker
        """
        return self._current_node

    def generate_walk(self, steps: int = 1, start_node: Optional[Node] = None):
        """Returns a path that represents the sequence of nodes traversed 
        by a single random walk with a given number of steps (and an optional start node)
        """

        # Choose random start node if no node is given
        if start_node is None:
            start_node = self._network.nodes[np.random.choice(list(self._network.nodes.uids))]
        elif start_node.uid not in self._network.nodes.uids:
            LOG.error('Invalid start node for random walk.')
            raise AttributeError('Invalid start node for random walk.')
        
        # initialize walk
        if type(self._network) == Network:
            walk = Path(start_node)
        elif type(self._network) == HigherOrderNetwork:
            walk = Path(start_node.nodes[-1])
        else:
            raise AttributeError('Unknown network of type {0}'.format(type(self._network)))
        self._t = 0
        self._current_node = start_node

        # construct walk
        for i in range(steps):
            next = self.reverse_index[self.samplers[self._current_node.uid].sample()]
            assert (self._current_node.uid, next) in self._network.edges, 'Assertion Error: {0} not in edge list'.format((self._current_node.uid, next))
            traversed_edge = self._network.edges[(self._current_node.uid, next)]
            if type(self._network) == Network:
                walk._path.append(traversed_edge)
            elif type(self._network) == HigherOrderNetwork:
                # map to first-order edge
                walk._path.append(traversed_edge.w.edges[-1])
            else:
                raise AttributeError('Unknown network of type {0}'.format(type(self._network)))
            self._t += 1
            self._current_node = self._network.nodes[next]
        return walk


    def generate_walks(self, steps_per_walk: int, start_nodes: Union[int, NodeCollection]):
        """Returns a PathCollection generated by a number of random walkers starting in different (random) nodes.
        """

        walks = PathCollection()

        # generate random start_nodes if no nodes are given
        if type(start_nodes) == int:
            for i in range(start_nodes):
                walks.add(self.generate_walk(steps_per_walk))
        else:
            for v in start_nodes:
                walks.add(self.generate_walk(steps_per_walk, start_node=v))
        
        return walks

    def walk(self, steps: int = 1, start_node: Optional[Node] = None) -> str:
        """Generator object which yields a configurable number of nodes visited by a random walker.

        Parameters
        ----------
        steps: int

            The number of random walk steps to simulate

        start_node: str
        
            Where to start the random walk

        Example
        -------
        >>> n = pp.Network('a-b-c-a-c-b')
        >>> rw = pp.processes.RandomWalk(n)
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

        if start_node is None:
            start_node = self._network.nodes[np.random.choice(list(self._network.nodes.uids))]

        reverse_index = { k:v for v,k in self._network.nodes.index.items()}

        # initialize walk
        self._t = 0
        self._current_node = start_node
        self._visitations = np.ravel(np.zeros(shape=(1, self._network.number_of_nodes())))
        self._visitations[self._network.nodes.index[start_node.uid]] = 1
                    
        for t in range(steps):
            prob = self.transition_probabilities(self._current_node.uid)
            if prob.sum() == 0:
                self._current_node = None
                # Terminate loop
                return None
            i = np.random.choice(a=self._network.number_of_nodes(), p=prob)
            self._current_node = self._network.nodes[reverse_index[i]]
            self._visitations[i] += 1
            self._t += 1

            # yield the next visited node
            if type(self._network) == Network:
                yield self._current_node.uid
            elif type(self._network) == HigherOrderNetwork:
                yield self._current_node.nodes[-1].uid
            else:
                raise AttributeError('Unknown network of type {0}'.format(type(self._network)))

    def transition(self) -> str:
        """Transition of the random walk.

        Performs a single transition of the random walk and returns the visited
        node

        """
        return next(self.walk())
