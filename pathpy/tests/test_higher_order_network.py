#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_higher_order_network.py -- Test environment for HONs
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2020-06-10 09:53 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

import pytest
from pathpy.models.higher_order_network import HigherOrderNetwork


def test_hon():
    """Default test for development"""
    print('test')
    hon = HigherOrderNetwork()
    hon.add_node('a')
    hon.add_node('b')
    hon.add_edge('a', 'b', uid='e1')
    print(hon)
    print(hon.nodes)
    print(hon.edges)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
