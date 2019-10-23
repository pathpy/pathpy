#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py -- Base class for a path
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-10-17 13:38 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List, Dict, Optional, Sequence
from collections import defaultdict, Counter
from copy import deepcopy
import sys

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
                                         config['path']['separator'])

        # use separator if given otherwise use config default value
        self.edge_separator: str = kwargs.get('edge_separator',
                                              config['edge']['separator'])

        # get the max display name length
        self.max_name_length: int = kwargs.get(
            'max_name_length', config['path']['max_name_length'])

        # check code
        self.check: bool = kwargs.get(
            'check_code', config['computation']['check_code'])

        # a dictionary containing node objects
        self._nodes: dict = defaultdict(dict)

        # a dictionary containing edge objects
        self._edges: dict = defaultdict(dict)

        # a list containing the edge uids of the path
        self._as_edges: List[str] = []

        # a list containing the node uids of the path
        self._as_nodes: List[str] = []

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
        self.NodeClass: Any = Node

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
        return len(self.as_edges)

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
        """Returns the unique id of the path.

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
        elif self.number_of_edges() > 0:
            return self.separator.join(self.as_edges)
        elif self.number_of_nodes() > 0:
            return self.as_nodes[0]
        else:
            return str(id(self))

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
                self.as_edges[0:-2][0:self.max_name_length]) \
                + self.separator + '...' + self.separator \
                + self.as_edges[-1]
        else:
            _name = self.separator.join(self.as_edges)

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
    def as_nodes(self) -> List[str]:
        """Return the adjacend node uids in the path.

        Returns
        -------
        List[str]
            Return a list the :py:class:`Node` uids.

        Examples
        --------
        Generate a simple path.

        >>> from pathpy import Path
        >>> p = Path('a','b','c','a','b',)

        Get the path as a list of nodes

        >>> p.as_nodes
        ['a', 'b', 'c', 'a', 'b']

        """
        return self._as_nodes

    @property
    def as_edges(self) -> List[str]:
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

        >>> p.as_edges
        ['a-b', 'b-c', 'c-a', 'a-b']

        """
        return self._as_edges

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
        return Counter(self.as_nodes)

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
        return Counter(self.as_edges)

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
        if config['logging']['enabled']:
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
            return len(self.as_nodes)

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
        >>> p = Path('a', 'b', 'c', 'a', 'b')

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
            return len(self.as_edges)

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
        edge: :py:class:`Edge`
            The :py:class:`Edge` object, which will be added to the path.

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

                # check if node is part of the path
                if len(self.as_nodes) == 0:
                    self.as_nodes.append(edge.v.uid)

            # check if node w is already defined, otherwise add node
            if edge.w.uid not in self._nodes:
                self.nodes[edge.w.uid] = edge.w

            # add new edge to the path
            self.edges[edge.uid] = edge

        # append edge to the path
        self.as_edges.append(edge.uid)

        # append nodes to path
        self.as_nodes.append(edge.w.uid)

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

        v_uid: str = ''
        # get predecessor node
        if len(self.as_nodes) > 0:
            v_uid = self.as_nodes[-1]

        # add node to the path
        if node.uid not in self.nodes:
            self.nodes[node.uid] = node
        else:
            node = self.nodes[node.uid]

        # append node to path
        if len(self.as_nodes) == 0:
            self.as_nodes.append(node.uid)

        # assigne edge from the last added node to the new node
        # TODO: Make also work for muli-edges
        if len(self.as_nodes) > 0 and v_uid != '':
            # add edge
            edge_uid = v_uid+self.edge_separator+node.uid
            if edge_uid not in self.edges:
                self.add_edge(self.EdgeClass(self.nodes[v_uid],
                                             node,
                                             separator=self.edge_separator))
            else:
                self.add_edge(self.edges[edge_uid])

    def add_nodes_from(self, nodes: Sequence[Node], **kwargs: Any) -> None:
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

    def subpaths(self, min_length: int = 0,
                 max_length: int = sys.maxsize,
                 include_path: bool = False) -> Dict[str, Path]:
        """Returns a list of subpaths.

        Parameters
        ----------

        min_length : int, optional (default = 0)
            Parameter which defines the minimum length of the sub-paths. This
            parameter has to be smaller then the maximum length parameter.

        max_length : int, optional (default = sys.maxsize)
            Parameter which defines the maximum length of the sub-paths. This
            parameter has to be greater then the minimum length parameter. If
            the parameter is also greater then the maximum length of the path,
            the maximum path length is used instead.

        include_path : bool, optional (default = Flase)
            If this option is enabled also the current path is added as a
            sub-path of it self.

        Returns
        -------
        Dict[str, Paths]
            Return a dictionary with the :py:class:`Paht` uids as key and the
            :py:class:`Path` objects as values.

        Examples
        --------
        >>> from pathpy import Path
        >>> p = Path('a','b','c','d','e')
        >>> for k in p.subpaths():
        ...     print(k)
        a
        b
        c
        d
        e
        a-b
        b-c
        c-d
        d-e
        a-b|b-c
        b-c|c-d
        c-d|d-e
        a-b|b-c|c-d
        b-c|c-d|d-e

        >>> for k in p.subpaths(min_length = 2, max_length = 2)
        ...     print(k)
        a-b|b-c
        b-c|c-d
        c-d|d-e

        """

        # initializing the subpaths dictionary
        subpaths: dict = defaultdict(dict)

        # get the default max and min path lengths
        _min_length: int = min_length
        _max_length: int = max_length

        # if min_length is zero, account also for nodes
        if _min_length <= 0:
            for node in self.as_nodes:
                # generate empty path with one node
                subpaths[node] = Path.from_nodes([self.nodes[node]],
                                                 **self.attributes)

        # find the right path lengths
        min_length = max(_min_length, 1)
        max_length = min(len(self)-1, _max_length)

        # get subpaths
        for i in range(min_length-1, max_length):
            for j in range(len(self)-i):
                # get the edge uids
                edges = [self.edges[edge] for edge in self.as_edges[j:j+i+1]]
                # assign a new path based  on the given edges
                subpaths[self.separator.join(
                    self.as_edges[j:j+i+1])] = Path(*edges, **self.attributes)

        # include the path
        if include_path and _max_length >= len(self):
            subpaths[self.uid] = self

        # return the dict of subpaths
        return subpaths

    def has_subpath(self, subpath: Path) -> bool:
        """Return True if the path has a sub-path."""
        raise NotImplementedError

    def subpath(self, *args: str) -> Path:
        """Returns a sup-path of the path."""
        raise NotImplementedError

    def copy(self) -> Path:
        """Return a copy of the path.

        Returns
        -------
        Path
            A copy of the path.

        Examples
        --------
        >>> from pathpy import Path
        >>> p_1 = Path(uid='a')
        >>> p_2 = p_1.copy()
        >>> p_2.uid
        a

        """
        return deepcopy(self)

    @classmethod
    def from_nodes(cls, nodes: Sequence[Node], **kwargs: Any):
        """Generate a Path object from a list of nodes.

        Parameters
        ----------
        nodes: List[Node]

            Nodes from a list of: py: class: `Node` objects are added to the
            path.

        kwargs: Any, optional (default = {})
            Attributes assigned to the path as key = value pairs.

        Returns
        -------
        :py:class:`Path`
            Returns a :py:class:`Path` object with nodes and edges according to
            the given list of :py:class:`Nodes`.

        Examples
        --------
        Generate a simple path.

        >>> from pathpy import Path
        >>> p = Path.from_nodes(['a', 'b'])
        >>> p.nodes
        {'a': Node a, 'b': Node b}

        """
        path: Path = cls(**kwargs)
        path.add_nodes_from(nodes)
        return path

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
