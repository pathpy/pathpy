#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : matrices.py -- Module to calculate various matrices
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2020-04-02 16:12 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List
from functools import singledispatch
from scipy import sparse
import numpy as np

from pathpy import config, logger, tqdm
from pathpy.core.base import (BaseNetwork,
                              BaseHigherOrderNetwork)


# create logger
LOG = logger(__name__)


@singledispatch
def adjacency_matrix(self, weight: str = 'weight', transposed: bool = False,
                     **kwargs: Any) -> sparse.coo_matrix:
    """Returns a sparse adjacency matrix of the network.

    By default, the entry corresponding to a directed link v->w is stored in
    row v and column w and can be accessed via A[v,w].

    Parameters
    ----------
    weight: bool, str or None, optional (default = None)
        The weight parameter defines which attribute is used as weight. Per
        default an un-weighted network is used, i.e. `None` or `False` is
        chosen, the weight will be 1.0. Any other attribute of the edge can be
        used as a weight. Hence if set to `None` or `False`, the function
        returns a binary adjacency matrix. If set to `True`, or any other
        attribute, the adjacency matrix entries will contain the weight of an
        edge.

    transposed: bool, optional (default = False)
        Whether to transpose the matrix or not.

    Returns
    -------
    scipy.sparse.coo_matrix
        Returns a space scipy matrix.

    Examples
    --------
    Generate simple network

    >>> from pathpy import Network
    >>> net = Network()
    >>> net.add_edges_from([('a', 'b'), ('b', 'c')])
    >>> net.adjacency_matrix().todense()
    [[0. 1. 0.]
     [0. 0. 1.]
     [0. 0. 0.]]

    The function can also be directly called from pathpy

    >>> import pathpy as pp
    >>> pp.adjacency_matrix(net).todense()
    [[0. 1. 0.]
     [0. 0. 1.]
     [0. 0. 0.]]

    .. todo::

        Add more examples

    """


@adjacency_matrix.register(BaseNetwork)
def _network(self, weight: Any = None, transposed: bool = False,
             **kwargs: Any) -> sparse.coo_matrix:
    """Returns a sparse adjacency matrix of the network."""

    # update weight if frequency is chosen
    if weight == config['attributes']['frequency']:

        # update edge properties with the current frequencies
        # TODO: find better solution to update frequencies
        for uid, frequency in self.edges.counter().items():
            self.edges[uid][weight] = frequency

    # return an adjacency matrix
    return _adjacency_matrix(self, weight, transposed)


@adjacency_matrix.register(BaseHigherOrderNetwork)
def _hon(self, weight: Any = None, transposed: bool = False,
         **kwargs: Any) -> sparse.coo_matrix:
    """Returns a sparse adjacency matrix of the higher order network."""

    # get additional information for HONs
    subpaths: bool = kwargs.get('subpaths', True)

    # get the appropriate weights
    if weight is None and subpaths:
        weight = config['attributes']['frequency']

        # update edge properties with the current frequencies
        # TODO: find better solution to update frequencies
        for uid, frequency in self.edges.counter().items():
            self.edges[uid][weight] = frequency

    elif weight is None and not subpaths:
        weight = 'observed'
        print('observed')

    # return an adjacency matrix
    return _adjacency_matrix(self, weight, transposed)


def _adjacency_matrix(self, weight: Any = None,
                      transposed: bool = False) -> sparse.csr_matrix:
    """Function to generate the adjacency matrix."""

    # initializing variables
    rows: List[int] = list()
    cols: List[int] = list()
    entries: List[float] = list()

    # iterate over the edges of the network
    for e_id, e in tqdm(self.edges.items(), desc='adj matrix'):

        # add notes if network is directed
        rows.append(self.nodes.index[e.v.uid])
        cols.append(self.nodes.index[e.w.uid])
        entries.append(e.weight(weight))

        # add additional nodes if not directed
        if not self.directed:
            rows.append(self.nodes.index[e.w.uid])
            cols.append(self.nodes.index[e.v.uid])
            entries.append(e.weight(weight))


    A = sparse.csr_matrix((entries, (rows, cols)))
    if transposed:
        return A.transpose()
    else:
        return A


# @singledispatch
def transition_matrix(self, weight: Any = None, transposed: bool = False,
                      **kwargs: Any) -> sparse.coo_matrix:
    """Returns a transition matrix of the network.

    The transition matrix is the matrix

    .. math::

        T = 1/D * A

    where `D` is a matrix with the node out degrees on the diagonal and `A`
    is the adjacency matrix of the network.

    Parameters
    ----------
    weight : string or None, optional (default=None)
       The name of an edge attribute that holds the numerical value used
       as a weight.  If None or False, then each edge has weight 1.

    Returns
    -------
    transition_matrix : scipy.sparse.coo_matrix
        Returns the transition matrix, corresponding to the network.

    """
    A = self.adjacency_matrix(weight=weight, transposed=False, **kwargs)

    # Ignore division by zero warning
    with np.errstate(divide='ignore'):
        D = sparse.diags(1/A.sum(axis=1).A1)

    # calculate transition matrix
    T = D*A

    # transpose matrix if needed
    if transposed:
        T = T.transpose()

    # return matrix if needed
    return T

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
