#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : core.py -- Plots with tikz
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2021-06-22 12:51 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations

import os

from typing import Any
from string import Template

from pathpy import logger
from pathpy.visualisations.new_plot import PathPyPlot

# create logger
LOG = logger(__name__)


class TikzPlot(PathPyPlot):
    """Base class for plotting d3js objects"""

    def __init__(self, **kwargs: Any):
        """Initialize plot class"""
        super().__init__()
        if kwargs:
            self.config = kwargs

    def generate(self):
        """Function to generate the plot"""
        raise NotImplementedError

    def save(self, filename: str, **kwargs: Any) -> None:
        """Function to save the plot"""
        if filename.endswith('tex'):
            with open(filename, 'w+') as new:
                new.write(self.to_tex())
        elif filename.endswith('pdf'):
            self.compile_pdf()
        else:
            raise NotImplementedError

    def show(self, **kwargs: Any) -> None:
        """Function to show the plot"""
        print(self.to_tex())

    def compile_pdf(self) -> None:
        """Compile pdf from tex."""
        raise NotImplementedError

    def to_tex(self) -> str:
        """Convert data to tex."""
        # get path to the pathpy templates
        template_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            os.path.normpath('_tikz/templates'))

        # get template files
        with open(os.path.join(template_dir, f"{self._kind}.tex")) as template:
            tex_template = template.read()

        # generate data
        data = self.to_tikz()

        # fill template with data
        tex = Template(tex_template).substitute(
            classoptions=self.config.get('latex_class_options', ''),
            width=self.config.get('width', '6cm'),
            height=self.config.get('height', '6cm'),
            tikz=data
        )

        return tex

    def to_tikz(self) -> str:
        """Converter data to tex"""
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
