"""Network plots with d3js"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network_plots.py -- Network plots with d3js
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2021-06-10 17:04 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from typing import Any, Optional
from pathpy.visualisations.new_plot import PathPyPlot


def network_plot(obj, filename: Optional[str] = None,
                 backend: Optional[str] = None, **kwargs: Any):
    """Plot a static network with d3js"""
    result = NetworkPlot(obj, **kwargs)
    return result


class NetworkPlot(PathPyPlot):
    """Base network plot"""

    def __init__(self, data, **kwargs):
        """Initialize network plot class"""
        self.data = data
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
