"""Path class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py -- Base class for a path
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-05-03 17:37 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
# from typing import Any, Optional, Union
# from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9

from pathpy import logger
from pathpy.core.core import BasePath, BasePathCollection

# create logger for the Path class
LOG = logger(__name__)


class Path(BasePath):
    """Base class for a path."""

    def summary(self) -> str:
        """Returns a summary of the path. """
        summary = [
            'Uid:\t\t{}\n'.format(self.uid),
            'Type:\t\t{}\n'.format(self.__class__.__name__),
            'Directed:\t{}\n'.format(self.directed),
            'Nodes:\t\t{}\n'.format(self.relations),
        ]

        return ''.join(summary)


class PathCollection(BasePathCollection):
    """A collection of edges"""
    # pylint: disable=too-many-ancestors

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
