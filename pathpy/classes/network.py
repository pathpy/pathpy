#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py -- Base class for a network
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2019-09-09 16:39 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, TypeVar
from copy import deepcopy
from collections import defaultdict

from .. import logger
from . import Node
from . import Edge

# create logger for the Edge class
log = logger(__name__)

# create multi type for Nodes
NodeType = TypeVar('NodeType', Node, str)
EdgeType = TypeVar('EdgeType', Edge, str)
WeightType = TypeVar('WeightType', str, None, float, int)


class Network(object):
    """Base class for a network."""

    def __init__(self, directed: bool = True, **kwargs: Any) -> None:
        """Initialize the network object."""

        # inidcator whether the network is directed or undirected
        self._directed = directed

        # dictionary for network attributes
        self.attributes: dict = {}

        # add attributes to the network
        self.attributes.update(kwargs)

        # a dictionary containing node objects
        self.nodes = defaultdict(dict)

        # a dictionary containing edge objects
        self.edges = defaultdict(dict)

        # Classes of the Node and Edge objects
        # TODO: Probably there is a better solution to have different Node and
        # Edge classes for different Network sub classes
        self._node_class()
        self._edge_class()

        pass

    def _node_class(self):
        """Internal function to assign different Node classes."""
        self.NodeClass = Node

    def _edge_class(self):
        """Internal function to assign different Edge classes."""
        self.EdgeClass = Edge

    def __repr__(self):
        """Return the description of the network (see :meth:`_desc`) with the id
        of the network."""
        return '<{} object {} at 0x{}x>'.format(self._desc(), self.name, id(self))

    def _desc(self):
        """Return a string *Network*."""
        return '{}'.format(self.__class__.__name__)

    def __getitem__(self, key):
        """Returns a specific attribute of the network."""
        try:
            return self.attributes[key]
        except Exception as error:
            log.error('No attribute with key "{}" is defined for network'
                      ' "{}".'.format(key, self.id))
            raise

    def __setitem__(self, key, item):
        """Add a specific attribute to the network"""
        self.attributes[key] = item

    @property
    def shape(self):
        """Return the size of the Network as tuple of number of nodes and number
        of edges"""
        return self.number_of_nodes(), self.number_of_edges()

    @property
    def directed(self):
        """Return if the network id directed (True) or undirected (False)."""
        return self._directed

    @property
    def name(self):
        """Return the name of the network if defined, else an empty space."""
        _name = self.attributes.get('name', '')
        if _name is None:
            _name = ''
        return _name

    @name.setter
    def name(self, s):
        """Set the name of the network."""
        self.attributes['name'] = s

    def __add__(self):
        pass
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
