#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : node.py -- Base class for a node
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-10-31 10:25 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Set

from .. import logger
from .base import BaseClass

# create logger for the Node class
log = logger(__name__)


class Node(BaseClass):
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

        # initialize the base class
        super().__init__(**kwargs)

        # assign node identifier
        self._uid: str = str(uid)

        # set of incoming and outgoing edges
        self._outgoing: set = set()
        self._incoming: set = set()

        # add attributes to the node
        self.attributes.update(uid=self.uid, **kwargs)

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
    def outgoing(self) -> Set[str]:
        """Returns the outgoing edge uids of the node."""
        return self._outgoing

    @property
    def incoming(self) -> Set[str]:
        """Returns the incoming edge uids of the node."""
        return self._incoming

    # TODO: Maybe rename to adjacent?
    @property
    def adjacent_edges(self) -> Set[str]:
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


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
