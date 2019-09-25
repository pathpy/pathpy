#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : am.py -- Test am
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2019-09-25 14:29 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import List, Any
from functools import singledispatch
from scipy import sparse
from ..classes.base import DefaultNetwork


@singledispatch
def adjacency_matrix(self, weight: Any = None,
                     transposed: bool = False) -> sparse.coo_matrix:
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

    raise NotImplementedError('Unsupported class')


@adjacency_matrix.register(DefaultNetwork)
def _(self, weight: Any = None, transposed: bool = False) -> sparse.coo_matrix:
    """Returns a sparse adjacency matrix of the network.

    """
    # initializing variables
    row: List(float) = []
    col: List(float) = []
    data: List(float) = []

    # get a list of nodes for the matrix indices
    n = list(self.nodes.keys())

    # iterate over the edges of the network
    for e_id, e in self.edges.items():

        # add notes if network is directed
        row.append(n.index(e.v.id))
        col.append(n.index(e.w.id))

        # add additional nodes if not directed
        if not self.directed:
            row.append(n.index(e.w.id))
            col.append(n.index(e.v.id))

        # add weight
        data.append(e.weight(weight))

        # add weight for undirected edges
        if not self.directed:
            # exclude self loops
            if e.v.id != e.w.id:
                data.append(e.weight(weight))
            else:
                data.append(0.0)

    # generate scipy sparse matrix
    shape = (self.number_of_nodes(), self.number_of_nodes())
    A = sparse.coo_matrix((data, (row, col)), shape=shape).tocsr()

    if transposed:
        return A.transpose()
    return A


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
