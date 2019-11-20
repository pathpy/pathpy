#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_likelihood.py -- Test environment for likelihood calculation
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2019-11-15 08:48 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

from pathpy import Path, Network, HigherOrderNetwork, NullModel


def test_likelihood():
    """Test likelihood for higher order networks."""
    p1 = Path('a', 'c', 'd', frequency=2)
    p2 = Path('b', 'c', 'e', frequency=2)

    net = Network(p1, p2)

    hon = HigherOrderNetwork(net, order=2)

    # print(hon.transition_matrix())

    hon.likelihood(net)

    null = NullModel(net)

    n2 = null.generate(2)
    n2.likelihood(net)


def test_likelihood_2():
    p = Path('a', 'b', 'c', 'd', 'e', 'c', 'b', 'a',
             'c', 'd', 'e', 'c', 'e', 'd', 'c', 'a', frequency=1)
    # p = Path('a', 'b', 'a', 'b', 'c', 'a', 'c')
    net = Network(p)

    # hon_1 = HigherOrderNetwork(net, order=1)
    null = NullModel(net)
    # n2 = null.generate(2)
    n5 = null.generate(5)

    # n5.summary()

    # print(n5.adjacency_matrix())
    # print(n5.transition_matrix())
    # print(n5.adjacency_matrix())

    # n5.subpaths.summary()
    # print(s)

    # print(net.adjacency_matrix(weight='frequency'))
    # print('xxxxxxxxxx')
    # print(net.transition_matrix(weight='frequency'))
    # hon_1.subpaths.summary()
    # hon_1.likelihood(net, log=False)
    # n2.likelihood(net, log=False)
    # print(n5.transition_matrix(transposed=True))
    # for e in n5.edges.values():
    #     print(e.uid)
    # n5.likelihood(net, log=False)
    # print(n2)
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
