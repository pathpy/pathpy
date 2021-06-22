#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : core.py -- Plots with d3js
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2021-06-22 13:43 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations

from typing import Any

from pathpy import logger
from pathpy.visualisations.new_plot import PathPyPlot

# create logger
LOG = logger(__name__)


class MatplotlibPlot(PathPyPlot):
    """Base class for plotting matplotlib objects"""

    def generate(self):
        """Function to generate the plot"""
        raise NotImplementedError

    def save(self, filename: str, **kwargs: Any) -> None:
        """Function to save the plot"""
        raise NotImplementedError

    def show(self, **kwargs: Any) -> None:
        """Function to show the plot"""
        raise NotImplementedError


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
