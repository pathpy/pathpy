#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : node.py -- Base class for a single node
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2020-04-02 15:16 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Set

from pathpy import logger, config
from pathpy.core.base import BaseClass

# create logger for the Node class
LOG = logger(__name__)


class Node(BaseClass):
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
            node uid.

        Examples
        --------
        Genarate new node.

        >>> from pathpy import Node
        >>> u = Node('u')
        >>> print(u)
        Node u

        """
        return '{} {}'.format(self._desc(), self.uid)

    def __str__(self) -> str:
        """Print a summary of the node.

        The summary contains the uid, the type, the in- and outdegree.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        """
        return self.summary()

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
        """Return the unique identifier (uid) of the node.

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
        return self._uid

    @property
    def outgoing(self) -> Set[str]:
        """Returns the outgoing edge uids of the node.

        Returns
        -------
        Set[str]

            Return the uids of the outgoing edges of the node.

        Examples
        --------
        Generate two nodes and an (directed) edge.

        >>> from pathpy import Node, Edge
        >>> u = Node('u')
        >>> v = Node('v')
        >>> e = Edge('u','v')

        Print the outgoing edges for the node u.

        >>> u.outgoing
        {'u-v'}

        """
        return self._outgoing

    @property
    def incoming(self) -> Set[str]:
        """Returns the incoming edge uids of the node.

        Returns
        -------
        Set[str]

            Return the uids of the incoming edges of the node.

        Examples
        --------
        Generate two nodes and an (directed) edge.

        >>> from pathpy import Node, Edge
        >>> u = Node('u')
        >>> v = Node('v')
        >>> e = Edge('u','v')

        Print the incoming edges for the node v.

        >>> v.incoming
        {'u-v'}

        """
        return self._incoming

    # TODO: Maybe rename to adjacent?
    @property
    def adjacent_edges(self) -> Set[str]:
        """Returns the set of edge uids adjacent to the node.

        Returns
        -------
        Set[str]

            Returns a set of adjacent edge uids as string values.  I.e. all
            edges associated with this node.

        Examples
        --------
        Generate some nodes and (directed) edges.

        >>> from pathpy import Node, Edge
        >>> u = Node('u')
        >>> v = Node('v')
        >>> w = Node('w')
        >>> e1 = Edge('u','v')
        >>> e2 = Edge('v','w')

        Print the adjacent edges for the nodes.

        >>> print(u.adjacent_edges)
        {'u-v'}
        >>> print(v.adjacent_edges)
        {'v-w', 'u-v'}
        >>> print(w.adjacent_edges)
        {'v-w'}

        """
        return self.incoming.union(self.outgoing)

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
            'Indegree:\t{}\n'.format(len(self.incoming)),
            'Outdegree:\t{}'.format(len(self.outgoing)),
        ]
        
        return ''.join(summary)

    def update(self, other: Node = None, attributes: bool = True,
               **kwargs: Any) -> None:
        """Update of the node object.

        Update the node with new kwargs or based on an other given
        :py:class:`Node` object. If an other object is given, the other
        attributes can be used or not.

        Parameters
        ----------
        other : Node, optional (default = None)

            An other :py:class:`Node` object, which is used to update the node
            attributes and properties.

        attributes : bool, optional (default = True)

            If ``True`` the attributes from the other node are written to the
            initial node. If ``False`` only the incoming and outgoing edges are
            updated.

        kwargs : Any

            Keyword arguments stored as node attributes. Attributes are added
            to the node as ``key=value`` pairs.

        Examples
        --------
        Create an :py:class:`Node` object with an assigned attribute.

        >>> from pathpy import Node
        >>> u = Node('u', color='red')
        >>> u['color']
        'red'

        Update color and shape of the node.

        >>> u.update(color='green', shape='rectangle')
        >>> u['shape']
        'rectangle'

        Create a new node.

        >>> v = Node('v', shape='circle', size=30)
        >>> u.update(v)
        >>> u.attributes
        {'color': 'green', 'shape': 'circle', 'size': 30}

        """
        # if an other node is given
        if other is not None:

            # get relations with the associated nodes
            self._incoming = self.incoming.union(other.incoming)
            self._outgoing = self.outgoing.union(other.outgoing)

            # get the attributes of the other node
            if attributes:
                self.attributes.update(
                    **other.attributes.to_dict(history=False))

        # update the attributes given new kwargs
        self.attributes.update(**kwargs)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
