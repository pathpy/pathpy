#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_mulit_order_model.py -- Test environment for MOMs
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2020-01-14 15:29 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

from pathpy import Path, Network, HigherOrderNetwork, MultiOrderModel, NullModel


# def test_basic():
#     """Test basic functions."""

#     p1 = Path('a', 'c', 'd', frequency=2)
#     p2 = Path('b', 'c', 'e', frequency=2)

#     net = Network(p1, p2)

#     # net.summary()

#     mom = MultiOrderModel(net, max_order=2)
#     # print(mom.layers)


# def test_generate():
#     """Test to generate a MOM."""

#     p1 = Path('a', 'c', 'd', frequency=2)
#     p2 = Path('b', 'c', 'e', frequency=2)

#     net = Network(p1, p2)

#     hon = HigherOrderNetwork(net, order=2)
#     hon.summary()
#     # net.summary()

#     mom = MultiOrderModel(net, max_order=2)
#     mom.generate(max_order=2)

#     # print(mom.layers)

#     # mom.summary()


# def test_estimate():
#     """Test order estimation."""
#     p1 = Path('a', 'c', 'd', frequency=2)
#     p2 = Path('b', 'c', 'e', frequency=2)

#     net = Network(p1, p2)
#     mom = MultiOrderModel(net, max_order=2)
#     mom.generate(max_order=2)

#     mom.estimate()


def test_path_likelihood():
    """Test the path likelihood."""
    p1 = Path('a', 'c', 'b', frequency=1)
    p2 = Path('c', 'b', 'a')
    p3 = Path('a', 'b', 'a', 'c')

    po = Path('a', 'b', 'a', 'c', 'd', 'e', 'f', 'g')

    net = Network(p1, p2, p3, po)

    mum = MultiOrderModel(net, max_order=6)
    mum.generate(max_order=6)

    #hon = HigherOrderNetwork(net, order=6)
    null = NullModel(net)
    # print(hon.summary())

    pl = mum.path_likelihood(po, order=6, log=False)
    print('pl', pl)

    ll = mum.layer_likelihood(longer_paths=False, order=6)
    print('ll', ll)

    l = mum.likelihood(order=6)
    print('l', l)

    lrt = mum.likelihood_ratio_test(order=3)
    print(lrt)

    o = mum.estimate()
    # n2 = null(1)
    # print(n2.summary())
    # print('dof', null(2).degrees_of_freedom(mode='path'))

    # for e in n2.edges:
    #     print(e)
    # mum.prefixes(po, order=6)
    # mum.path_to_higher_order_edge_uids(po, order=6)

    # net = Network(po)
    # hon = HigherOrderNetwork(net, order=2)
    # for e in hon.edges.values():
    #     print(e.uid)
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
