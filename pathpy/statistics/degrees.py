#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : degrees.py -- Module to calculate degree-based statistics
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Thu 2020-04-02 17:04 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Union, Dict
from collections import defaultdict

import numpy as np

from pathpy.core.network import Network


def sequence(network: Network, weight: bool = False) -> np.array:
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
    >>> s = pp.algorithms.statistics.degrees.sequence(net)
    >>> s
    array([2., 1., 1.])

    Return weighted degree sequence

    >>> s = pp.algorithms.statistics.degrees.sequence(net, weights = True)
    >>> s
    array([3.1, 2.1, 1.0])
    """

    return np.fromiter(network.nodes.degrees(weight=weight).values(), dtype=float)


def distribution(network: Network, weight: bool = False) -> Dict:
    """Calculates the degree distribution of a network.

    Parameters
        ----------
        network : Network

            The :py:class:`Network` object that contains the network

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
    """

    cnt = defaultdict(float)
    n = network.number_of_nodes()
    for v in network.nodes:
        cnt[network.nodes.degrees(weight=weight)[v]] += 1.0 / n

    return cnt


def raw_moment(network, k: int = 1, weight: bool = False) -> float:
    """Calculates the k-th raw moment of the degree distribution of a network

    Parameters
    ----------

    network :  Network

        The network in which to calculate the k-th raw moment

    """
    p_k = distribution(network, weight=weight)
    mom = 0.
    for x in p_k:
        mom += x**k * p_k[x]
    return mom


def central_moment(network: Network, k: int = 1, weight: bool = False) -> float:
    """Calculates the k-th central moment of the degree distribution of a network

    Parameters
    ----------

    network :  Network

        The network in which to calculate the k-th central moment

    """
    p_k = distribution(network, weight=weight)
    mean = np.mean(sequence(network))
    m = 0.
    for x in p_k:
        m += (x - mean)**k * p_k[x]
    return m


def generating_func(network: Network, x: float, weight: bool = False) -> Union[float, np.ndarray]:
    """Returns f(x) where f is the probability generating function for the
    degree distribution P(k) for a network. The function is defined in the interval [0,1].
    The value returned is from the range [0,1]. The following properties hold:

    [1/k! d^k/dx f]_{x=0} = P(k)    with d^k/dx f being the k-th derivative of f by x
    f'(1) = <k>                     with f' being the first derivative and <k> the mean degree
    [(x d/dx)^m f]_{x=1} = <k^m>    with <k^m> being the m-th raw moment of P

    Parameters
    ----------
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

    Plot generating function

    >>> x = np.linspace(0, 1, 20)
    >>> y = pp.statistics.degrees.generating_func(n, x)
    >>> x = plt.plot(x, y)
    [Function plot]
    """

    assert isinstance(x, (float, list, np.ndarray)), \
        'Argument can only be float, list or numpy.array'

    p_k = distribution(network, weight=weight)

    if isinstance(x, float):
        x_range = [x]
    else:
        x_range = x

    values = defaultdict(float)
    for k in p_k:
        for v in x_range:
            values[v] += p_k[k] * v**k

    if len(x_range) > 1:
        return np.fromiter(values.values(), dtype=float)
    else:
        return values[x]


def molloy_reed_fraction(network: Network, weight: bool = False) -> float:
    """Calculates the Molloy-Reed fraction k**2/<k> based on the (in/out)-degree
    distribution of a directed or undirected network.

    Parameters
    ----------

    network : Network

        The network in which to calculate the Molloy-Reed fraction
    """
    return raw_moment(network, k=2, weight=weight)/raw_moment(network, k=1, weight=weight)


def assortativity(network: Network, weight: bool = False) -> float:
    """Calculates the degree assortativity coefficient of a network.

    Parameters
    ----------

    network : Network

        The network in which to calculate the Molloy-Reed fraction
    """
    m = network.number_of_edges()
    A = network.adjacency_matrix()
    idx = dict()
    i = 0
    for v in network.nodes:
        idx[v] = i
        i += 1

    cov = 0.
    var = 0.
    for i in network.nodes:
        for j in network.nodes:
            cov += (A[idx[i], idx[j]] - (network.nodes.degrees(weight)[i]*network.nodes.degrees(
                weight)[j])/(2*m)) * network.nodes.degrees()[i] * network.nodes.degrees()[j]
            if i != j:
                var -= (network.nodes.degrees(weight)[i]*network.nodes.degrees(weight)[j])/(
                    2*m) * network.nodes.degrees(weight)[i] * network.nodes.degrees(weight)[j]
            else:
                var += (network.nodes.degrees(weight)[i] - (network.nodes.degrees()[i]*network.nodes.degrees()[
                        j])/(2*m)) * network.nodes.degrees()[i] * network.nodes.degrees()[j]
    return cov/var
