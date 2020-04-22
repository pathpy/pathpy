"""HTML plot."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : html.py -- Module to create a html file
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2020-04-22 19:34 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations  # remove for python 3.8

import webbrowser
import tempfile

from typing import TYPE_CHECKING
from singledispatchmethod import singledispatchmethod  # remove for python 3.8

from pathpy import logger, config
from pathpy.visualisations.backends import D3js

# pseudo load class for type checking
if TYPE_CHECKING:
    from collections import defaultdict


# create logger
LOG = logger(__name__)


class HTML:
    """Class to draw html objects."""

    def __init__(self) -> None:
        """Initialize html drawer"""
        self.html: str = ''

    @singledispatchmethod
    def draw(self, backend, data: defaultdict) -> None:
        """Draw the object."""
        raise NotImplementedError

    @draw.register(D3js)
    def _draw_d3js(self, backend: D3js, data: defaultdict) -> None:
        LOG.debug('Draw d3js object as html file')
        self.html = backend.to_html(data)

    def save(self, filename: str) -> None:
        """Save the file"""
        with open(filename, 'w+') as new:
            new.write(self.html)

    def show(self) -> None:
        """Show the object."""

        if config['environment']['interactive']:
            from IPython.display import display_html

            display_html(self.html, raw=True)
        else:

            # create temporal file
            temp_file = tempfile.NamedTemporaryFile(delete=False)

            # save html
            self.save(temp_file.name)

            # open the file
            webbrowser.open(r'file:///'+temp_file.name)

            # close the file
            temp_file.close()


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
