#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : edge.py -- Base class for an edge
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2019-10-01 11:38 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, TypeVar
from copy import deepcopy

from .. import logger
from . import Node

# create logger for the Edge class
log = logger(__name__)

# create multi type for Nodes
NodeType = TypeVar('NodeType', Node, str)
WeightType = TypeVar('WeightType', str, None, float, int)


class Edge(object):
    """Base class for an edge."""

    def __init__(self, id: str, v: NodeType, w: NodeType,
                 directed: bool = True, **kwargs: Any) -> None:
        """Initialize the edge object."""

        # Class of the Node object
        # TODO: Probably there is a better solution to have different Node
        # classes for different Edges sub classes
        self._node_class()

        # assign edge identifier
        self._id = str(id)

        # node id for node v
        self._v = v

        # node id for node w
        self._w = w

        # edge counter
        self._count = 1

        # inidcator whether the edge is directed or undirected
        self._directed = directed

        # dictionary for edge attributes
        self.attributes: dict = {}

        # add attributes to the edge
        self.attributes.update(kwargs)

        # check type of the nodes and add new nodes
        if not isinstance(v, self.NodeClass):
            self._v = self.NodeClass(v)
        if not isinstance(w, self.NodeClass):
            self._w = self.NodeClass(w)

    def _node_class(self) -> Node:
        """Internal function to assign different Node classes to the edge"""
        self.NodeClass = Node

    def __repr__(self) -> str:
        """Return the description of the edge.

        Returns
        -------
        str
            Returns the description of the edge with the class and assigned
            edge id.

        Examples
        --------
        Genarate new edge
        >>> from pathpy import Edge
        >>> vw = Edge('vw','v','w')
        >>> print(vw)

        """
        return '{} {}'.format(self._desc(), self.id)

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
        Generate new node.

        >>> from pathpy import Edge
        >>> vw = Edge('vw', 'v', 'w')

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
        >>> vw = Edge('vw', 'v', 'w', length=10)

        Get the edge attribute.

        >>> print(vw['length'])

        """
        try:
            return self.attributes[key]
        except KeyError as error:
            log.error(
                'No attribute with key {} is defined!'.format(error))
            raise

    @property
    def id(self) -> str:
        """Return the id of the edge.

        Returns
        -------
        str
            Return the edge identifier as a string.

        Examples
        --------
        Generate a single edge and print the id.

        >>> from pathpy import Edge
        >>> vw = Edge('vw','v','w')
        >>> print(vw.id)

        """
        return self._id

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
        >>> vw = Edge('vw','v','w')
        >>> print(vw.v)

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
        >>> vw = Edge('vw','v','w')
        >>> print(vw.w)

        """

        """Return the target node w of the edge"""
        return self._w

    @property
    def directed(self) -> bool:
        """Return if the edge is directed (True) or undirected (False)."""
        return self._directed

    @property
    def count(self) -> int:
        """Return a count how often the edge is observed.

        Returns
        -------
        int
            Returns an intiger value of the count property.

        Examples
        --------
        Generate a single edge and return the count value.

        >>> from pathpy import Edge
        >>> vw = Edge('vw','v','w')
        >>> print(vw.count)
        1

        """
        return self._count

    @count.setter
    def count(self, value: int) -> None:
        """Set,increase or decrease counter.

        Parameters
        ----------
        value : int
            Value of the counter.

        Examples
        --------
        Generate a single edge and increase the count at 1.

        >>> from pathpy import Edge
        >>> vw = Edge('vw','v','w')
        >>> vw.count += 1
        >>> print(vw.count)
        2

        Reduce the counter at 1.

        >>> vw.count -= 1
        >>> print(vw.count)
        1

        Set the counter to an arbitrary value.

        >>> vw.count = 33
        >>> print(vw.count)
        33

        """
        self._count = value

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
        >>> vw = Edge('vw,'v','w',length = 5)
        >>> vw.update(length = 10, capacity = 5)

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
        >>> vw = Edge('vw','v','w')
        >>> ab = vw.copy()

        """
        return deepcopy(self)

    def weight(self, weight: WeightType = 'weight') -> float:
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
        >>> vw = Edge('vw','v','w')
        >>> print(vw.weight())

        Change the weight.

        >>> vw['weight'] = 4
        >>> print(vw.weight())
        >>> print(vw.weight(False))

        Add an attribute and use this as weight.

        >>> vw['length'] = 5
        >>> print(vw.weight('length'))

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
