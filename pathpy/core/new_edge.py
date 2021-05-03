"""Edge class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : edge.py -- Base class for an edge
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-05-03 15:50 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from typing import Any, Optional, Union

from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9

from pathpy import logger
from pathpy.core.classes import PathPyObject
from pathpy.core.path import BasePath, BasePathCollection
from pathpy.core.node import Node, NodeCollection

# create logger for the Path class
LOG = logger(__name__)


class Edge(BasePath):
    """Base class for an edge."""

    def __init__(self, v: Union[str, PathPyObject],
                 w: Union[str, PathPyObject],
                 uid: Optional[str] = None,
                 directed: bool = True,
                 **kwargs: Any) -> None:
        """Initialize the node object."""

        # initialize the parent class
        super().__init__(v, w, uid=uid, directed=directed, **kwargs)

    @property
    def v(self) -> Node:
        """Return the source node v uid of the edge. """
        # pylint: disable=invalid-name
        return self.objects[self.relations[0]]

    @property
    def w(self) -> Node:
        """Return the target node w uid of the edge. """
        # pylint: disable=invalid-name
        return self.objects[self.relations[-1]]

    @property
    def nodes(self) -> dict:
        """Return the nodes of the edge."""
        return self.objects

    def summary(self) -> str:
        """Returns a summary of the edge. """
        summary = [
            'Uid:\t\t{}\n'.format(self.uid),
            'Type:\t\t{}\n'.format(self.__class__.__name__),
            'Directed:\t{}\n'.format(self.directed),
            'Nodes:\t\t{}\n'.format(self.relations),
        ]

        return ''.join(summary)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
