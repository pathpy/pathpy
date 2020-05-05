"""Algorithms to bend the edges."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : bending.py -- Algorithms to bend the edges
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2020-05-05 14:23 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

import numpy as np


def bend_factor(curved):
    """Calculate the bend factor for curved edges."""
    bend = 0

    if curved != 0:
        v1 = np.array([0, 0])
        v2 = np.array([1, 1])
        v3 = np.array([(2*v1[0]+v2[0]) / 3.0 - curved * 0.5 * (v2[1]-v1[1]),
                       (2*v1[1]+v2[1]) / 3.0 +
                       curved * 0.5 * (v2[0]-v1[0])
                       ])
        vec1 = v2-v1
        vec2 = v3 - v1
        angle = np.rad2deg(np.arccos(
            np.dot(vec1, vec2) / np.sqrt((vec1*vec1).sum()) / np.sqrt((vec2*vec2).sum())))
        bend = np.round(
            np.sign(curved) * angle * -1, 4)
    return bend


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
