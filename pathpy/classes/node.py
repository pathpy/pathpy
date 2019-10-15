#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : node.py -- Base class for a node
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2019-10-15 10:04 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Dict, Set
from copy import deepcopy

from .. import logger

# create logger for the Node class
log = logger(__name__)


class Node:
    """Base class for a node.

    .. todo::

        Add detailed documentation for the object.

    Parameters
    ----------

    Attributes
    ----------
    """

    def __init__(self, uid: str, **kwargs: Any) -> None:
        """Initialize the node object."""

        # assign node identifier
        self._uid: str = str(uid)

        # dictionary for node attributes
        self._attributes: dict = {}

        # add attributes to the node
        self._attributes.update(kwargs)

        # set of incoming and outgoing edges
        self._outgoing: set = set()
        self._incoming: set = set()

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
        Node u

        """
        return '{} {}'.format(self._desc(), self.uid)

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

        >>> u['color']
        'blue'

        """
        try:
            return self.attributes[key]
        except KeyError as error:
            log.error(
                'No attribute with key {} is defined!'.format(error))
            raise

    def __hash__(self) -> Any:
        """Returns the unique hash of the node.

        Here the hash value is defined by the unique node id!

        """
        return hash(self.uid)

    @property
    def uid(self) -> str:
        """Return the unique id of the node.

        Returns
        -------
        str
            Return the node identifier as a string.

        Examples
        --------
        Generate a single node and print the uid.

        >>> from pathpy import Node
        >>> u = Node('u')
        >>> print(u.uid)
        u

        """
        return self._uid

    @property
    def attributes(self) -> Dict:
        """Return the attributes associated with the node.

        Returns
        -------
        Dict
            Return a dictionary with the node attributes.

        Examples
        --------
        Generate a single node with a color attribute.

        >>> from pathpy import Node
        >>> u = Node('u', color='red')

        Get the attributes of the node.

        >>> u.attributes
        {'color'='red}

        """
        return self._attributes

    @property
    def outgoing(self) -> Set[str]:
        """Returns the outgoing edge uids of the node."""
        return self._outgoing

    @property
    def incoming(self) -> Set[str]:
        """Returns the incoming edge uids of the node."""
        return self._incoming

    @property
    def edges(self) -> Set[str]:
        """Returns the set of edge uids adjacent to the node.

        Returns
        -------
        Set[str]
            Returns a set of adjacent edge uids as string values.
            I.e. all edges that share this node.

        .. todo::

            Add an example for this function.


        """
        return self.incoming.union(self.outgoing)

    def update(self, **kwargs: Any) -> None:
        """Update the attributes of the node.

        Parameters
        ----------
        kwargs : Any
            Attributes to add or update for the node as key=value pairs.

        Examples
        --------
        Generate simple node with attribute.

        >>> from pathpy import Node
        >>> u = Node('u',color='red')
        >>> u.attributes
        {'color': 'red'}

        Update attributes.

        >>> u.update(color='green',shape='rectangle')
        >>> u.attributes
        {'color': 'green', 'shape': 'rectangle'}

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
        >>> v.uid
        u
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
