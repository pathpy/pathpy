"""Degree statistics."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : degrees.py -- Module to calculate degree-based statistics
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Mon 2020-04-20 09:09 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Union, Dict, Tuple
from collections import defaultdict
from collections.abc import Iterable

import numpy as np

from pathpy import logger
from pathpy.core.network import BaseModel

# pseudo load class for type checking
if TYPE_CHECKING:
    from pathpy.core.network import Network

# create custom types
Weight = Union[str, bool, None]

# create logger
LOG = logger(__name__)


def degree_sequence(network: Network, weight: Weight = None) -> np.array:
    """Calculates the degree sequence of a network.

    Parameters
    ----------

    network : Network

        The :py:class:`Network` object that contains the network

    weights : bool

        If True weighted degrees will be calculated

    Examples
    --------
    Generate a simple network

    >>> import pathpy as pp
    >>> net = pp.Network(directed=False)
    >>> net.add_edge('a', 'b', weight = 2.1)
    >>> net.add_edge('a', 'c', weight = 1.0)
    >>> s = pp.algorithms.statistics.degrees.degree_sequence(net)
    >>> s
    np.array([2., 1., 1.])

    Return weighted degree sequence
    >>> s = pp.algorithms.statistics.degrees.degree_sequence(net,weight=True)
    >>> s
    array([3.1, 2.1, 1.0])
    """
    _degrees = np.zeros(network.number_of_nodes(), dtype=float)
    for v in network.nodes.uids:
        _degrees[network.nodes.index[v]] = network.degrees(weight=weight)[v]
    return _degrees


def degree_distribution(degrees: Union[Network, Iterable],
                        weight: Weight = None) -> Dict[float, float]:
    """Calculates the degree distribution of a network.

    Parameters
        ----------
        degrees : Network or Iterable

            :py:class:`Network` object that contains the network for which 
            the degree distribution shall be calculated or a degree sequence 
            of the network

        weights : bool
    
            If True the weighted degree distribution will be calculated

        Examples
        --------
        Generate a simple network

        >>> import pathpy as pp
        >>> net = pp.Network(directed=False)
        >>> net.add_edge('a', 'b', weight = 2.1)
        >>> net.add_edge('a', 'c', weight = 1.0)
        >>> s = pp.algorithms.statistics.degree_distribution(net)
        >>> s
        dict({ 2.: 0.33333., 1.: 0.66667})

        Return weighted degree distribution

        >>> s = pp.algorithms.statistics.degree_distribution(net, weights = True)
        >>> s
        dict({ 3.1: 0.33333., 2.1: 0.33333., 1.: 0.333333. })

        Return degree distribution for degree sequence

        >>> s = pp.algorithms.statistics.degree_distribution([1,2,3])
        >>> s
        dict({ 1.: 0.33333., 2.: 0.33333., 3.: 0.333333. })
    """

    assert isinstance(degrees, (BaseModel, Iterable)), \
        "degrees can only be Network instance or Iterable that contains degree sequence"

    cnt: defaultdict = defaultdict(float)
    if isinstance(degrees, BaseModel):
        n = degrees.number_of_nodes()
        for v in degrees.nodes.uids:
            cnt[degrees.degrees(weight=weight)[v]] += 1.0 / n
    else:
        n = len(degrees)
        for d in degrees:            
            cnt[d] += 1.0 / n

    return cnt


def mean_degree(network, weight: Weight = None) -> float:
    """Calculates the mean (weighted degree of a network)
    """
    return degree_raw_moment(network, k=1, weight=weight)


def mean_neighbor_degree(network, weight: Weight = None, exclude_neighbor = False) -> float:
    """Calculates the mean (weighted degree of a network)
    """
    neighbor_degrees = []
    for v in network.nodes.uids:
        for w in network.successors[v]:
            if exclude_neighbor:
                neighbor_degrees.append(network.degrees(weight=weight)[w.uid] - 1)
            else:
                neighbor_degrees.append(network.degrees(weight=weight)[w.uid])
    return np.mean(neighbor_degrees)


def degree_raw_moment(network: Network, k: int = 1,
                      weight: Weight = None) -> float:
    """Calculates the k-th raw moment of the degree distribution of a network

    Parameters
    ----------

    network :  Network

        The network in which to calculate the k-th raw moment

    """
    p_k = degree_distribution(network, weight = weight)
    mom = 0.
    for x in p_k:
        mom += x**k * p_k[x]
    return mom


def degree_central_moment(network: Network, k: int = 1,
                          weight: Weight = None) -> float:
    """Calculates the k-th central moment of the degree distribution.

    Parameters
    ----------

    network :  Network

        The network in which to calculate the k-th central moment

    """
    p_k = degree_distribution(network, weight=weight)
    mean = np.mean(degree_sequence(network))
    m = 0.
    for x in p_k:
        m += (x - mean)**k * p_k[x]
    return m


def degree_generating_function(degrees: Union[Network, Iterable], x: Union[float, list, np.ndarray],
                               weight: Weight = None) -> Union[float, np.ndarray]:
    """Returns the generating function of the (weighted) degree distribution of a network, 
        calculated for either a single value or an Iterable of values


    Returns f(x) where f is the probability generating function for the degree
    distribution P(k) for a network. The function is defined in the interval
    [0,1].  The value returned is from the range [0,1]. The following properties
    hold:

    [1/k! d^k/dx f]_{x=0} = P(k)
    with d^k/dx f being the k-th derivative of f by x

    f'(1) = <k>
    with f' being the first derivative and <k> the mean degree

    [(x d/dx)^m f]_{x=1} = <k^m>
    with <k^m> being the m-th raw moment of P

    Parameters
    ----------
    degrees: Network, np.array
        The Network or degree sequence for which the generating function
        shall be computed

    x:  float, list, numpy.ndarray
        The argument(s) for which value(s) f(x) shall be computed.

    Returns
    -------
        Either a single float value f(x) (if x is float) or a numpy.array
        containing function values f(x) for all values in x

    Example
    -------
    Generate simple network

    >>> import pathpy as pp
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> n = pp.Network()
    >>> n.add_edge('a', 'b')
    >>> n.add_edge('b', 'c')
    >>> n.add_edge('a', 'c')
    >>> n.add_edge('c', 'd')
    >>> n.add_edge('d', 'e')
    >>> n.add_edge('d', 'f')
    >>> n.add_edge('e', 'f')

    Return single function value

    >>> val = pp.statistics.degrees.generating_func(n, 0.3)
    >>> print(val)
    0.069

    Plot generating function of degree distribution

    >>> x = np.linspace(0, 1, 20)
    >>> y = pp.statistics.degrees.generating_func(n, x)
    >>> x = plt.plot(x, y)
    [Function plot]

    Plot generating function based on degree sequence

    >>> x = np.linspace(0, 1, 20)
    >>> y = pp.statistics.degrees.generating_func([1,2,1,2], x)
    >>> x = plt.plot(x, y)
    [Function plot]

    """

    assert isinstance(x, (float, list, np.ndarray)), \
        'x can only be float, list or numpy.array'

    assert isinstance(degrees, (BaseModel, Iterable)), \
        'degrees can only be Network or Iterable'
    
    p_k = degree_distribution(degrees, weight=weight)

    if isinstance(x, float):
        x_range = [x]
    else:
        x_range = x

    values: defaultdict = defaultdict(float)
    for k in p_k:
        for v in x_range:
            values[v] += p_k[k] * v**k

    _values: Union[float, np.ndarray]
    if len(x_range) > 1:
        _values = np.fromiter(values.values(), dtype=float)
    else:
        _values = values[x]
    return _values


def molloy_reed_fraction(network: Network, weight: Weight = False) -> float:
    """Calculates the Molloy-Reed fraction.

    Calculates the Molloy-Reed fraction k**2/<k> based on the (in/out)-degree
    distribution of a directed or undirected network.

    Parameters
    ----------

    network : Network

        The network in which to calculate the Molloy-Reed fraction

    """
    _mrf = (degree_raw_moment(network, k=2, weight=weight) /
            degree_raw_moment(network, k=1, weight=weight))
    return _mrf


def degree_assortativity(network: Network, mode: str = 'in', weight: Weight = None) -> float:
    """Calculates the degree assortativity coefficient of a network.

    Parameters
    ----------

    network : Network

        The network in which to calculate the Molloy-Reed fraction
    """
    A = network.adjacency_matrix(weight=weight)
    m = np.sum(A)
    
    d = network.degrees(weight)
    if network.directed and mode == 'in':
        d = network.indegrees(weight)
    elif network.directed and mode == 'out':
        d = network.outdegrees(weight)
    elif not network.directed:
        m = m/2.
    idx = network.nodes.index

    cov: float = 0.
    var: float = 0.
    for i in network.nodes.keys():
        for j in network.nodes.keys():
            cov += (A[idx[i], idx[j]] - (d[i]*d[j])/(2*m)) * d[i] * d[j]
            if i != j:
                var -= (d[i]*d[j])/(2*m) * d[i] * d[j]
            else:
                var += (d[i] - (d[i]*d[j])/(2*m)) * d[i] * d[j]
    return cov/var
