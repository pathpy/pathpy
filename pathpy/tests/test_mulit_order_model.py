#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_mulit_order_model.py -- Test environment for MOMs
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2021-06-01 19:11 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

from pathpy import PathCollection, MultiOrderModel, NullModel, HigherOrderNetwork


def test_basic():
    """Test basic functions."""

    paths = PathCollection()
    paths.add('a', 'c', 'd', count=20)
    paths.add('b', 'c', 'e', count=20)

    mom = MultiOrderModel.from_paths(paths, max_order=2)
    assert mom.predict() == 2

    paths = PathCollection()
    paths.add('a', 'c', 'd', count=5)
    paths.add('a', 'c', 'e', count=5)
    paths.add('b', 'c', 'e', count=5)
    paths.add('b', 'c', 'd', count=5)

    mom = MultiOrderModel.from_paths(paths, max_order=2)

    assert mom.predict() == 1

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
