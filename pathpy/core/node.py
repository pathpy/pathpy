"""Node Class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : node.py -- Base class for a node
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2021-05-28 10:48 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from typing import Any, Optional, Union

from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9

from pathpy import logger
from pathpy.core.core import PathPyObject, PathPyPath, PathPyCollection

# create logger for the Path class
LOG = logger(__name__)


class Node(PathPyPath):
    """Base class for a node.

    A node (or vertex) is the fundamental unit of which networks are formed. In
    general nodes are treated as featureless and indivisible objects, although
    they may have additional structure depending on the application from which
    the netwokr arises.

    In ``pathpy`` the :py:class:`Node` is a path of length 0. I.e. an object
    which do not have any explicit relations to other objects. Internaly it
    refers to a :py:class:`PathPyObject` or to itself.  The node is referenced
    by its unique identifier (``uid``) and can store any arbitrary python
    objects as attributes.

    Parameters
    ----------
    *node : str or PathPyObject

        A ``str`` or :py:class:`PathPyObject` associated with the node. The
        :py:class:`Node` will point to this object and stor this reference. If
        a ``str`` is given, the :py:class:`Node` will refere to itself usig the
        ``str`` as ``uid``.

    uid : str optional (default=None)

        The parameter ``uid`` is the unique identifier for the node. Every node
        should have an uid. The uid is converted to a string value and is used
        as a key value for all dict which saving node objects. If no ``uid`` is
        given, and the node argument is not a ``str``, a random python uid will
        be assigned.

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
    Path

    """

    def __init__(self, *node: Union[str, PathPyObject],
                 uid: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the node object."""

        # Node Assumption:
        # ----------------
        # If only one string argument is given and no uid is defined
        # use the string argument as uid
        uid = node[0] if node and isinstance(
            node[0], (int, str)) and uid is None else uid
        node = (str(uid), ) if not node else node

        # initialize the parent class
        super().__init__(*node, uid=uid, **kwargs)


class NodeCollection(PathPyCollection):
    """A collection of nodes"""
    # pylint: disable=too-many-ancestors

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the NodeCollection object."""

        # initialize the base class
        super().__init__(*args, **kwargs)

        # class of objects
        self._default_class: Any = Node

    @singledispatchmethod
    def add(self, *args, **kwargs: Any) -> None:
        """Add multiple nodes. """
        raise NotImplementedError

    @add.register(Node)  # type: ignore
    def _(self, *args: Node, **kwargs: Any) -> None:
        super().add(args[0], **kwargs)

    @add.register(str)  # type: ignore
    @add.register(int)  # type: ignore
    @add.register(PathPyObject)  # type: ignore
    def _(self, *args: Union[int, str, PathPyObject], **kwargs: Any) -> None:
        super().add(args[0], **kwargs)

    @add.register(tuple)  # type: ignore
    @add.register(list)  # type: ignore
    def _(self, *args: tuple, **kwargs: Any) -> None:
        for arg in args[0]:
            self.add(arg, **kwargs)

    @singledispatchmethod
    def remove(self, *node, **kwargs):
        """Remove objects"""
        super().remove(*node, **kwargs)

    @remove.register(tuple)  # type: ignore
    @remove.register(list)  # type: ignore
    def _(self, *node: tuple, **kwargs: Any) -> None:
        for _n in node[0]:
            self.remove(_n, **kwargs)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
