#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : likelihoods.py -- Methods to calculate likelihoods
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2019-11-15 08:54 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List, Dict, Tuple, Optional
from functools import singledispatch
from collections import Counter
import datetime
import sys
from scipy import sparse
import numpy as np

from ... import config, logger, tqdm
from ...core.base import BaseNetwork, BaseHigherOrderNetwork


# create logger
_log = logger(__name__)


@singledispatch
def likelihood(self, observations: Any, log: bool = False) -> float:
    """Returns the likelihood given some observations."""


@likelihood.register(BaseHigherOrderNetwork)
def _hon(self, observations: Any, log: bool = False) -> float:
    """Returns the likelihood of a higher order network
    given some observations."""

    # some information for debugging
    _log.debug('I\'m a likelihood of a HigherOrderNetwork')

    # get a list of nodes for the matrix indices
    n = list(self.nodes.keys())

    # get the transition matrix
    T = self.transition_matrix(transposed=True)

    # generate hon network for the observed paths
    hon = self.from_network(observations, order=self.order)

    # initialize likelihood
    if log:
        likelihood = 0.0
        _path_likelihood = 0.0
    else:
        likelihood = 1.0
        _path_likelihood = 1.0

    # print(n)
    # print(hon.edges)
    # iterate over observed hon paths
    for path in hon.paths.values():

        # initial path likelihood
        path_likelihood = _path_likelihood

        # iterate over all edges in the hon path
        for e in path.as_edges:

            # calculate path likelihood
            if log:
                path_likelihood += np.log(T[n.index(path.edges[e].w.uid),
                                            n.index(path.edges[e].v.uid)])
            else:
                path_likelihood *= T[n.index(path.edges[e].w.uid),
                                     n.index(path.edges[e].v.uid)]

        # calculate likelihood
        if log:
            likelihood += path_likelihood * hon.paths.counter()[path.uid]
        else:
            likelihood *= path_likelihood ** hon.paths.counter()[path.uid]

    return likelihood


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
