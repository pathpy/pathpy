"""Module for base classes in the processes module."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : classes.py -- Base classes for processes
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Wed 2021-04-28 02:11 ingo>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
import abc
from pathpy.core.classes import BaseClass
from typing import Iterable, TYPE_CHECKING, Any, Optional, List, Dict, Tuple, Union, Set
from pathpy.core.api import Node
from pathpy.models.network import Network
from pathpy.models.temporal_network import TemporalNetwork, TemporalNode
from collections import defaultdict
from pandas import DataFrame

class BaseProcess:
    """Abstract base class for all implementations of discrete-time dynamical processes.
    """

    def __init__(self, network:Network):
        """initialize process."""
        self._network = network
        self.init(self.random_seed())

    @property
    def network(self) -> Network:
        return self._network 

    @abc.abstractmethod
    def init(self, seed: Any) -> None:
        """Abstract method to initialize the process with a given seed state."""

    @abc.abstractmethod
    def random_seed(self) -> Any:
        """Abstract method to generate a random seed state for the process."""

    @abc.abstractmethod
    def step(self) -> Iterable[str]:
        """Abstract method to simulate a single step of the process. Returns 
        an iterable of node uids whose state has been changed in this step."""

    @abc.abstractproperty
    def time(self) -> int:
        """Abstract property returning the current time."""

    @abc.abstractmethod
    def state_to_color(self, Any) -> Union[Tuple[int, int, int], str]:
        """Abstract method mapping node states to RGB colors or color names."""

    @abc.abstractmethod
    def node_state(self, v: str) -> Any:
        """Abstract method returning the current state of a given node."""

    def simulation_run(self, steps: int, seed: Optional[Any]=None) -> Tuple[int, Set[str]]:
        """Abstract generator method that initializes the process, runs a number of steps and yields a tuple consisting of the current time and the set of nodes whose state has changed in each step."""
        if seed == None:
            self.init(self.random_seed())
        else:
            self.init(seed)
        for _ in range(steps):
            ret = self.step()
            if ret is not None:
                yield self.time, ret
            else:
                return None

    def run_experiment(self, steps: int, runs: Optional[Union[int, Iterable[Any]]] = 1) -> DataFrame:
        """Perform one or more simulation runs of the process with a given number of steps."""

        # Generate initializations for different runs
        seeds: List=list()
        if type(runs) == int:
            for s in range(runs):
                seeds.append(self.random_seed())
        else:
            for s in runs:
                seeds.append(s)

        results = list()
        run_id: int = 0
        for seed in seeds:            
            
            # initialize seed state and record initial state
            self.init(seed)
            for v in self.network.nodes.uids:
                results.append({'run_id': run_id, 'seed': seed, 'time': self.time, 'node': v, 'state': self.node_state(v)})

            # simulate the given number of steps
            for time, updated_nodes in self.simulation_run(steps, seed):
                # record the new state of each changed node
                for v in updated_nodes:
                    results.append({'run_id': run_id, 'seed': seed, 'time': time, 'node': v, 'state': self.node_state(v)})
            run_id += 1

        return DataFrame.from_dict(results)


    def plot(self, data: DataFrame, run_id: int=0, timescale: Optional[int]=100, **kwargs):
        """
        Display an interactive plot of the evolution of a process based on a recorded simulation experiment
        """

        evolution: DataFrame = data.loc[data['run_id']==run_id]
        steps = evolution.max()['time']
        
        # create network with temporal attributes
        tn = TemporalNetwork(directed=self.network.directed)        
        for v in self.network.nodes:
            tn.add_node(TemporalNode(v.uid))
        for e in self.network.edges:
            tn.add_edge(e.v.uid, e.w.uid, start=0, end=steps*timescale)

        # set initial state
        for v in tn.nodes.uids:
            tn.nodes[v][0, 'color'] = self.state_to_color(self.node_state(v))

        # update state
        for index, row in evolution.iterrows():            
            tn.nodes[row['node']][row['time']*timescale, 'color'] = self.state_to_color(row['state'])
        return tn.plot(**kwargs)