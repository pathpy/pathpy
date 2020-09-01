""""Directed Acyclic Graph class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : directed_acyclic_graph.py -- Network model for a DAG
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2020-09-01 12:41 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional, Union, cast

from pathpy import logger, config
from pathpy.core.node import Node, NodeCollection
from pathpy.core.edge import Edge, EdgeCollection
from pathpy.core.network import Network


class DirectedAcyclicGraph(Network):
    """Base class for a directed acyclic graph."""

    def __init__(self, uid: Optional[str] = None, multiedges: bool = False,
                 **kwargs: Any) -> None:
        """Initialize the directed acyclic graph."""

        # initialize the base class
        super().__init__(uid=uid, directed=True, multiedges=multiedges, **kwargs)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
