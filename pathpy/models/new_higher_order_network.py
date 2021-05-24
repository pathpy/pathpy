"""Higher-order network class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : higher_order_network.py -- Basic class for a HON
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2021-05-24 13:13 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from typing import Any, Optional, Union

from pathpy import logger
from pathpy.core.edge import Edge, EdgeCollection
from pathpy.core.path import Path, PathCollection
from pathpy.models.classes import BaseHigherOrderNetwork
from pathpy.models.network import Network
# create logger for the Network class
LOG = logger(__name__)


class HigherOrderNode(Path):
    """Base class of a higher-order node."""

    @property
    def order(self):
        "Return the order of the higher-oder node"
        return len(self)


class HigherOrderNodeCollection(PathCollection):
    """A collection of edges"""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the EdgeCollection object."""

        # initialize the base class
        super().__init__(*args, **kwargs)

        # class of objects
        self._default_class: Any = HigherOrderNode


class HigherOrderEdge(Edge):
    """Base class of an higher-order edge."""


class HigherOrderEdgeCollection(EdgeCollection):
    """A collection of edges"""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the EdgeCollection object."""

        # initialize the base class
        super().__init__(*args, **kwargs)

        # class of objects
        self._default_class: Any = HigherOrderEdge


class HigherOrderNetwork(BaseHigherOrderNetwork, Network):
    """Base class for a Higher Order Network (HON)."""

    def __init__(self, uid: Optional[str] = None, order: int = 1,
                 **kwargs: Any) -> None:
        """Initialize the higer-order network object."""

        # initialize the base class
        super().__init__(uid=uid, directed=True, multiedges=False, **kwargs)

        # order of the higher-order network
        self._order: int = order

        # a container for node objects
        self._nodes: Any = HigherOrderNodeCollection()

        # a container for edge objects
        self._edges: Any = HigherOrderEdgeCollection()

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
