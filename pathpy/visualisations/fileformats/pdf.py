"""PDF plot."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : pdf.py -- Module to create a pdf file
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2020-04-21 09:12 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations  # remove for python 3.8

import os
import time
import shutil
import tempfile
import subprocess
import webbrowser

from typing import TYPE_CHECKING, Tuple
from singledispatchmethod import singledispatchmethod  # remove for python 3.8

from pathpy import logger, config
from pathpy.visualisations.backends import Tikz
from pathpy.visualisations.fileformats import TEX


# pseudo load class for type checking
if TYPE_CHECKING:
    from collections import defaultdict


# create logger
LOG = logger(__name__)


class PDF:
    """Class to draw html objects."""

    def __init__(self):
        """Initialize tex drawer"""
        self.figure = None
        self.filename: str = None

    @singledispatchmethod
    def draw(self, backend, data: defaultdict) -> None:
        """Draw the object."""
        raise NotImplementedError

    @draw.register(Tikz)
    def _draw_tikz(self, backend: Tikz, data: defaultdict) -> None:
        LOG.debug('Draw tikz object as pdf file')
        self.figure = TEX()
        self.figure.draw(backend, data)

    def save(self, filename: str) -> None:
        """Save the file"""
        temp_dir, temp_file = self.compile()

        # create temp file name
        temp_filename = os.path.join(temp_dir, temp_file)

        # Copy a file with new name
        shutil.copy(temp_filename, filename)

        # remove the temporal directory
        shutil.rmtree(temp_dir)

    def compile(self) -> Tuple[str, str]:
        """Show the object."""

        # basename
        basename = 'default'
        # get current directory
        current_dir = os.getcwd()

        # get temporal directory
        temp_dir = tempfile.mkdtemp()

        # change to output dir
        os.chdir(temp_dir)

        # save the tex file
        self.figure.save(basename + '.tex')

        # latex compiler
        command = ['latexmk', '--pdf', '-shell-escape',
                   '--interaction=nonstopmode',
                   basename + '.tex']

        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT)
        except Exception:
            # If compiler does not exist, try next in the list
            LOG.error('No latexmk compiler found')
            raise AttributeError

        # change back to the current directory
        os.chdir(current_dir)

        # return the name of the folder and temp pdf file
        return (temp_dir, basename+'.pdf')

    def show(self) -> None:
        """Show the object."""
        temp_dir, temp_file = self.compile()

        # create temp file name
        filename = os.path.join(temp_dir, temp_file)

        if config['environment']['interactive']:
            from IPython.display import IFrame, display
            # open the file in the notebook
            display(IFrame(filename, width=600, height=300))
        else:
            # open the file in the webbrowser
            webbrowser.open(r'file:///'+filename)

        # Wait for .1 second before temp file is deleted
        time.sleep(.1)

        # remove the temporal directory
        shutil.rmtree(temp_dir)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
