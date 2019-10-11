#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : edge.py -- Base class for an edge
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2019-10-11 08:57 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List, Dict
from copy import deepcopy
from collections import defaultdict

from .. import logger, config
from . import Node

# create logger for the Edge class
log = logger(__name__)


class Edge:
    """Base class for an edge."""

    def __init__(self, v: Node, w: Node, uid: str = None,
                 directed: bool = True, **kwargs: Any) -> None:
        """Initialize the edge object."""

        # Class of the Node object
        # TODO: Probably there is a better solution to have different Node
        # classes for different Edges sub classes
        self._node_class()

        # set unique identifier of the edge
        self._uid: str

        # inidcator whether the edge is directed or undirected
        self._directed: bool = directed

        # a dictionary containing node objects
        self._nodes: dict = defaultdict(dict)

        # dictionary for edge attributes
        self._attributes: dict = {}

        # add attributes to the edge
        self._attributes.update(kwargs)

        # use separator if given otherwise use config default value
        self.separator: str = kwargs.get('separator',
                                         config.get('edge', 'separator'))

        # check code
        self.check: bool = kwargs.get('check_code',
                                      config.getboolean('computation',
                                                        'check_code'))

        # add nodes
        self.add_nodes_from([v, w])

        # set source and target nodes
        self._v: Node = list(self.nodes.values())[0]
        self._w: Node = list(self.nodes.values())[-1]

        # set uid of the edge
        if uid is None:
            self._uid = self.v.uid + self.separator + self.w.uid
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

    def __setitem__(self, key: Any, value: Any) -> None:
        """Add a specific attribute to the edge.

        An attribute has a key and the corresponding value expressed as a pair,
        key: value.

        Parameters
        ----------
        key: Any
            Unique identifier for a corrisponding value.

        value: Any
            A value i.e. attribute which is associated with the edge.

        Examples
        --------
        Generate new edge.

        >>> from pathpy import Edge
        >>> vw = Edge('v', 'w')

        Add atribute to the edge.

        >>> vw['capacity'] = 5.5

        """
        self.attributes[key] = value

    def __getitem__(self, key: Any) -> Any:
        """Returns a specific attribute of the edge.

        Parameters
        ----------
        key: any
            Key value for the attribute of the edge.

        Returns
        -------
        any
            Returns the attribute of the edge associated with the given key
            value.

        Raises
        ------
        KeyError
            If no attribute with the assiciated key is defined.

        Examples
        --------
        Generate new edge with length 10

        >>> from pathpy import Edge
        >>> vw = Edge('v', 'w', length=10)

        Get the edge attribute.

        >>> vw[length]
        10

        """
        try:
            return self.attributes[key]
        except KeyError as error:
            log.error(
                'No attribute with key {} is defined!'.format(error))
            raise

    def __eq__(self, other: object) -> bool:
        """Returns True if two edges are equal, otherwise False."""
        return self.__dict__ == other.__dict__

    def __hash__(self) -> Any:
        """Returns the unique hash of the edge.

        Here the hash value is defined by the unique edge id!

        """
        return hash(self.uid)

    def __del__(self) -> None:
        """Delete the edge."""
        # update associated nodes
        self.v.outgoing.remove(self.uid)
        self.w.incoming.remove(self.uid)
        if not self.directed:
            self.v.incoming.remove(self.uid)
            self.w.outgoing.remove(self.uid)

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
    def attributes(self) -> Dict:
        """Return the attributes associated with the edge.

        Returns
        -------
        Dict
            Return a dictionary with the edge attributes.

        Examples
        --------
        Generate a single edge with a color attribute.

        >>> from pathpy import Edge
        >>> vw = Edge('v','w', color='red')

        Get the attributes of the edge.

        >>> vw.attributes
        {'color'='red'}

        """
        return self._attributes

    @property
    def nodes(self) -> Dict[str, Node]:
        """Return the associated nodes of the edge.

        Returns
        -------
        Dict[str,Node]
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
        return self._v

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
        return self._w

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
        if not isinstance(node, self.NodeClass) and self.check:
            node = self._check_node(node, **kwargs)

        # add node to the edge
        self.nodes[node.uid] = node

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
        # TODO: parallize this function
        for node in nodes:
            self.add_node(node, **kwargs)

    def _check_node(self, node: Any, **kwargs: Any) -> Node:
        """Helperfunction to check if the node is in the right format."""
        if isinstance(node, str):
            return self.NodeClass(node, **kwargs)
        else:
            log.error('The definition of the node "{}"'
                      ' is incorrect!'.format(node))
            raise AttributeError

    def update(self, **kwargs: Any) -> None:
        """Update the attributes of the edge.

        Parameters
        ----------
        kwargs : Any
            Attributes to add or update for the edge as key=value pairs.

        Examples
        --------
        Update attributes.

        >>> from pathpy import Edge
        >>> vw = Edge('v','w',length = 5)
        >>> vw.attributes
        {'length':5}

        Update attributes.

        >>> vw.update(length = 10, capacity = 5)
        >>> vw.attributes
        {'length':10, 'capacity':5}

        """
        self.attributes.update(kwargs)

    def copy(self) -> Edge:
        """Return a copy of the edge.

        Returns
        -------
        :py:class:`Edge`
            A copy of the edge.

        Examples
        --------
        >>> from pathpy import Edge
        >>> vw = Edge('v','w')
        >>> ab = vw.copy()
        >>> ab.uid
        'v-w'

        """
        return deepcopy(self)

    def weight(self, weight: str = 'weight') -> float:
        """Returns the weight of the edge.

        Per default the attribute with the key 'weight' is used as
        weight. Should there be no such attribute, a new one will be crated
        with weight = 1.0.

        If an other attribute should be used as weight, the option weight has
        to be changed.

        If a weight is assigned but for calculation a weight of 1.0 is needed,
        the weight can be disabled with False or None.

        Parameters
        ----------
        weight : str, optional (default = 'weight')
            The weight parameter defines which attribute is used as weight. Per
            default the attribute 'weight' is used. If `None` or `False` is
            chosen, the weight will be 1.0. Also any other attribute of the
            edge can be used as a weight

        Returns
        -------
        float
            Returns the attribute value associated with the keyword.

        Examples
        --------
        Create new edge and get the weight.

        >>> form pathpy import Edge
        >>> vw = Edge('v','w')
        >>> vw.weight()
        1.0

        Change the weight.

        >>> vw['weight'] = 4
        >>> vw.weight()
        4.0

        >>> vw.weight(False)
        1.0

        Add an attribute and use this as weight.

        >>> vw['length'] = 5
        >>> vw.weight('length')
        5.0

        """
        if weight is None:
            weight = False
        if not weight:
            return 1.0
        elif isinstance(weight, str) and weight != 'weight':
            return float(self.attributes.get(weight, 1.0))
        else:
            return float(self.attributes.get('weight', 1.0))


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
