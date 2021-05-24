"""HyperEdge class"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : hyperedge.py -- Base class for a hyperedge
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-05-24 10:50 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================

from typing import Any, Optional, Union

# from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9

from pathpy import logger
from pathpy.core.core import PathPyObject, PathPyPath  # , PathPyCollection

# create logger for the Path class
LOG = logger(__name__)


class HyperEdge(PathPyPath):
    """Base class for a hyperedge.  """

    def __init__(self, *nodes: Union[str, PathPyObject],
                 uid: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the node object."""

        # initialize the parent class
        super().__init__(*nodes, uid=uid, directed=False, ordered=False, **kwargs)

    @property
    def nodes(self) -> dict:
        """Return the nodes of the edge."""
        return self.objects

    def summary(self) -> str:
        """Returns a summary of the edge. """
        summary = [
            'Uid:\t\t{}\n'.format(self.uid),
            'Type:\t\t{}\n'.format(self.__class__.__name__),
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
