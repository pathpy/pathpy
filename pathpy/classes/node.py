#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : node.py -- Base class for a node
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2019-10-01 11:46 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Set
from copy import deepcopy

from .. import logger

# create logger for the Node class
log = logger(__name__)


class Node(object):
    """Base class for a node.

    Parameters
    ----------

    Attributes
    ----------
    """

    def __init__(self, id: str, **kwargs: Any) -> None:
        """Initialize the node object."""

        # assign node identifier
        self._id = str(id)

        # node counter
        self._count = 1

        # dictionary for node attributes
        self.attributes: dict = {}

        # add attributes to the node
        self.attributes.update(kwargs)

        # set of incomming and outgoing edges
        self.outgoing: set = set()
        self.incoming: set = set()

    def __repr__(self) -> str:
        """Return the description of the node.

        Returns
        -------
        str
            Returns the description of the node with the class and assigned
            node id.

        Examples
        --------
        Genarate new node.

        >>> from pathpy import Node
        >>> u = Node('u')
        >>> print(u)

        """
        return '{} {}'.format(self._desc(), self.id)

    def _desc(self) -> str:
        """Return a string *Node*."""
        return '{}'.format(self.__class__.__name__)

    def __setitem__(self, key: Any, value: Any) -> None:
        """Add a specific attribute to the node.

        An attribute has a key and the corresponding value expressed as a pair,
        key: value.

        Parameters
        ----------
        key: Any
            Unique identifier for a corrisponding value.

        value: Any
            A value i.e. attribute which is associated with the node.

        Examples
        --------
        Generate new node.

        >>> from pathpy import Node
        >>> u = Node('u')

        Add atribute to the node.

        >>> u['color'] = 'blue'

        """
        self.attributes[key] = value

    def __getitem__(self, key: Any) -> Any:
        """Returns a specific attribute of the node.

        Parameters
        ----------
        key: any
            Key value for the attribute of the node.

        Returns
        -------
        any
            Returns the attribute of the node associated with the given key
            value.

        Raises
        ------
        KeyError
            If no attribute with the assiciated key is defined.

        Examples
        --------
        Generate new node with blue color

        >>> from pathpy import Node
        >>> u = Node('u', color='blue')

        Get the node attribute.

        >>> print(u['color'])
        """
        try:
            return self.attributes[key]
        except KeyError as error:
            log.error(
                'No attribute with key {} is defined!'.format(error))
            raise

    @property
    def id(self) -> str:
        """Return the id of the node.

        Returns
        -------
        str
            Return the node identifier as a string.

        Examples
        --------
        Generate a single node and print the id.

        >>> from pathpy import Node
        >>> u = Node('u)
        >>> print(u.id)

        """
        return self._id

    @property
    def adjacent_edges(self) -> Set[str]:
        """Returns the set of adjacent edges.

        Returns
        -------
        Set[str]
            Returns a set of adjacent edge ids as string values.
            I.e. all edges that share this node.
        """
        return self.incoming.union(self.outgoing)

    @property
    def count(self) -> int:
        """Return a count how often the node is observed.

        Returns
        -------
        int
            Returns an intiger value of the count property.

        Examples
        --------
        Generate a single node and return the count value.

        >>> from pathpy import Node
        >>> u = Node('u')
        >>> print(u.count)
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
        Generate a single node and increase the count at 1.

        >>> from pathpy import Node
        >>> u = Node('u')
        >>> u.count += 1
        >>> print(u.count)
        2

        Reduce the counter at 1.

        >>> u.count -= 1
        >>> print(u.count)
        1

        Set the counter to an arbitrary value.

        >>> u.count = 33
        >>> print(u.count)
        33

        """
        self._count = value

    def update(self, **kwargs: Any) -> None:
        """Update the attributes of the node.

        Parameters
        ----------
        kwargs : Any
            Attributes to add or update for the node as key=value pairs.

        Examples
        --------
        Update attributes.

        >>> from pathpy import Node
        >>> u = Node('u',color='red')
        >>> u.update(color='green',shape='rectangle')

        """
        self.attributes.update(kwargs)

    def copy(self) -> Node:
        """Return a copy of the node.

        Returns
        -------
        :py:class:`Node`
            A copy of the node.

        Examples
        --------
        >>> from pathpy import Node
        >>> u = Node('u')
        >>> v = u.copy()

        """
        return deepcopy(self)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
