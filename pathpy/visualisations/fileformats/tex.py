"""TEX plot."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : tex.py -- Module to create a tex file
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2020-05-05 14:54 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations  # remove for python 3.8
from string import Template

from typing import TYPE_CHECKING

from singledispatchmethod import singledispatchmethod  # remove for python 3.8

from pathpy import logger, config
from pathpy.visualisations.backends import Tikz
from pathpy.visualisations.utils import UnitConverter

# pseudo load class for type checking
if TYPE_CHECKING:
    from collections import defaultdict


# create logger
LOG = logger(__name__)


class TEX:
    """Class to draw html objects."""

    def __init__(self) -> None:
        """Initialize tex drawer"""
        self.tex: str = ''

    @singledispatchmethod
    def draw(self, backend, data: defaultdict) -> None:
        """Draw the object."""
        raise NotImplementedError

    @draw.register(Tikz)
    def _draw_tikz(self, backend: Tikz, data: defaultdict) -> None:
        LOG.debug('Draw tikz object as tex file')

        # generate default tex file with parameters
        tex = (
            '\\documentclass$class_options{standalone}\n'
            '\\usepackage[dvipsnames]{xcolor}\n'
            '\\usepackage{tikz-network}\n'
            '\\begin{document}\n'
            '\\begin{tikzpicture}\n'
            '\\tikzset{every node}=[font=\\sffamily\\bfseries]\n'
            '\\clip (0,0) rectangle ($width,$height);\n'
            '$tikz'
            '\\end{tikzpicture}\n'
            '\\end{document}'
        )

        # create function to convert the units to cm
        px2cm = UnitConverter('px', 'cm')

        # update the parameters
        self.tex = Template(tex).substitute(
            class_options=data['config'].get('latex_class_options', ''),
            width=px2cm(data['config']['width']),
            height=px2cm(data['config']['height']),
            tikz=backend.to_tex(data)
        )

    def save(self, filename: str) -> None:
        """Save the file"""
        with open(filename, 'w+') as new:
            new.write(self.tex)

    def show(self) -> None:
        """Show the object."""
        if config['environment']['interactive']:
            print(self.tex)
        else:
            print(self.tex)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
