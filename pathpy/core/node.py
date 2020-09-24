"""Node Class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : node.py -- Base class for a single node
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Sun 2020-09-06 10:44 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Optional, Union, Set
from singledispatchmethod import singledispatchmethod

from pathpy import logger
from pathpy.core.base import BaseNode, BaseCollection

# create logger for the Node class
LOG = logger(__name__)


class Node(BaseNode):
    """Base class for a single node.

    A node (or vertex) is the fundamental unit of which networks are formed. In
    general nodes are treated as featureless and indivisible objects, although
    they may have additional structure depending on the application from which
    the netwokr arises.

    The two nodes forming an :py:class:`Edge` are said to be the endpoints of
    this edge, and the edge is said to be incident to the nodes.

    In ``pathpy`` the node is referenced by its unique identifier (``uid``) and
    can store any arbitrary python objects as attributes.

    Parameters
    ----------
    uid : str

        The parameter ``uid`` is the unique identifier for the node. Every node
        should have an uid. The uid is converted to a string value and is used
        as a key value for all dict which saving node objects.

    kwargs : Any

        Keyword arguments to store node attributes. Attributes are added to the
        node as ``key=value`` pairs.

    Examples
    --------
    Load the ``pathpy`` module and create an empty :py:class:`Node` object.

    >>> from pathpy import Node
    >>> u = Node('u')

    Get the id of the node.

    >>> u.uid
    'u'

    Create a node with attached attribute.

    >>> u = Node('u', color='red')
    >>> u['color']
    'red'

    Add attribute to the node.

    >>> u['shape'] = 'circle'
    >>> u['shape]
    'circle'

    Change single attribute.

    >>> u['color'] = 'blue'

    Update multiple attributes.

    >>> u.update(color='green', shape='rectangle')

    Make a copy of the node.

    >>> v = u.copy()
    >>> v.uid
    'u'

    Make a plot element and plot the node as a png image.

    .. todo::

        Make a single plot command for plotting nodes.
        The code below is not working yet!

    >>> plt = u.plot()
    >>> plt.show('png')

    .. plot::

       import pathpy as pp
       u = pp.Node('u', color='green', shape='rectangle')
       net = pp.Network()
       net.add_node(u)
       plt = net.plot()
       plt.show('png')

    See Also
    --------
    Edge

    """

    def __init__(self, uid: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the node object."""

        # initialize the base class
        super().__init__(uid=uid, **kwargs)

        # add attributes to the node
        self.attributes.update(uid=self.uid, **kwargs)

    @property
    def uid(self) -> str:
        """Return the unique identifier (uid) of the node object.

        Returns
        -------
        str

            Return the node identifier (uid) as a string.

        Examples
        --------
        Generate a single node and print the uid.

        >>> from pathpy import Node
        >>> u = Node('u')
        >>> u.uid
        u

        """
        return super().uid

    def __str__(self) -> str:
        """Print a summary of the node.

        The summary contains the uid, the type, the in- and outdegree.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        """
        return self.summary()

    def summary(self) -> str:
        """Returns a summary of the node.

        The summary contains the uid, the type, the in- and outdegree.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        Returns
        -------
        str

            Return a summary of the node.

        """
        summary = [
            'Uid:\t\t{}\n'.format(self.uid),
            'Type:\t\t{}\n'.format(self.__class__.__name__),
        ]

        return ''.join(summary)


class NodeSet(BaseCollection):
    """A set of nodes."""

    def add(self, node: Node) -> None:
        """Add a node to the set of nodes."""
        self._map[node.uid] = node

    def discard(self, node: Node) -> None:
        """Removes the specified item from the set."""
        self.pop(node.uid, None)

    def __getitem__(self, key: Union[int, str, Node]) -> Node:
        """Returns a node object."""
        node: Node
        if isinstance(key, Node) and key in self:
            node = key
        elif isinstance(key, (int, slice)):
            node = list(self._map.values())[key]
        else:
            node = self._map[key]
        return node

    def __setitem__(self, key: Any, value: Any) -> None:
        """Set an node object."""
        for node in self.values():
            node[key] = value

    def __repr__(self) -> str:
        """Description of the object."""
        return set(self.values()).__repr__()

    @property
    def uid(self) -> Set[str]:
        """return a set of uids"""
        return set(self.keys())


class NodeCollection(BaseCollection):
    """A collection of nodes"""

    def __init__(self) -> None:
        """Initialize the NodeCollection object."""

        # initialize the base class
        super().__init__()

        # class of objects
        self._node_class: Any = Node

    def __getitem__(self, key: Union[str, Node]) -> Node:
        """Returns a node object."""
        if isinstance(key, str):
            _node = self._map[key]
        elif isinstance(key, self._node_class) and key in self:
            _node = key
        else:
            raise KeyError
        return _node

    def __lshift__(self, node: Node) -> None:
        """Quick assigment of the node"""
        self[node.uid] = node

    @singledispatchmethod
    def add(self, *node, **kwargs: Any) -> None:
        """Add multiple nodes. """

        raise NotImplementedError

    @add.register(Node)  # type: ignore
    def _(self, *node: Node, **kwargs: Any) -> None:
        # check if more then one node is given raise an AttributeError
        if len(node) != 1:
            LOG.error('More then one node was given.')
            raise AttributeError

        # get node object
        _node: Node = node[0]

        # update node attributes
        _node.update(**kwargs)

        # check if node exists already
        if _node not in self and _node.uid not in self.keys():
            # if not add new node
            self[_node.uid] = _node
        else:
            # raise error if edge already exists
            LOG.error('The node "%s" already exists!', _node.uid)
            raise KeyError

    @add.register(str)  # type: ignore
    def _(self, *node: str, **kwargs: Any) -> None:

        # get node uid
        _uid: str = node[0]

        # check if node with given uid str exists already
        if _uid not in self:
            # if not add new node with provided uid str
            self[_uid] = self._node_class(uid=_uid, **kwargs)
        else:
            # raise error if node already exists
            LOG.error('The node "%s" already exists!', _uid)
            raise KeyError

    @add.register(tuple)  # type: ignore
    @add.register(list)  # type: ignore
    def _(self, *node: tuple, **kwargs: Any) -> None:
        for _n in node[0]:
            self.add(_n, **kwargs)

    def _add(self, node: Node) -> None:
        self[node.uid] = node

    @singledispatchmethod
    def remove(self, *nodes: Union[str, Node, tuple, list], **kwargs) -> None:
        """Remove multiple nodes. """
        # pylint: disable=unused-argument

        raise NotImplementedError

    @remove.register(Node)  # type: ignore
    @remove.register(str)  # type: ignore
    def _(self, *node: Union[str, Node], **kwargs: Any) -> None:
        # pylint: disable=unused-argument
        if node[0] in self:
            self.pop(self[node[0]].uid, None)

    @remove.register(tuple)  # type: ignore
    @remove.register(list)  # type: ignore
    def _(self, *node: Union[tuple, list], **kwargs: Any) -> None:
        for _n in node[0]:
            self.remove(_n, **kwargs)

    def copy(self) -> NodeCollection:
        """Return a new copy of the node collection."""
        nodes = NodeCollection()
        for node in self.values():
            nodes.add(node)
        return nodes


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
