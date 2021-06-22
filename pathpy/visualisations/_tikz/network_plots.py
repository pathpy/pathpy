"""Network plots with tikz"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network_plots.py -- Network plots with tikz
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2021-06-22 10:53 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations

from typing import Any


from pathpy import logger
from pathpy.visualisations._tikz.core import TikzPlot

# create logger
LOG = logger(__name__)


class NetworkPlot(TikzPlot):
    """Network plot class for a static network."""

    _kind = 'network'

    def __init__(self, data, **kwargs: Any):
        """Initialize network plot class"""
        super().__init__()
        self.data = data
        self.config = kwargs

    def to_tikz(self):
        """Converter to Tex"""
        return 'tikz'
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
