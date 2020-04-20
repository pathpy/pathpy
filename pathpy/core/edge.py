"""Edge class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : edge.py -- Base class for an single edge
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2020-04-16 10:06 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Optional

from pathpy import logger
from pathpy.core.base import BaseEdge
from pathpy.core.node import Node

# create logger for the Edge class
LOG = logger(__name__)


class Edge(BaseEdge):
    """Base class for an single edge.

    An edge is (together with nodes) one of the two basic units out of which
    networks are constructed. Each edge has two nodes to which it is attached,
    called its endpoints. Edges may be directed or undirected; undirected edges
    are also called lines and directed edges are also called arcs or arrows. In
    an undirected network, an edge may be represented as the set of its nodes,
    and in a directed network it may be represented as an ordered pair of its
    vertices.

    The two nodes forming an :py:class:`Edge` are said to be the endpoints of
    this edge, and the edge is said to be incident to the nodes.

    In ``pathpy`` the edge is referenced by its unique identifier (``uid``),
    connects two :py:class:`Node` objects and can store any arbitrary python
    objects as attributes.

    .. note::

       To generate an edge, only two nodes have to be defined. ``pathpy`` will
       automatically create a unique identifier (``uid``) for the edge based on
       the node uids. In this case, the edge ``uid`` is defined as a
       combination of the node uids separated by ``-``. The separation sign can
       be changed in the config file.

    Parameters
    ----------

    v : Node

        This parameter defines the source of the edge (if directed),
        i.e. v->w. Beside a py:class:`Node` object also a ``str`` node uid can
        be entered, in this case, a new :py:class:`Node` will be created.

    w : Node

        This parameter defines the target of the edge (if directed)
        i.e. u->v. Beside a py:class:`Node` object also a ``str`` node uid can
        be entered, in this case, a new :py:class:`Node` will be created.

    uid : str, optional (default = None)

        The parameter ``uid`` is the unique identifier for the edge. Every edge
        should have an uid. The uid is converted to a string value and is used
        as a key value for all dict which saving edge objects. If no edge uid
        is specified the edge ``uid`` will be defined as a combination of the
        node uids separated by ``-``. The separation sign can be changed in the
        config file.

    directed : bool, optional (default = True)

        If ``True`` the edge is directed, i.e. quantities can only transmited
        from the source node ``v`` to the traget node ``w``. If ``False`` the
        edge is undirected, i.e. quantities can be transmited in both
        directions. Per default edges in ``pathpy`` are directed.

    kwargs : Any

        Keyword arguments to store edge attributes. Attributes are added to the
        edge as ``key=value`` pairs.

    Examples
    --------
    From the ``pathpy`` import the :py:class:`Node` and :py:class:`Edge` classes.

    >>> from pathpy import Node, Edge

    Create an edge ``e`` with given nodes.

    >>> v = Node('w')
    >>> w = Node('v')
    >>> e = Edge(v, w, uid='e')
    >>> e.uid
    e

    Create an edge with given node uids and no edge uid.

    >>> ab = Edge('a', 'b')
    >>> ab.uid
    a-b

    Show the associated node objects

    >>> ab.nodes
    NodeDict(<class 'dict'>, {'a': Node a, 'b': Node b})

    Create an edge with attached attribute.

    >>> ab = Edge('a','b', length=10)

    Add attribute to the edge.

    >>> ab['capacity'] = 5.5

    Show attached attributes

    >>> ab.attributes
    {'length': 10, 'capacity': 5}

    Change attribute.

    >>> ab['length'] = 5

    Update attributes (and add new).

    >>> ab.update(length = 2, capacity = 3, speed = 10)
    >>> ab.attributes
    {'length': 2, 'capacity': 3, 'speed': 10}

    Get the weight of the edge. Per default the attribute with the key 'weight'
    is used as weight. Should there be no such attribute, a new one will be
    crated with weight = 1.0.

    >>> ab.weight()
    1.0

    If an other attribute should be used as weight, the option weight has to be
    changed.

    >>> ab.weight('length')
    2

    If a weight is assigned but for calculation a weight of 1.0 is needed, the
    weight can be disabled with ``False`` or None.

    >>> ab['weight'] = 4
    >>> ab.weight()
    4.0
    >>> ab.weight(False)
    1.0

    Make copy of the edge.

    >>> ef = ab.copy()
    >>> ef.uid
    'a-b'

    Make a plot element and plot the edge as a png image.

    .. todo::

        Make a single plot command for plotting edges.
        The code below is not working yet!

    >>> plt = ab.plot()
    >>> plt.show('png')

    .. plot::

       import pathpy as pp
       ab = pp.Edge('a','b')
       net = pp.Network()
       net.add_edge(ab)
       plt = net.plot()
       plt.show('png')

    Create an undirected edge.

    >>> cd = Edge('c', 'd', directed=False)
    >>> plt = ab.plot()
    >>> plt.show('png')

    .. plot::

       import pathpy as pp
       cd = pp.Edge('c','d',directed=False)
       net = pp.Network(directed=False)
       net.add_edge(cd)
       plt = net.plot()
       plt.show('png')


    See Also
    --------
    Node

    """

    def __init__(self, v: Node, w: Node, uid: Optional[str] = None,
                 **kwargs: Any) -> None:
        """Initialize the edge object."""

        # initialize the base class
        super().__init__(uid=uid, **kwargs)

        # a set containing node objects
        self._nodes: set = set()

        # add attributes to the edge
        self.attributes.update(**kwargs)

        # check nodes
        if not isinstance(v, Node) or not isinstance(w, Node):
            LOG.error('v and w have to be Node objects!')
            raise TypeError

        # add nodes
        self._v: Node = v
        self._w: Node = w

        self._nodes.add(v)
        self._nodes.add(w)

    def __str__(self) -> str:
        """Print a summary of the edge.

        The summary contains the uid, the associated nodes, and if it is
        directed or not.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        """
        return self.summary()

    @property
    def uid(self) -> str:
        """Return the unique identifier (uid) of the edge.

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
        return super().uid

    @property
    def nodes(self) -> set:
        """Return the associated nodes of the edge.

        Returns
        -------
        :py:class:`NodeDict`

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
        Generate an single edge and return the source node.

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
        Generate an single edge and return the target node.

        >>> from pathpy import Edge
        >>> vw = Edge('v','w')
        >>> vw.w
        Node w

        """
        return self._w

    def summary(self) -> str:
        """Returns a summary of the edge.

        The summary contains the uid, the associated nodes, and if it is
        directed or not.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        Returns
        -------
        str

            Return a summary of the edge.

        """
        summary = [
            'Uid:\t\t{}\n'.format(self.uid),
            'Type:\t\t{}\n'.format(self.__class__.__name__),
            'Source node:\t{}\n'.format(self.v.__repr__()),
            'Target node:\t{}'.format(self.w.__repr__()),
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
