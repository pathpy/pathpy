"""Classes to simlate random walks on static, temporal, and higher-order networks. 
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
from typing import Any, Iterable, Optional, Union, Set, Tuple

import numpy as np
import scipy as sp  # pylint: disable=import-error
from scipy.sparse import linalg as spl
from scipy import linalg as spla
from pandas import DataFrame

from pathpy import logger, tqdm

from pathpy.core.path import Path
from pathpy.core.path import PathCollection
from pathpy.models.network import Network
from pathpy.models.temporal_network import TemporalNetwork, TemporalNode
from pathpy.models.network import Node
from pathpy.models.network import Edge

from pathpy.algorithms.matrices import adjacency_matrix

from .sampling import VoseAliasSampling
from .process import BaseProcess

# create custom types
Weight = Union[str, bool, None]

# create logger
LOG = logger(__name__)

class RandomWalk(BaseProcess):
    """Class that implements a biased random walk process in a network.
    
    Instances of this class can be used to simulate random walk processes in any instance
    of the class Network. The random walk process can include weighted edges as well as a 
    restart probability, i.e. a per-step probability to teleport to a
    randomly chosen node.

    Since any instance of HigherOrderNetwork is also an instance of Network, this class
    can be directly be applied to simulate random walks in higher-order networks. However, 
    the state space of such a random walk is given by the higher-order nodes. If you wish to
    simulate a higher-order random walk while projecting states to the corresponding first-order 
    network, you should use the class HigherOrderRandomWalk instead.

    The implementation follows the general concept to simulate discrete-time (stochastic) processes
    as implemented in the base class BaseProcess. Hence, the user can either use the iterator interface
    to iterate through the steps of a single random walk process, or use the `run_experiment` function
    to simulate multiple runs of a random walk with different start nodes (i.e. seeds).

    The `run_experiment` function returns a pandas DataFrame object that contains all node state changes 
    during the process' evolution. This data frame can be converted to Path and PathCollection objects 
    and it can be visualized using the plot function.

    Examples
    --------
    Generate and visualize a single biased random walk with 10 steps on a network

    >>> import pathpy as pp
    >>> n = pp.Network(directed=False)
    >>> n.add_edge('a', 'b', weight=1, uid='a-b')
    >>> n.add_edge('b', 'c', weight=1, uid='b-c')
    >>> n.add_edge('c', 'a', weight=2, uid='c-a')
    >>> n.add_edge('c', 'd', weight=1, uid='c-d')
    >>> n.add_edge('d', 'a', weight=1, uid='d-a')
    >>> rw = pp.processes.RandomWalk(n, weight='weight')
    >>> data = rw.run_experiment(steps=10, seed='a')
    >>> rw.plot(data)
    [interactive visualization]

    Generate a single random walk with 10 steps starting from node 'a' and 
    return a Path instance

    >>> p = rw.get_path(rw.run_experiment(steps=10, runs=['a']))
    >>> pprint([v.uid for v in p.nodes ]) 
    [ 'a', 'b', 'c', 'a', 'a', 'b', 'c', 'd', 'a', 'b']

    Generate one random walk with 10 steps starting from each node and 
    return a PathCollection instance

    >>> pc = rw.get_paths(rw.run_experiment(steps=10, runs=n.nodes.uids))
    >>> pprint([v.uid for v in p.nodes ]) 
    [ 'a', 'b', 'c', 'a', 'a', 'b', 'c', 'd', 'a', 'b'] 
    [ 'd', 'a', 'b', 'c', 'd', 'a', 'b', 'c', 'a', 'b', 'c' ]
    [ 'c', 'a', 'b', 'c', 'a', 'b', 'c', 'd', 'a', 'b', 'c' ]
    [ 'b', 'c', 'a', 'b', 'c', 'd', 'a', 'b', 'c', 'a', 'b' ]

    Simulate a random walk using the iterator interface, which provides full access 
    to the state after each simulation step

    >>> for time, _ in rw.simulation_run(steps=5, seed='a'):
    >>>     print('Current node = {0}'.format(rw.current_node))
    >>>     print(rw.visitation_frequencies)
    Current node = b
    [0.5 0.5 0.  0. ]
    Current node = c
    [0.33333333 0.33333333 0.33333333 0. ]
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
        """Creates a biased random walk process in a network.

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
        VoseAliasSampling, HigherOrderRandomWalk, BaseProcess
        """

        # transition matrix of random walk
        self._transition_matrix = RandomWalk.compute_transition_matrix(network, weight, restart_prob)

        # initialize Vose Alias Samplers
        self.reverse_index = { v:k for k,v in network.nodes.index.items() }
        self.samplers = { v:VoseAliasSampling(np.nan_to_num(np.ravel(
            self._transition_matrix[
                network.nodes.index[v], :].todense()))) for v in network.nodes.uids }

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
        
        self._network = network
        self.init(self.random_seed())    

    def init(self, seed: str) -> None:
        """
        Initializes the random walk state with a given seed/source node

        Parameters
        ----------

        seed: str

            uid of the node in which the random walk will start
        """
        # reset currently visited node (or higher-order node)
        self._current_node = seed

        # set time
        self._t = 0

        # set number of times each node has been visited
        self._visitations = np.ravel(
            np.zeros(shape=(1, self._network.number_of_nodes())))
        self._visitations[self._network.nodes.index[seed]] = 1

    def random_seed(self) -> str:
        """
        Returns a random node from the network, chosen uniformly at random
        """
        return np.random.choice(list(self._network.nodes.uids))

    def step(self) -> Iterable[str]:
        """
        Function that will be called for each step of the random walk. This function 
        returns a tuple, where the first entry is the uids of the currently visited node and the second entry is the uid of the previously visited node.
        """

        # determine next node
        next_node = self.reverse_index[self.samplers[self._current_node].sample()]
        assert (self._current_node, next_node) in self._network.edges, 'Assertion Error: {0} not in edge list'.format((self._current_node, next_node))
        
        previous_node = self._current_node
        self._current_node = next_node

        # increment visitations and current time
        self._visitations[self._network.nodes.index[self._current_node]] += 1
        self._t += 1

        # return tuple of changed nodes, where the first node is the currently visited node
        return (self._current_node, previous_node)

    def node_state(self, v: str) -> bool:
        """
        Returns a boolean variable indicating whether the walker is currently 
        visiting (first-order) node v
        """
        if v in self._network.nodes:
            return v == self._current_node
        elif type(self._network) == HigherOrderNetwork:
            return v == self._network.nodes[self._current_node].edges[-1].w.uid
        else:
            raise NotImplementedError('Random walk not implemented for network of type {0}'.format(type(self._network)))

    @property
    def time(self) -> int:
        """
        The current time of the random walk process, i.e. the number of steps taken since the start node.
        """
        return self._t    

    def state_to_color(self, state: bool) -> str:
        """
        Maps the current (visitation) state of nodes to colors for visualization. The state is True for the currently visited node and False for all other nodes.

        Parameters
        ----------

        state: bool
        """
        if state:
            return 'red'
        else:
            return 'blue'

    @staticmethod
    def compute_transition_matrix(network: Network,
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
    def transition_matrix(self) -> sp.sparse.csr_matrix:
        """Returns the transition matrix of the random walk
        """
        return self._transition_matrix

    def transition_probabilities(self, node: str) -> np.array:
        """Returns a vector that contains transition probabilities.

        Returns a vector that contains transition probabilities from a given
        node to all other nodes in the network.

        """
        return np.nan_to_num(np.ravel(
            self._transition_matrix[
                self._network.nodes.index[node], :].todense()))

    def visitation_probabilities(self, t, seed: str) -> np.ndarray:
        """Calculates visitation probabilities of nodes after t steps for a given start node

        Initially, all visitation probabilities are zero except for the start node.
        """
        assert seed in self._network.nodes.uids

        initial_dist = np.zeros(self._network.number_of_nodes())
        initial_dist[self._network.nodes.index[seed]] = 1.0
        return np.dot(initial_dist, (self._transition_matrix**t).todense())


    def transition_matrix_pd(self) -> DataFrame:
        """
        Returns the transition matrix as pandas DataFrame with proper row/column labels.
        """
        return DataFrame(self.transition_matrix.todense(), columns=[v for v in self._network.nodes.index], index=[v for v in self._network.nodes.index])


    @property
    def current_node(self) -> str:
        return self._current_node


    def get_path(self, data: DataFrame, run_id: Optional[int]=0, first_order: Optional[bool]=True) -> Path:
        """Returns a path that represents the sequence of (first-order) nodes traversed 
        by a single random walk.

        Parameters
        ----------

        data: DataFrame
            Pandas data frame containing the trajectory of one or more (higher-order) random walks, generated by a call of `run_experiment`

        run_uid: Optional[int]=0
               Uid of the random walk simulation to be returns as Path (default: 0).

        Returns
        -------

        Path
            Path object containing the sequence of nodes traversed by the random walk

        See Also
        --------

        Path
        """
        # list of traversed nodes starting with seed node
        walk_steps = list(data.loc[(data['run_id']==run_id) & (data['state']==True)]['node'].values)        

        # generate Path
        return Path(*[walk_steps[i] for i in range(len(walk_steps))], directed=True, ordered=True)


    def get_paths(self, data: DataFrame, run_ids: Optional[Iterable]=None) -> PathCollection:
        """Returns a PathCollection where each 

        Parameters
        ----------

        data: DataFrame
            Pandas data frame containing the trajectory of one or more random walks, generated by 
            `run_experiment`

        run_uids: Optional[Iterable]=None
            Uids of the random walk simulations to be included in the PathCollection instance. If None (default), all random walk simulations will be included.

        Returns
        -------

        PathCollection
            PathCollection object where each random walk is represented by one Path instance in the collection.

        See Also
        --------

        PathCollection
        """
        
        if not run_ids: # generate paths for all run_ids in the data frame
            runs =data['run_id'].unique()
        else:
            runs = run_ids

        pc = PathCollection()
        for i in runs:
            pc.add(self.get_path(data, i))

        return pc


    def stationary_state(self, **kwargs: Any) -> np.array:
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

    @property
    def visitation_frequencies(self) -> np.array:
        """Returns current normalized visitation frequencies of nodes based on the history of
        the random walk. Initially, all visitation probabilities are zero except for the start node.
        """
        return np.nan_to_num(self._visitations/(self._t+1))

    @property
    def total_variation_distance(self) -> float:
        """Returns the total variation distance between stationary 
        visitation probabilities and the current visitation frequencies

        Computes the total variation distance between the current visitation
        probabilities and the stationary probabilities. This quantity converges
        to zero for RandomWalk.t -> np.infty and its magnitude indicates the
        current relaxation of the random walk process.

        """
        return self.TVD(self.stationary_state(), self.visitation_frequencies)

    @staticmethod
    def TVD(a: np.array ,b: np.array) -> float:        
        """Calculates the total variation distance between two probability vectors
        """
        return np.abs(a - b).sum()/2.0


class HigherOrderRandomWalk(RandomWalk):
    """Class that implements a biased random walk process in a higher-order network.
        
        Instances of this class can be used to simulate random walk processes in higher-order networks for 
        arbitrary orders k. The random walk process can include weighted edges as well as a 
        restart probability, i.e. a per-step probability to teleport to a
        randomly chosen higher-order node.

        Different from the class RandomWalk, instances of class HigherOrderRandomWalk automatically project states to the corresponding first-order network, i.e. paths and visualisations are given 
        in terms of the nodes in the first-order network, while the dynamics of the random walk is governed by the underlying higher-order network.

        The implementation follows the general concept to simulate discrete-time (stochastic) processes
        as implemented in the base class BaseProcess. Hence, the user can either use the iterator interface
        to iterate through the steps of a single random walk process, or use the `run_experiment` function
        to simulate multiple runs of a random walk with different start nodes (i.e. seeds).

        The `run_experiment` function returns a pandas DataFrame object that contains all node state changes 
        during the process' evolution. This data frame can be converted to Path and PathCollection objects 
        and it can be visualized using the plot function.

        Examples
        --------
        Generate and visualize a single random walk with 10 steps on a higher-order network

        >>> import pathpy as pp
        >>> n = pp.Network(directed=False)
        >>> n.add_edge('a', 'b', weight=1, uid='a-b')
        >>> n.add_edge('b', 'c', weight=1, uid='b-c')
        >>> n.add_edge('c', 'a', weight=2, uid='c-a')
        >>> n.add_edge('c', 'd', weight=1, uid='c-d')
        >>> n.add_edge('d', 'a', weight=1, uid='d-a')
        >>> v1 = pp.HigherOrderNode(n.edges['a-b'], uid='a-b')
        >>> v2 = pp.HigherOrderNode(n.edges['b-c'], uid='b-c')
        >>> v3 = pp.HigherOrderNode(n.edges['c-a'], uid='c-a')
        >>> v4 = pp.HigherOrderNode(n.edges['c-d'], uid='c-d')
        >>> v5 = pp.HigherOrderNode(n.edges['d-a'], uid='d-a')
        >>> n2.add_edge(v1, v2, uid='a-b-c', weight=1)
        >>> n2.add_edge(v2, v3, uid='b-c-a', weight=1)
        >>> n2.add_edge(v2, v4, uid='b-c-d', weight=0.2)
        >>> n2.add_edge(v3, v1, uid='c-a-b', weight=1)
        >>> n2.add_edge(v4, v5, uid='c-d-a', weight=0.2)
        >>> n2.add_edge(v5, v1, uid='d-a-b', weight=1)
        >>> rw = pp.processes.HigherOrderRandomWalk(n2, weight='weight')
        >>> data = rw.run_experiment(steps=10, runs=['b-c'])
        >>> rw.plot(data)
        [interactive visualization in first-order network]

        Use `plot` function of base class to visualize random walk in second-order network

        >>> pp.processes.RandomWalk.plot(rw, data)
        [interactive visualization in second-order network]

        Generate a single random walk with 10 steps starting from node 'b-c' and 
        return a first-order path

        >>> p = rw.get_path(rw.run_experiment(steps=10, runs=['b-c']))
        >>> pprint([v.uid for v in p.nodes ]) 
        [ 'a', 'b', 'c', 'a', 'a', 'b', 'c', 'd', 'a', 'b']

        Use `get_path` function of base class to return path with second-order nodes

        >>> p = pp.processes.RandomWalk.get_path(rw2, data)
        >>> print([ v.uid for v in p.nodes ])

        Generate one random walk with 10 steps starting from each node and 
        return a PathCollection instance with first-order paths

        >>> pc = rw.get_paths(rw.run_experiment(steps=10, runs=n.nodes.uids))
        >>> pprint([v.uid for v in p.nodes ]) 
        [ 'a', 'b', 'c', 'a', 'a', 'b', 'c', 'd', 'a', 'b'] 
        [ 'd', 'a', 'b', 'c', 'd', 'a', 'b', 'c', 'a', 'b', 'c' ]
        [ 'c', 'a', 'b', 'c', 'a', 'b', 'c', 'd', 'a', 'b', 'c' ]
        [ 'b', 'c', 'a', 'b', 'c', 'd', 'a', 'b', 'c', 'a', 'b' ]

        Simulate a random walk using the iterator interface, which provides full access 
        to the state after each simulation step

        >>> for time, _ in rw2.simulation_run(steps=50, seed='b-c'):
        >>>     print('Current node = {0}'.format(rw2.first_order_node(rw2.current_node)))
        >>>     print(rw2._first_order_visitation_frequencies)
        Current node = b
        [0.33333333 0.33333333 0.33333333 0.        ]
        Current node = c
        [0.32142857 0.32142857 0.35714286 0.        ]
        Current node = a
        [0.34482759 0.31034483 0.34482759 0.        ]
        Current node = b
        [0.33333333 0.33333333 0.33333333 0.        ]
        Current node = c
        [0.32258065 0.32258065 0.35483871 0.        ]
        Current node = a

        See Also
        --------
        VoseAliasSampling, RandomWalk, BaseProcess
    """

    def __init__(self, higher_order_network: HigherOrderNetwork, first_order_network, weight: Optional[Weight] = None, restart_prob: float = 0) -> None:
        self._first_order_network = first_order_network
        RandomWalk.__init__(self, higher_order_network, weight, restart_prob)

    def init(self, seed) -> None:
        """Creates a biased random walk process in a network.

        Parameters
        ----------
        higher_order_network: HigherOrderNetwork
            The higher-order network instance on which to perform the random walk process.

        first_order_network: Network
            The first-order network instance to be used for mapping the process to first-order nodes

        weight: Weight = None
            If specified, the given numerical edge attribute will be used to bias
            the random walk transition probabilities.

        restart_probability: float = 0
            The per-step probability that a random walker restarts in a random (higher-order) node

        See Also
        --------
        RandomWalk, BaseProcess
        """
        # set number of times each first-order node has been visited
        self._first_order_visitations = np.ravel(
            np.zeros(shape=(1, self._first_order_network.number_of_nodes())))
        self._first_order_visitations[self._first_order_network.nodes.index[self._network.nodes[seed].nodes[-1].uid]] = 1
        RandomWalk.init(self, seed)

    @property
    def first_order_visitation_frequencies(self) -> np.array:
        """Returns current normalized visitation frequencies of first-order nodes based on the history of
        the higher-order random walk. Initially, all visitation probabilities are zero except for the last node of the higher-order seed node.
        """
        return np.nan_to_num(self._first_order_visitations/(self._t+1))

    def first_order_stationary_state(self, **kwargs) -> np.array:
        """Returns current normalized visitation frequencies of first-order nodes based on the history of
        the higher-order random walk. Initially, all visitation probabilities are zero except for the last node of the higher-order seed node.
        """
        first_order_stationary_state = np.ravel(
            np.zeros(shape=(1, self._first_order_network.number_of_nodes())))
        higher_order_stationary_dist = RandomWalk.stationary_state(self, **kwargs)
        for v in self._network.nodes:
            # newly visited node in first_order network
            v1 = v.nodes[-1]
            first_order_stationary_state[self._first_order_network.nodes.index[v1.uid]] += higher_order_stationary_dist[self._network.nodes.index[v.uid]]
        return first_order_stationary_state

    @property
    def first_order_total_variation_distance(self) -> float:
        """Returns the total variation distance between stationary 
        visitation probabilities and the current visitation frequencies, projected
        to nodes in the first_order_network.

        Computes the total variation distance between the current (first-order) node visitation
        probabilities and the (first-order) stationary node visitation probabilities. This quantity converges to zero for HigherOrderRandomWalk.time -> np.infty and its magnitude indicates the
        current relaxation of the higher-order random walk process.
        """
        return self.TVD(self.first_order_stationary_state(), self.first_order_visitation_frequencies)


    def first_order_node(self, higher_order_node: str) -> str:
        """
        Maps a given uid of a node in the higher-order network to the corresponding 
        first-order node.

        Parameters
        ----------
        higher_order_node: str
            The string uid of the higher-order node

        Returns
        -------
        str
            uid of the corresponding first-order node
        """
        return self._network.nodes[higher_order_node].nodes[-1].uid


    def step(self) -> Iterable[str]:
        """
        Function that will be called for each step of the random walk. This function 
        returns a tuple, where the first entry is the uids of the currently visited higher-order node and the second entry is the uid of the previously visited higher-order node.

        Use the `first_order_node` function to map those nodes to nodes in the first-order network
        """
        (current_node, previous_node) = RandomWalk.step(self)

        self._first_order_visitations[self._first_order_network.nodes.index[self._network.nodes[current_node].nodes[-1].uid]] += 1

        return (current_node, previous_node)


    def plot(self, data: DataFrame, run_id: Optional[int]=0, timescale: Optional[int]=100, **kwargs):
        """Displays an interactive plot of the random walk dynamics, projected to a first-order network based on a recorded simulation experiment

        Parameters
        ----------
        data: DataFrame
            A pandas dataframe containing the state changes recorded in a simulation of the process, as generated by function `run_experiment`
        
        run_id: Optional[int]=0
            The integer identifier of the simulation run contained in `data` that shall be visualized. 
            If omitted, a default value of zero is used, i.e. the first simulation run in `data` will 
            be visualized. 

        timescale: Optional[int]=100
            Determines the speed of the visualisation. For the default value of 100, each simulation step
            will be displayed for 100 timesteps in the visualisation.

        **kwargs
            Optional keyword-arguments that will be passed to the plot function of the underlying instance 
            of TemporalNetwork

        Examples
        --------

        Generate 10 higher-order random walks and visualize the walk dynamics of the run with id 3

        >>> import pathpy as pp
        >>> n = pp.Network(directed=False)
        >>> n.add_edge('a', 'b', weight=1, uid='a-b')
        >>> n.add_edge('b', 'c', weight=1, uid='b-c')
        >>> n.add_edge('c', 'a', weight=2, uid='c-a')
        >>> n.add_edge('c', 'd', weight=1, uid='c-d')
        >>> n.add_edge('d', 'a', weight=1, uid='d-a')
        >>> v1 = pp.HigherOrderNode(n.edges['a-b'], uid='a-b')
        >>> v2 = pp.HigherOrderNode(n.edges['b-c'], uid='b-c')
        >>> v3 = pp.HigherOrderNode(n.edges['c-a'], uid='c-a')
        >>> v4 = pp.HigherOrderNode(n.edges['c-d'], uid='c-d')
        >>> v5 = pp.HigherOrderNode(n.edges['d-a'], uid='d-a')
        >>> n2.add_edge(v1, v2, uid='a-b-c', weight=1)
        >>> n2.add_edge(v2, v3, uid='b-c-a', weight=1)
        >>> n2.add_edge(v2, v4, uid='b-c-d', weight=0.2)
        >>> n2.add_edge(v3, v1, uid='c-a-b', weight=1)
        >>> n2.add_edge(v4, v5, uid='c-d-a', weight=0.2)
        >>> n2.add_edge(v5, v1, uid='d-a-b', weight=1)
        >>> rw = pp.processes.HigherOrderRandomWalk(n2, weight='weight')
        >>> data = rw.run_experiment(steps=10, runs=10)
        >>> rw.plot(data, run_id=3)
        [interactive visualization in first-order network]

        See Also:
        ---------
        TemporalNetwork, plot, RandomWalk, HigherOrderRandomWalk, EpidemicSIR
        """

        evolution: DataFrame = data.loc[data['run_id']==run_id]
        steps = evolution.max()['time']
        
        # create network with temporal attributes
        tn = TemporalNetwork(directed=self.network.directed)        
        for v in self._first_order_network.nodes:
            tn.add_node(TemporalNode(v.uid))
        for e in self._first_order_network.edges:
            tn.add_edge(e.v.uid, e.w.uid, start=0, end=steps*timescale)

        # set initial state
        for v in tn.nodes.uids:
            tn.nodes[v][0, 'color'] = self.state_to_color(False)

        # update state
        for index, row in evolution.iterrows():
            higher_order_node = self._network.nodes[row['node']]
            first_order_node = higher_order_node.nodes[-1]
            tn.nodes[first_order_node.uid][row['time']*timescale, 'color'] = self.state_to_color(row['state'])
        return tn.plot(**kwargs)


    def get_path(self, data: DataFrame, run_id: Optional[int]=0) -> Path:
        """Returns a path that represents the sequence of (first-order) nodes traversed 
        by a single random walk.

        Parameters
        ----------

        data: DataFrame
            Pandas data frame containing the trajectory of one or more (higher-order) random walks, generated by a call of `run_experiment`

        run_uid: Optional[int]=0
               Uid of the random walk simulation to be returns as Path (default: 0).

        Returns
        -------

        Path
            Path object containing the sequence of nodes traversed by the random walk

        """
        # list of traversed nodes starting with seed node
        walk_steps = list(data.loc[(data['run_id']==run_id) & (data['state']==True)]['node'].values)        

        # for higher-order random walk, seed node is a higher-order node
        # consisting of one or more edges
        seed: HigherOrderNode = self._network.nodes[walk_steps[0]]
        walk = Path(seed.edges[0].v)
        for e in seed.edges:
            walk._path.append(e)

        # map higher-order nodes to first-order nodes
        for i in range(1, len(walk_steps)):
            v = walk_steps[i-1]
            w = walk_steps[i]
            traversed_higher_order_edge = self._network.edges[v, w]
            traversed_edge = traversed_higher_order_edge.w.edges[-1]
            walk._path.append(traversed_edge)
        
        return walk


    def get_paths(self, data: DataFrame, run_ids: Optional[Iterable]=None) -> PathCollection:
        """Returns a PathCollection where each 

        Parameters
        ----------

        data: DataFrame
            Pandas data frame containing the trajectory of one or more random walks, generated by 
            `run_experiment`

        run_uids: Optional[Iterable]=None
            Uids of the random walk simulations to be included in the PathCollection instance. If None (default), all random walk simulations will be included.

        Returns
        -------

        PathCollection
            PathCollection object where each random walk is represented by one Path instance in the collection.

        """
        
        if not run_ids: # generate paths for all run_ids in the data frame
            runs =data['run_id'].unique()
        else:
            runs = run_ids

        pc = PathCollection()
        for i in runs:
            pc.add(self.get_path(data, i))

        return pc