""" Classes to simulate epidemic spreading on networks
"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : epidemic_spreading.py -- Classes implementing epidemic models in 
#               (higher-order) networks
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Wed 2021-04-28 18:51 ingo>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations
import abc
import operator

from typing import Any, Iterable, Optional, Union, Dict, Set, Tuple

from numpy import random

from pathpy.core.path import Path
from pathpy.core.path import PathCollection
from pathpy.models.network import Network
from pathpy.models.network import Node
from pathpy.models.network import Edge
import numpy as np
from .process import BaseProcess

class EpidemicSIR(BaseProcess):
    """Implementation of Susceptible-Infected-Removed (SIR) model for epidemic spreading.
    
    The SIR model is an epidemiological compartment model, in which the nodes are assigned to three 
    compartments `susceptible` (those nodes that have not been infected but can potentially be infected), 
    `infected` (those nodes that are currently infected and can infect others), and `recovered` (those who
    have been infected in the past but are not infectious anymore).

    Once a node is infected, it will remain infectious for a time span that is governed by the recovery time. In each time step, each node connected to an infectious node is infected with probability infection_prob.

    The basic reproduction number R0 of the process is given by the product of the recovery time and the infection probability.

    Parameters
    ----------

    network: Network
        The network on which to simulate the SIR process

    recovery_time: int
        number of steps after which a newly infected node will recover

    infection_prob: float
        probability that a susceptible node connected to an infected node is infected

    source: Optional[Node]
        source node that is initially infected

    Examples
    --------

    Create an SIR process on a network

    >>> import pathpy as pp
    >>> n = pp.generators.ER_np(500, 0.01)
    >>> sir = pp.processes.EpidemicSIR(n, 10, 0.25)
    >>> print(sir.R0)
    2.5

    """

    def __init__(self, network: Network, 
                        recovery_time: int,
                        infection_prob: float) -> None:
        """
        Constructor
        """       

        super().__init__(network)

        # Set model parameters
        self.infection_prob: float = infection_prob
        self.recovery_time: int = recovery_time


    def random_seed(self):
        return np.random.choice(list(self._network.nodes.uids))

    def init(self, seed):

        # Initialize compartments
        self.susceptible: Set[str] = set()
        self.infected: Set[str] = set()
        self.recovered: Set[str] = set()

        # infection times
        self.infection_times: Dict[str, int] = dict()
        self._time = 0

        # Set all nodes in network to susceptible   
        for v in self.network.nodes.uids:
            self.susceptible.add(v)
        
        self.infected.add(seed)
        self.infection_times[seed] = self.time
        self.susceptible.remove(seed)

    def step(self) -> Set[str]:
        """
        """
        newly_infected = set()
        newly_recovered = set()

        # identify recovered nodes
        for v in list(self.infected):
            if self._time-self.infection_times[v] > self.recovery_time:
                self.infected.remove(v)
                self.recovered.add(v)
                newly_recovered.add(v)
        
        # # stop of no infected or susceptible nodes are left
        # if not self.infected or not self.susceptible:
        #     return newly_recovered
        
        # infection of neighbors        
        for v in self.infected:
            for w in self.network.successors[v]:
                if w.uid in self.susceptible and random.uniform()<=self.infection_prob:
                    self.susceptible.remove(w.uid)
                    newly_infected.add(w.uid)            
        # update state and time of newly infected nodes
        for w in newly_infected:
            self.infection_times[w] = self.time
            self.infected.add(w)

        self._time += 1
        return newly_infected.union(newly_recovered)

    def node_state(self, v:str) -> int:
        if v in self.susceptible:
            return 0
        elif v in self.infected:
            return 1
        else:
            return 2

    def state_to_color(self, state) -> str:
        if state==0:
            return "blue"
        elif state==1:
            return "red"
        else:
            return "gray"
        
    @property
    def time(self) -> int:
        return self._time

    @property
    def R0(self) -> float:
        return self.infection_prob * self.recovery_time


