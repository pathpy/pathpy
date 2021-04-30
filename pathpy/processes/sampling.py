"""Classes for efficient random sampling from discrete distributions
"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : vose_sampling.py -- Class to sample from discrete distributions
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Wed 2021-04-28 01:59 ingo>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Union

import numpy as np

class VoseAliasSampling:
    """
    Implementation of fast biased sampling of discrete values [0, ..., n]
    
    For a concise explanation see https://www.keithschwarz.com/darts-dice-coins/

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

    >>> from pathpy.processes import VoseAliasSampling
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