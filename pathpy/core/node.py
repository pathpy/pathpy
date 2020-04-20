"""Node Class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : node.py -- Base class for a single node
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2020-04-16 09:26 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Optional

from pathpy import logger
from pathpy.core.base import BaseNode

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


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
