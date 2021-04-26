"""This module contains classes to efficiently simlate random walks on static, temporal, and higher-order networks. 
"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : random_walk.py -- Class to simulate random walks in (higher-order) networks
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Mon 2020-04-20 11:02 ingo>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations
import abc

from scipy.sparse.construct import random
from pathpy.models.higher_order_network import HigherOrderEdge, HigherOrderNetwork, HigherOrderNode

from pathpy.core.node import NodeCollection
from typing import Any, Iterable, Optional, Union

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
    Implementation of fast biased sampling from a discrete distribution
    of values [0, ..., n]
    
    For explanation see https://www.keithschwarz.com/darts-dice-coins/

    Parameters
    ----------

    weights: Union[np.array, list]

        relative weights of the n events, where weights[i] is the relative 
        statistical weight of event i. The weights do not need to be 
        normalized. 
        
        For an array with length n, generated random values 
        will be from range(n).
        
    See Also
    --------
    RandomWalk

    Examples
    --------
    Create a VoseAliasSampling instance

    >>> from pathpy.processes.RandomWalk import VoseAliasSampling
    >>> sampler = VoseAliasSampling([1,1,2])
    
    Fast biased sampling in O(1)
    
    >>> [ sampler.sample() for i in range(10) ]
    [ 0 2 0 1 2 1 2 1 2 0 2 2 ] 
    """

    def __init__(self, weights: Union[np.array, list]) -> None:
        """
        Initializes probability and alias tables
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

    def sample(self) -> int:
        """
        Biased sampling of discrete value in O(1)

        Returns
        -------
            integer value from range(n), where n is the length 
            of the weight array used to create the instance.

        """
        i = np.random.randint(1, self.n+1)
        x = np.random.rand()
        if x < self.probs[i]:
            return i-1
        else:
            return self.aliases[i]-1


class RandomWalk(BaseWalk):
    """Implements a (biased) random walk process in a network or higher-order 
    network.

    Parameters
    ----------
    network: Network

        The network instance on which to perform the random walk process. Can also 
        be an instance of HigherOrderNetwork.

    weight: Weight = None

        If specified, the given numerical edge attribute will be used to bias
        the random walk transition probabilities.

    restart_probability: float = 0

        The per-step probability that a random walker restarts in a random node

    See Also
    --------
    VoseAliasSampling

    Examples
    --------
    Create a Network an RandomWalk instance

    >>> import pathpy as pp
    >>> n = pp.Network(directed=False)
    >>> n.add_edge('a', 'b', weight=1, uid='a-b')
    >>> n.add_edge('b', 'c', weight=1, uid='b-c')
    >>> n.add_edge('c', 'a', weight=2, uid='c-a')
    >>> n.add_edge('c', 'd', weight=1, uid='c-d')
    >>> n.add_edge('d', 'a', weight=1, uid='d-a')

    Generate a random walk with 10 steps starting from node 'a'

    >>> rw = pp.processes.RandomWalk(n, weight='weight')
    >>> p = rw.generate_walk(steps=10, start_node=n.nodes['a'])
    >>> pprint([v.uid for v in p.nodes ]) 
    [ 'a', 'b', 'c', 'a', 'a', 'b', 'c', 'd', 'a', 'b'] 

    Random walk using iterator interface

    >>> for x in rw.walk(5, start_node=n.nodes['a']):
    >>>     print('Current node = {0}'.format(v))
    >>>     print(rw.visitation_probabilities())
    Current node = b
    [0.5 0.5 0.  0. ]
    Current node = c
    [0.33333333 0.33333333 0.33333333 0.        ]
    Current node = d
    [0.25 0.25 0.25 0.25]
    Current node = a
    [0.4 0.2 0.2 0.2]
    Current node = b
    [0.33333333 0.33333333 0.16666667 0.16666667]
    Current node = a
    [0.42857143 0.28571429 0.14285714 0.14285714]
    Current node = c
    [0.375 0.25  0.25  0.125]
    Current node = a
    [0.44444444 0.22222222 0.22222222 0.11111111]
    Current node = b
    [0.4 0.3 0.2 0.1]
    Current node = a
    [0.45454545 0.27272727 0.18181818 0.09090909]
    """

    def __init__(self, network: Network, weight: Optional[Weight] = None, restart_prob: float = 0) -> None:
        """Initialises a random walk process.
        """

        # network (or higher-order network) in which we perform the random walk
        self._network: Network = network

        # current time of the random walk
        self._t: int = -1

        # currently visited node (or higher-order node)
        self._current_node: Optional[Node] = None

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

            Arbitrary key-value pairs to bee passed to the
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
        """Returns current normalized visitation frequencies of nodes based on the history of
        the random walk. Initially, all visitation probabilities are zero except for the start node.
        """
        return np.nan_to_num(self._visitations/(self._t+1))

    def visitation_probabilities(self, t, start_node: Node) -> np.ndarray:
        """Calculates visitation probabilities of nodes after t steps for a given start node

        Initially, all visitation probabilities are zero except for the start node.
        """
        assert start_node.uid in self._network.nodes.uids

        initial_dist = np.zeros(self._network.number_of_nodes())
        initial_dist[self._network.nodes.index[start_node.uid]] = 1.0
        return np.dot(initial_dist, (self._transition_matrix**t).todense())

    @property
    def total_variation_distance(self) -> float:
        """Returns the total variation distance between stationary 
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
    def TVD(a: np.array ,b: np.array) -> float:        
        return np.abs(a - b).sum()/2.0

    @staticmethod
    def transition_matrix(network: Network,
                          weight: Optional[Weight] = None, restart_prob: float = 0) -> sp.sparse.csr_matrix:
        """Returns the transition matrix of a (biased) random walk in the given network.

        Returns a transition matrix that describes a random walk process in the
        given network.

        Parameters
        ----------
        network: Network

            The network for which the transition matrix will be created.

        weight: Weight

            If specified, the numerical edge attribute that shall be used in the biased
            transition probabilities of the random walk.

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

    def matrix_pd(self) -> DataFrame:
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
    def state(self) -> Optional[Node]:
        """Returns the current state of the random walker
        """
        return self._current_node

    def generate_walk(self, steps: int = 1, start_node: Optional[Union[Node, HigherOrderNode]] = None) -> Path:
        """Returns a path that represents the sequence of nodes traversed 
        by a single random walk with a given number of steps 
        (and an optional given start node)

        Parameters
        ----------

        steps: int = 1
            
            The number of steps of the random walk

        start_node: Optional[Node] = None

            If specified, the random walk will start from the given node. If not given, 
            a random start node will be chosen uniformly.

        Returns
        -------

        A Path object containing the sequence of traversed nodes
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
            next_node = self.reverse_index[self.samplers[self._current_node.uid].sample()]
            assert (self._current_node.uid, next_node) in self._network.edges, 'Assertion Error: {0} not in edge list'.format((self._current_node.uid, next_node))
            traversed_edge: Union[Edge, HigherOrderEdge] = self._network.edges[(self._current_node.uid, next_node)]
            if type(self._network) == Network:
                walk._path.append(traversed_edge)
            elif type(self._network) == HigherOrderNetwork:
                # map to first-order edge
                walk._path.append(traversed_edge.w.edges[-1])
            else:
                raise AttributeError('Unknown network of type {0}'.format(type(self._network)))
            self._t += 1
            self._current_node = self._network.nodes[next_node]
        return walk


    def generate_walks(self, steps_per_walk: int, start_nodes: Union[int, Iterable[Node]]) -> PathCollection:
        """Returns a PathCollection generated by a number of random walkers starting in different (random) nodes.

        Parameters
        ----------

            steps_per_walk: int
                The number of steps to be performed for each random walk

            start_nodes: Union[int, NodeCollection]
                The (number of) start nodes to use for the generated random walks. If an integer k is given, 
                k random walks will be generated for start nodes chosen uniformly at random. If a list of Node
                objects is given, a single random walk will be started for each entry in the list.

        Returns
        -------

            A PathCollection instance. Each random walk is represented by one Path instance in this collection.

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
