"""Path class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py -- Base class for a path
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Sat 2021-05-01 17:30 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Optional, Union, cast
from collections import defaultdict
from collections.abc import MutableMapping

from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9

from pathpy import logger
from pathpy.core.classes import PathPyObject


class PathTuple(tuple):
    """Class to store directed and undirected relationships of path components."""
    def __new__(cls, args, **kwargs):
        """Create a new PathTuple object."""
        # pylint: disable=unused-argument
        return super(PathTuple, cls).__new__(cls, args)

    def __init__(self, _, directed=False):
        """ Initialize the new tuple class."""
        # pylint: disable=super-init-not-called
        # self._reversed = self[::-1]
        self.directed = directed

    def __hash__(self):
        return super().__hash__() if self.directed else super().__hash__() \
            + hash(self[::-1])

    def __eq__(self, other):
        return super().__eq__(other) if self.directed else super().__eq__(other) \
            or self[::-1] == other

    def __repr__(self):
        return super().__repr__() if self.directed else '|'+super().__repr__()[1:-1]+'|'


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
