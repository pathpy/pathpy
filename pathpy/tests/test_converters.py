#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_converters.py -- Test environment for pathpy converters
# Author    : Ingo Scholtes <scholtes@ifi.uzh.ch>
# Time-stamp: <Tue 2021-05-25 18:42 ingo>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================



# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
import pathpy as pp


def test_to_networkx():
    network = pp.Network()
    network.add_edge("a", "b")
    n = pp.converters.to_networkx(network)