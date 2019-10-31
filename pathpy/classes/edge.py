#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : edge.py -- Base class for an edge
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-10-31 12:09 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List, Dict

from .. import logger
from .base import BaseClass
from .base import NodeDict
from .utils.separator import separator
from .utils._check_node import _check_node
from . import Node

# create logger for the Edge class
log = logger(__name__)


class Edge(BaseClass):
    """Base class for an edge."""

    def __init__(self, v: Node, w: Node, uid: str = None,
                 directed: bool = True, **kwargs: Any) -> None:
        """Initialize the edge object."""

        # initialize the base class
        super().__init__(**kwargs)

        # Class of the Node object
        # TODO: Probably there is a better solution to have different Node
        # classes for different Edges sub classes
        self._node_class()

        # set unique identifier of the edge
        self._uid: str

        # inidcator whether the edge is directed or undirected
        self._directed: bool = directed

        # a dictionary containing node objects
        self._nodes: NodeDict = NodeDict(dict)

        # use separator if given otherwise use config default value
        self.separator: dict = separator(mode='edge', **kwargs)

        # add attributes to the edge
        self.attributes.update(**kwargs)

        # add nodes
        self.add_nodes_from([v, w])

        # set source and target nodes
        self._v: str = list(self.nodes.values())[0].uid
        self._w: str = list(self.nodes.values())[-1].uid

        # set uid of the edge
        if uid is None:
            self._uid = self.v.uid + self.separator['edge'] + self.w.uid
        else:
            self._uid = uid

        # update associated nodes
        self.v.outgoing.add(self.uid)
        self.w.incoming.add(self.uid)
        if not self.directed:
            self.w.outgoing.add(self.uid)
            self.v.incoming.add(self.uid)

    def _node_class(self) -> None:
        """Internal function to assign different Node classes to the edge"""
        self.NodeClass = Node

    def __repr__(self) -> str:
        """Return the description of the edge.

        Returns
        -------
        str
            Returns the description of the edge with the class and assigned
            edge uid.

        Examples
        --------
        Generate new edge without dedicated uid

        >>> from pathpy import Node, Edge
        >>> vw = Edge(Node('v'),Node('w'))
        >>> vw
        Edge v-w

        """
        return '{} {}'.format(self._desc(), self.uid)

    def _desc(self) -> str:
        """Return a string *Edge()*."""
        return '{}'.format(self.__class__.__name__)

    def __hash__(self) -> Any:
        """Returns the unique hash of the edge.

        Here the hash value is defined by the unique edge id!

        """
        return hash(self.uid)

    def __del__(self) -> None:
        """Delete the edge."""
        # update associated nodes
        try:
            self.v.outgoing.remove(self.uid)
        except Exception:
            pass
        try:
            self.w.incoming.remove(self.uid)
        except Exception:
            pass

        if not self.directed:
            try:
                self.v.incoming.remove(self.uid)
            except Exception:
                pass
            try:
                self.w.outgoing.remove(self.uid)
            except Exception:
                pass

    @property
    def uid(self) -> str:
        """Return the unique id of the edge.

        Returns
        -------
        str
            Return the edge identifier as a string.

        Examples
        --------
        Generate a single edge and print the id.

        >>> from pathpy import Edge
        >>> vw = Edge('v','w')
        >>> vw.uid
        'v-w'

        """
        return self._uid

    @property
    def nodes(self) -> NodeDict:
        """Return the associated nodes of the edge.

        Returns
        -------
        NodeDict
            Return a dictionary with the :py:class:`Node` uids as key and the
            :py:class:`Node` objects as values, associated with the edge.

        Examples
        --------
        Generate a single edge with a color attribute.

        >>> from pathpy import Edge
        >>> vw = Edge('v','w', color='red')

        Get the nodes of the edge

        >>> vw.nodes
        {'v': Node v, 'w': Node w}

        """
        return self._nodes

    @property
    def v(self) -> Node:
        """Return the source node v of the edge.

        Returns
        -------
        :py:class:`Node`
            Retun the source :py:class:`Node` of the edge.

        Examples
        --------
        Generate a single edge and return the source node.

        >>> from pathpy import Edge
        >>> vw = Edge('v','w')
        >>> vw.v
        Node v

        """
        return self.nodes[self._v]

    @property
    def w(self) -> Node:
        """Return the target node w of the edge.

        Returns
        -------
        :py:class:`Node`
            Retun the target :py:class:`Node` of the edge.

        Examples
        --------
        Generate a single edge and return the target node.

        >>> from pathpy import Edge
        >>> vw = Edge('v','w')
        >>> vw.w
        Node w

        """
        return self.nodes[self._w]

    @property
    def directed(self) -> bool:
        """Return if the edge is directed (True) or undirected (False)."""
        return self._directed

    def add_node(self, node: Node, **kwargs: Any) -> None:
        """Add a single node to the edge.

        Parameters
        ----------
        node : :py:class:`Node`
            The :py:class:`Node` object, which will be added to the network.

        kwargs : Any, optional (default = {})
            Attributes assigned to the node as key=value pairs.

        Notes
        -----
        This function is only used internally. It can be used to consider
        hyperedges in a futher version of pathpy.

        """
        # check if the right object is provided.
        if self.check:
            node = _check_node(self, node, **kwargs)

        # add node to the edge
        self.nodes[node.uid] = node

        # update node counter
        self.nodes.increase_counter(node.uid, self.attributes.frequency)

    def add_nodes_from(self, nodes: List[Node], **kwargs: Any) -> None:
        """Add multiple nodes from a list.

        Parameters
        ----------
        nodes : List[Node]

            Nodes from a list of :py:class:`Node` objects are added to the
            edge.

        kwargs : Any, optional (default = {})
            Attributes assigned to all nodes in the list as key=value pairs.

        Notes
        -----
        This function is only used internally. It can be used to consider
        hyperedges in a futher version of pathpy.

        """
        # iterate over a list of nodes
        # TODO: parallelize this function
        for node in nodes:
            self.add_node(node, **kwargs)

    def inherit(self, other: Edge) -> None:
        """Inherit attributes and associated nodes from an other edge."""

        # get relations with the associated nodes
        self.v.incoming.union(other.v.incoming)
        self.v.outgoing.union(other.v.outgoing)
        self.w.incoming.union(other.w.incoming)
        self.w.outgoing.union(other.w.outgoing)

        # get the attributes
        self.attributes.update(**other.attributes.to_dict(history=False))


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
