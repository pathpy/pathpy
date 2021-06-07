#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py -- network plot of pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-06-07 17:18 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================

class PlanePlot:
    """Class with an empty Plot"""

    def __init__(self, data, **kwargs):
        self.data = data

        @property
        def _kind(self):
            """Specify kind str. Must be overridden in child class"""
            raise NotImplementedError

        def _make_plot(self):
            raise NotImplementedError


class NetworkPlot(PlanePlot):
    """Plot of a static network"""
    _kind = "network"

    def __init__(self, obj, **kwargs):
        self.data = 0

    def _make_plot(self):
        pass
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
