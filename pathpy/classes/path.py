#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py -- Base class for a path
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2019-10-11 09:18 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List, Dict, Optional
from collections import defaultdict, Counter

from .. import logger, config
from . import Node, Edge

# create logger for the Edge class
log = logger(__name__)


class Path:
    """Base class for a path."""

    def __init__(self, *args: Edge, uid: str = '',
                 directed: bool = True, **kwargs: Any) -> None:
        """Initialize the path object."""
        # Classes of the Node, Edge and Path objects
        # TODO: Probably there is a better solution to have different Node and
        # Edge classes for different Network sub classes
        self._node_class()
        self._edge_class()

        # set unique identifier of the path
        self._uid: str = uid

        # inidcator whether the edge is directed or undirected
        self._directed: bool = directed

        # dictionary for edge attributes
        self._attributes: dict = {}

        # add attributes to the edge
        self.attributes.update(kwargs)

        # use separator if given otherwise use config default value
        self.separator: str = kwargs.get('separator',
                                         config.get('path', 'separator'))

        # use separator if given otherwise use config default value
        self.edge_separator: str = kwargs.get('edge_separator',
                                              config.get('edge', 'separator'))

        # get the max display name length
        self.max_name_length: int = kwargs.get('max_name_length',
                                               config.getint(
                                                   'path',
                                                   'max_name_length'))

        # check code
        self.check: bool = kwargs.get('check_code',
                                      config.getboolean('computation',
                                                        'check_code'))

        # a dictionary containing node objects
        self._nodes: dict = defaultdict(dict)

        # a dictionary containing edge objects
        self._edges: dict = defaultdict(dict)

        # a list containing the path
        self._path: List[str] = []

        # a counter fo the nodes
        self._node_counter: Counter = Counter()

        # a counter fo the edges
        self._edge_counter: Counter = Counter()

        # add edges
        if len(args) > 0:
            if isinstance(args[0], self.EdgeClass):
                self.add_edges_from(list(args))

            elif isinstance(args[0], str):
                self.add_nodes_from(args)

    def _node_class(self) -> None:
        """Internal function to assign different Node classes."""
        self.NodeClass = Node

    def _edge_class(self) -> None:
        """Internal function to assign different Edge classes."""
        self.EdgeClass = Edge

    def __repr__(self) -> str:
        """Return the description of the path.

        Returns
        -------
        str
            Returns the description of the path with the class, the name (if
            deffined) and the assigned system id.

        Examples
        --------
        Generate new path

        >>> from pathpy import Path
        >>> p = Path()
        >>> p
        Path object  at 0x140458648250512x

        """
        return '<{} object {} at 0x{}x>'.format(self._desc(),
                                                self.name,
                                                id(self))

    def _desc(self) -> str:
        """Return a string *Path()*."""
        return '{}'.format(self.__class__.__name__)

    def __setitem__(self, key: Any, value: Any) -> None:
        """Add a specific attribute to the path.

        An attribute has a key and the corresponding value expressed as a pair,
        key: value.

        Parameters
        ----------
        key: Any
            Unique identifier for a corrisponding value.

        value: Any
            A value i.e. attribute which is associated with the path.

        Examples
        --------
        Generate new path.

        >>> from pathpy import Path
        >>> p = Path('a', 'b', 'c')

        Add atribute to the edge.

        >>> p['capacity'] = 5.5

        """
        self.attributes[key] = value

    def __getitem__(self, key: Any) -> Any:
        """Returns a specific attribute of the path.

        Parameters
        ----------
        key: any
            Key value for the attribute of the edge.

        Returns
        -------
        any
            Returns the attribute of the path associated with the given key
            value.

        Raises
        ------
        KeyError
            If no attribute with the assiciated key is defined.

        Examples
        --------
        Generate new path with length 10

        >>> from pathpy import Path
        >>> p = Path('a', 'b', 'c', length=10)

        Get the edge attribute.

        >>> p[length]
        10

        """
        try:
            return self.attributes[key]
        except KeyError as error:
            log.error(
                'No attribute with key {} is defined!'.format(error))
            raise

    def __len__(self) -> int:
        """Returns the number of edges in the path"""
        return len(self.path)

    def __eq__(self, other: object) -> bool:
        """Returns True if two paths are equal, otherwise False."""
        return self.__dict__ == other.__dict__

    def __hash__(self) -> Any:
        """Returns the unique hash of the path.

        Here the hash value is defined by the unique path id!

        """
        return hash(self.uid)

    @property
    def uid(self) -> str:
        """Returns the id of the path.

        Id of the path. If no id is assigned the path is called after the
        assigned edges. e.g. if the path has edges 'a-b' and 'c-d', the id is
        'a-b|b-c'.

        Returns
        -------
        str
            Returns the uid of the path as a string.

        Examples
        --------

        Generate a simple path
        >>> from pathpy import Path
        >>> p = Path('a','b','c')
        >>> p.uid
        'a-b|b-c'

        """
        if self._uid != '':
            return self._uid
        else:
            return self.separator.join(self.path)

    @property
    def attributes(self) -> Dict:
        """Return the attributes associated with the path.

        Returns
        -------
        Dict
            Return a dictionary with the path attributes.

        Examples
        --------
        Generate a sample path with a color attribute.

        >>> from pathpy import Path
        >>> p = Path('v','w', color='red')

        Get the attributes of the path.

        >>> p.attributes
        {'color'='red'}

        """
        return self._attributes

    @property
    def directed(self):
        """Return if the path is directed (True) or undirected (False)."""
        return self._directed

    @property
    def name(self) -> str:
        """Returns the name of the path.

        Name of the path. If no name is assigned the network is called after
        the assigned edge. e.g. if the path has edges 'a-b' and 'b-c', the path
        is named 'a-b|b-c'. The maximum length of the name is defined in the

        config file and is per default 5. E.g. if the path has 6 edges
        (a-b,b-c,c-d,d-e,e-f,f-g) the name of the path is
        'a-b|b-c|c-d|d-e|...|f-g'. Please, note the name of a path is NOT an
        unique identifier!

        Returns
        -------
        str
            Returns the name of the path as a string.

        Examples
        --------

        Generate simple path:

        >>> from pathpy import Path
        >>> p = Path('a', 'b', 'c')
        >>> p.name
        'a-b|b-c'

        Generate longer path:
        >>> p = Path('a', 'b', 'c', 'd', 'e', 'f', 'g')
        >>> p.name
        'a-b|b-c|c-d|d-e|...|f-g'

        """

        if len(self) > self.max_name_length:
            _name = self.separator.join(
                self.path[0:-2][0:self.max_name_length]) \
                + self.separator + '...' + self.separator \
                + self.path[-1]
        else:
            _name = self.separator.join(self.path)

        return self.attributes.get('name', _name)

    @property
    def nodes(self) -> Dict[str, Node]:
        """Return the associated nodes of the path.

        Returns
        -------
        Dict[str,Node]
            Return a dictionary with the :py:class:`Node` uids as key and the
            :py:class:`Node` objects as values, associated with the path.

        Examples
        --------
        Generate a simple path.

        >>> from pathpy import Path
        >>> p = Path('a','b','c')

        Get the nodes of the path

        >>> p.nodes
        {'a': Node a, 'b': Node b, 'c': Node c}
        """
        return self._nodes

    @property
    def edges(self) -> Dict[str, Edge]:
        """Return the associated edges of the path.

        Returns
        -------
        Dict[str,Edge]
            Return a dictionary with the :py:class:`Edge` uids as key and the
            :py:class:`Edge` objects as values, associated with the path.

        Examples
        --------
        Generate a simple path.

        >>> from pathpy import Path
        >>> p = Path('a','b','c')

        Get the nodes of the path

        >>> p.edges
        {'a-b': Edge a-b, 'b-c': Edge b-c}
        """
        return self._edges

    @property
    def path(self) -> List[str]:
        """Return the adjacend edge uids in the path.

        Returns
        -------
        List[str]
            Return a list the :py:class:`Edge` uids.

        Examples
        --------
        Generate a simple path.

        >>> from pathpy import Path
        >>> p = Path('a','b','c','a','b',)

        Get the edges of the path

        >>> p.path
        ['a-b','b-c','c-a','a-b']

        """
        return self._path

    @property
    def node_counter(self) -> Counter:
        """Returns a Conter object for the nodes.

        Returns
        -------
        Counter
            Retunr a Counter with nodes uids

        Examples
        --------
        Generate a simple path.

        >>> from pathy import Path
        >>> p = Path('a', 'b', 'c', 'a', 'b',)
        >>> p.node_counter
        Counter({'a': 2, 'b': 2, 'c': 1})

        Get the two most common nodes.

        >>> p.node_counter.most_common(2)
        [('a', 2), ('b', 2)]

        """
        nodes = [self.edges[e].v.uid for e in self.path]
        nodes.append(self.edges[self.path[-1]].w.uid)
        return Counter(nodes)

    @property
    def edge_counter(self) -> Counter:
        """Returns a Conter object for the edges.

        Returns
        -------
        Counter
            Retunr a Counter with edge uids

        Examples
        --------
        Generate a simple path.

        >>> from pathy import Path
        >>> p = Path('a', 'b', 'c', 'a', 'b',)
        >>> p.edge_counter
        Counter({'a-b': 2, 'b-c': 1, 'c-a': 1})

        Get the two most common edges.

        >>> p.edge_counter.most_common(2)
        [('a-b', 2), ('b-c', 1)]

        """
        return Counter(self.path)

    def update(self, **kwargs: Any) -> None:
        """Update the attributes of the path.

        Parameters
        ----------
        kwargs : Any
            Attributes to add or update for the path as key=value pairs.

        Examples
        --------
        Update attributes.

        >>> from pathpy import Path
        >>> p = Path(street='High Street')
        >>> p.attributes
        {'street': 'High Street'}

        Update attributes

        >>> p.update(street='Market Street', toll=False)
        >>> p.attributes
        {'street': 'Market Street', 'toll': False}

        """
        self.attributes.update(kwargs)

    def summary(self) -> Optional[str]:
        """Returns a summary of the path.

        The summary contains the name, the used path class, if it is directed
        or not, the number of unique nodes and unique edges, and the number of
        nodes in the path.

        Since a path can multiple times pass the same node and edge objects,
        the length of the path (i.e. the consecutive nodes) might be larger
        then the number of unique nodes.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        """
        summary = [
            'Name:\t\t\t{}\n'.format(self.name),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            'Directed:\t\t{}\n'.format(str(self.directed)),
            'Number of unique nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of unique edges:\t{}'.format(self.number_of_edges()),
            'Path length (# edges):\t{}'.format(len(self))
        ]
        if config.getboolean('logging', 'enabled'):
            for line in summary:
                log.info(line.rstrip())
            return None
        else:
            return ''.join(summary)

    def number_of_nodes(self, unique: bool = True) -> int:
        """Return the number of nodes in the path.

        Parameters
        ----------
        unique : bool, optional (default = True)
            If unique is True only the number of unique nodes in the path is
            returnd.

        Returns
        -------
        int
            Returns the number of nodes in the path.

        Examples
        --------
        Generate a simple path.

        >>> from pathy import Path
        >>> p = Path('a', 'b', 'c', 'a', 'b',)

        Get the number of unique nodes:

        >>> p.number_of_nodes()
        3

        Get the number of all nodes in the path:

        >>> p.number_of_nodes(unique=False)
        5

        """
        if unique:
            return len(self.nodes)
        else:
            return len(self.path)+1

    def number_of_edges(self, unique: bool = True) -> int:
        """Return the number of edges in the path.

        Parameters
        ----------
        unique : bool, optional (default = True)
            If unique is True only the number of unique edges in the path is
            returnd.

        Returns
        -------
        int
            Returns the number of edges in the path.

        Examples
        --------
        Generate a simple path.

        >>> from pathy import Path
        >>> p = Path('a', 'b', 'c', 'a', 'b',)

        Get the number of unique edges:

        >>> p.number_of_edges()
        3

        Get the number of all edges in the path:

        >>> p.number_of_nodes(unique=False)
        4

        """
        if unique:
            return len(self.edges)
        else:
            return len(self.path)

    def add_edges_from(self, edges: List[Edge], **kwargs: Any) -> None:
        """Add multiple edges from a list.

        Parameters
        ----------
        nodes: List[Edge]

            Edges from a list of: py: class:`Edge` objects are added to the
            path.

        kwargs: Any, optional(default={})
            Attributes assigned to all nodes in the list as key = value pairs.

        """
        # iterate over a list of nodes
        # TODO: parallize this function
        for edge in edges:
            self.add_edge(edge, **kwargs)

    def add_edge(self, edge: Edge, **kwargs: Any) -> None:
        """Add a single edge to the path.

        Parameters
        ----------
        node:: py: class: `Edge`
            The: py: class: `Edge` object, which will be added to the path.

        kwargs: Any, optional(default={})
            Attributes assigned to the node as key = value pairs.

        """
        # check if the right object is provided
        if not isinstance(edge, self.EdgeClass) and self.check:
            edge = self._check_edge(edge, **kwargs)

        # check if edge is already defined
        if edge.uid not in self.edges:

            # check if node v is already defined, otherwise add node
            if edge.v.uid not in self._nodes:
                self.nodes[edge.v.uid] = edge.v

            # check if node w is already defined, otherwise add node
            if edge.w.uid not in self._nodes:
                self.nodes[edge.w.uid] = edge.w

            # add new edge to the path
            self.edges[edge.uid] = edge

        # append edge to the path
        self.path.append(edge.uid)

    def _check_edge(self, node: Any, **kwargs: Any) -> Edge:
        """Helperfunction to check if the edge is in the right format."""
        raise NotImplementedError

    def add_node(self, node: Node, **kwargs: Any) -> None:
        """Add a single node to the path.

        Parameters
        ----------
        node:: py: class: `Node`
            The: py: class: `Node` object, which will be added to the path.

        kwargs: Any, optional(default={})
            Attributes assigned to the node as key = value pairs.

        """
        # check if the right object is provided.
        if not isinstance(node, self.NodeClass) and self.check:
            node = self._check_node(node, **kwargs)

        # get predecessor node
        v: List[Node] = []
        # if no edge is defined us the first assigned node
        if self.number_of_nodes() == 1:
            v.append(list(self.nodes.values())[0])
        # use the last node in the path
        elif self.number_of_nodes() > 1:
            v.append(self.edges[self.path[-1]].w)

        # add node to the path
        if node.uid not in self.nodes:
            self.nodes[node.uid] = node

        # assigne edge from the last added node to the new node
        # TODO: Make also work for muli-edges
        # TODO: Make the code nicer
        if ((self.number_of_nodes() >= 2) or
                (self.number_of_nodes() == 1 and len(v) > 0)):
            # add edge
            if v[0].uid+self.edge_separator+node.uid not in self.edges:
                self.add_edge(self.EdgeClass(v[0], node))
            # update path
            else:
                self.path.append(v[0].uid+self.edge_separator+node.uid)

    def add_nodes_from(self, nodes: List[Node], **kwargs: Any) -> None:
        """Add multiple nodes from a list.

        Parameters
        ----------
        nodes: List[Node]

            Nodes from a list of: py: class: `Node` objects are added to the
            path.

        kwargs: Any, optional(default={})
            Attributes assigned to all nodes in the list as key = value pairs.

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

    def weight(self, weight: str = 'weight') -> float:
        """Returns the weight of the path.

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

        >>> form pathpy import Path
        >>> p = Path('a','b','c')
        >>> p.weight()
        1.0

        Change the weight.

        >>> p['weight'] = 4
        >>> p.weight()
        4.0

        >>> p.weight(False)
        1.0

        Add an attribute and use this as weight.

        >>> p['length'] = 5
        >>> p.weight('length')
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

    def has_subpath(self, subpath: Path) -> bool:
        raise NotImplementedError

    def subpath(self, *args: str) -> Path:
        raise NotImplementedError

    def subpaths(self, min_length: int = None,
                 max_length: int = None) -> List[Path]:
        raise NotImplementedError

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
