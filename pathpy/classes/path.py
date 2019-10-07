#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network.py -- Base class for a path
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2019-09-30 16:28 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, TypeVar, List
# from collections import defaultdict

from .. import logger, config
from . import Node, Edge, Network

# create logger for the Edge class
log = logger(__name__)

# create multi type for Nodes
NodeType = TypeVar('NodeType', Node, str)
EdgeType = TypeVar('EdgeType', Edge, str)


class Path(Network):
    """Base class for a path."""

    def __init__(self, *args: Any, directed: bool = True,
                 **kwargs: Any) -> None:
        """Initialize the network object."""

        # Classes of the Path objects
        # TODO: Probably there is a better solution to have different Path
        # classes for different Path sub classes
        self._path_class()

        # use separator if given otherwise use config default value
        self.separator: str = kwargs.get('separator', config.path.separator)

        # nodes and edges in the path
        self.path_nodes: List(str) = []
        self.path_edges: List(str) = []

        # initializing the parent network class
        super().__init__(directed=directed, **kwargs)

        # assign nodes to the path
        # TODO Make this also available for other types

        if len(args) > 0 and isinstance(args[0], list):
            super().add_nodes_from(args[0])

    def _path_class(self) -> Path:
        """Internal function to assign different Path classes."""
        self.PathClass = Path

    def __repr__(self) -> str:
        """Return the description of the path.

        Returns
        -------
        str
            Returns the description of the path with the class, the name (if
            deffined) and the assigned system id.

        Examples
        --------
        Genarate new network

        >>> from pathpy import Path
        >>> p = Path()
        >>> print(p)

        """
        return '<{} object {} at 0x{}x>'.format(self._desc(),
                                                self.name,
                                                id(self))

    def _desc(self):
        """Return a string *Path()*."""
        return '{}'.format(self.__class__.__name__)

    def __len__(self):
        """Returns the number of nodes in the path"""
        return len(self.path_nodes)

    def __eq__(self, other):
        """Returns True if two paths are equal.

        Here equality is defined by the number and order of nodes in the path!

        """
        return self.id == other.id

    def __hash__(self):
        """Returns the unique hash of the path.

        Here the hash value is defined by the string of nodes in the path!

        """
        return hash(self.id)

    @property
    def name(self):
        """Returns the name of the path.

        Name of the path. If no name is assigned the network is called after
        the assigned nodes. e.g. if the path has nodes 'a', 'b' and 'c', the
        path is named 'a-b-c'. The maximum length of the name is defined in the
        config file and is per default 5. E.g. if the path has 7 nodes
        (a,b,c,d,e,f,g) the name of the path is 'a-b-c-d-...-g'. Please, note
        the name of a path is NOT an unique identifier!

        Returns
        -------
        str
            Returns the name of the path as a string.

        """
        max_name_length = config.path.max_name_length
        if len(self) > max_name_length:
            _name = self.separator.join(
                self.path_nodes[0:-2][0:max_name_length]) \
                + self.separator + '...' + self.separator \
                + self.path_nodes[-1]
        else:
            _name = self.separator.join(self.path_nodes)

        return self.attributes.get('name', _name)

    @property
    def full_name(self):
        '''Returns the full name of the path

        Name of the path. If no name is assigned the path is called after the
        assigned nodes. e.g. if the path has nodes 'a', 'b' and 'c', the
        network is named 'a-b-c'.

        Returns
        -------
        str
            Returns the name of the path as a string.

        '''
        _name = self.separator.join(self.path_nodes)

        return self.attributes.get('name', _name)

    @property
    def id(self):
        """Returns the id of the path.

        Id of the path. If no id is assigned the path is called after the
        assigned nodes. e.g. if the path has nodes 'a', 'b' and 'c', the id is
        'a-b-c'.

        Returns
        -------
        str
            Returns the id of the path as a string.

        """
        _id = self.separator.join(self.path_nodes)

        return self.attributes.get('id', _id)

    def summary(self):
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
            'Path length (# nodes):\t{}'.format(len(self))
        ]
        if config.logging.enabled:
            for line in summary:
                log.info(line.rstrip())
        else:
            return ''.join(summary)

    def add_node(self, n: NodeType, **kwargs: Any) -> None:
        """Add a single node n and update node attributes.

        Add a single node to the path object. If a second node is added,
        automatically an edge is created between these two nodes.

        Parameters
        ----------
        n : str or :py:class:`Node`
            The parameter `n` is the node which should be added to the
            path. The parameter `n` can either be string value or a
            :py:class:`Node` object. If the parameter is a string value, a new
            node object is created where the node identifier (id) is the given
            value `n`. If the parameter is already a :py:class:`Node` object,
            it will be added to the network.

        kwargs : Any, optional (default = {})
            Attributes assigned to the node as key=value pairs.


        Examples
        --------
        Adding a singe new node to the network.

        >>> from pathpy import Node, Path
        >>> p = Path()
        >>> p.add_node('a',color='red')

        Adding an existing node object to the network.

        >>> b = Node('b',color='green')
        >>> p.add_node(b)

        An edge was generated between a and b

        >>> p.name
        a-b

        Notes
        -----
        If the same node is entered twice, a self loope will be generated.

        """
        # check if u is not a Node object
        if not isinstance(n, self.NodeClass):
            _node = self.NodeClass(n, **kwargs)
        else:
            _node = n
            _node.update(**kwargs)

        # check if node is already in the network
        if _node.id in self.nodes:
            self.path_nodes.append(_node.id)
        else:
            self.nodes[_node.id] = _node
            self.path_nodes.append(_node.id)

        # check if edge between nodes exist, if not add edge automatically
        if len(self) >= 2:
            v = self.path_nodes[-2]
            # check if edge exists
            if not super().has_edge(v, _node.id):

                # add new edge to the path
                super().add_edge(v, _node)

                # add edge id to the path
                self.path_edges.append(
                    super().node_to_edges_map[(v, _node.id)][0])

    def add_edge(self, *args: Any, **kwargs: Any) -> None:
        """Add an edge e between node v and node w.

        With the :py:meth:`add_edge` an :py:class:`Edge` object is added to the
        path. Thereby the edge must be connected to the predecessor
        edge. Furthermore, mutliple input options are available.

        1. `add_edge(e, v, w)`:
            The first way to add an edge is via the triplet edge `e`, source
            node `v` and target node `w`. Thereby, the `e` is the string value
            of the edge id and `v` and `w` are either the string values of the
            node ids or :py:class:`Node` objects.

        2. `add_edge(v, w)`:
            The second way to add an edge is via a tuple of source node `v` and
            target node `w`. Thereby, `v` and `w` are either the string values
            of the node ids or :py:class:`Node` objects. Thereby the edge id is
            the combination of the node ids separated via the
            `separator`. e.g. an edge between nodes 'v' and 'w' is generated,
            with edge id 'v-w'.

        3. `add_edge(e)`:
            The thrid way to add an edge is directly add an :py:class:`Edge`
            object. Thereby, all properties of the edge object
            (e.g. corresponding nodes) are taken from the object.

        Parameters
        ----------
        e : str or py:class:`Edge`
            The parameter `e` describes the edge which schould be added to the
            path. The parameter `e` can either be a string value, a
            :py:class:`Edge` object, or not defined. If the parameter is a
            string value, a new edge object is created given that also node
            parameters are given. Thereby, the edge identifier (id) is the
            string value. If the parameter is already a :py:class:`Edge`
            object, it will be added to the path. If the edge is not defined
            but two node parameter are given, an edge based on the nodes is
            generated, i.e. the edge id is created based on the node ids.

        v : str or :py:class:`Node`
            The parameter `v` is the source node of the edge, which should be
            added to the path. The parameter `v` can either be string value,
            a :py:class:`Node` object or not defined. If the parameter is a
            string value, a new node object is created where the node
            identifier (id) is the given value `v`. If the parameter is already
            a :py:class:`Node` object, it will be added to the path. If the
            node is not defined an :py:class:`Edge` object has to be given.

        w : str or :py:class:`Node`
            The parameter `w` is the target node of the edge, which should be
            added to the path. The parameter `w` can either be string value,
            a :py:class:`Node` object or not defined. If the parameter is a
            string value, a new node object is created where the node
            identifier (id) is the given value `w`. If the parameter is already
            a :py:class:`Node` object, it will be added to the path. If the
            node is not defined an :py:class:`Edge` object has to be given.

        separator : str, optional, config (default = '-')
            If no edge id is provide, an edge id is generated based on the node
            ids, Thereby the edge id is the combination of the node ids
            separated via the `separator`. e.g. an edge between nodes 'v' and
            'w' is generated, with edge id 'v-w'.

        kwargs : Any, optional (default = {})
            Attributes assigned to the edge as key=value pairs.

        Examples
        --------
        Adding a singe new edge to the path.

        >>> from pathpy import Edge, Path
        >>> p = Path()
        >>> p.add_edge('ab','a','b', length = 10)

        Adding an existing edge object to the path.

        >>> e = Edge('bc','b','c', length = 5)
        >>> p.add_edge(e)

        """

        # check the inputs
        # returns a dict with
        # variable = {'id':str, 'object':class, 'given':bool}
        e, v, w = self._check_edge(*args, **kwargs)

        # generate a temporal edge object
        _edge = self._get_temporal_edge(e, v, w, **kwargs)

        # check if node v is already in the network
        if _edge.v.id not in self.nodes:
            self.nodes[_edge.v.id] = _edge.v

        # check if node w is already in the network
        if _edge.w.id not in self.nodes:
            self.nodes[_edge.w.id] = _edge.w

        # check if this is the first entry in the path
        if len(self) < 1:
            self._add_edge(_edge)
            self.path_nodes.append(_edge.v.id)
            self.path_nodes.append(_edge.w.id)
            self.path_edges.append(_edge.id)

        # check if edge is connected to previous edge in the path
        elif self.path_nodes[-1] == _edge.v.id:
            self._add_edge(_edge)
            self.path_nodes.append(_edge.w.id)
            self.path_edges.append(_edge.id)

        # check order of undirected edge
        elif not self.directed and \
                (self.path_nodes[-1] == _edge.v.id or
                 self.path_nodes[-1] == _edge.w.id):
            if self.path_nodes[-1] == _edge.v.id:
                self.path.append(_edge.w.id)
                self.path_edges.append(_edge.id)
                self._add_edge(_edge)
            else:
                self.path.append(_edge.v.id)
                self.path_edges.append(_edge.id)
                self._add_edge(_edge)
        # raise error of edge is not connected
        else:
            log.error('Edge "{}" with nodes "({},{})", is not connected to the'
                      ' previous edge with nodes "({},{})!"'
                      ''.format(_edge.id, _edge.v.id, _edge.w.id,
                                self.path_nodes[-2], self.path_nodes[-1]))
            raise AttributeError

    def remove_node(self, n: str) -> None:
        """Remove node n and all adjacent edges."""
        raise NotImplementedError

    def remove_nodes_from(self, nodes: List(str)) -> None:
        """Remove multiple nodes."""
        raise NotImplementedError

    def remove_edge(self, *args: Any) -> None:
        """Remove the edge e between u and v."""
        raise NotImplementedError

    def remove_edges_from(self, edges: List(str)) -> None:
        """Remove all edges specified in edges."""
        raise NotImplementedError

    def has_subpath(self, subpath: Any, mode: str = 'nodes') -> bool:
        """Return True if the path has a sub path.

        Parameters
        ----------
        subpath : list of node or edge ids or a :py:class:`Path` object
            The sub path is a list of consecutive nodes or edges describing the
            path.

        mode : str, 'nodes' or 'edges', optional (default = 'nodes')
            The mode defines how the sup path is defined, i.e. as a list of
            node ids or a list of edge ids. If the sub path is a path object,
            the mode does not matter.

        Examples:
        ---------
        >>> from pathpy import Path
        >>> p = Path(['a','b','c','d'])
        >>> p.has_subpath(['a','b'])
        True

        Test other path object

        >>> q = Path(['d','e'])
        >>> p.has_subpath(q)
        False

        Test edges.

        >>> p.has_subpath(['a-b','b-c'], mode='edges')
        True

        """
        # check if subpath is a path object
        if isinstance(subpath, self.PathClass):
            _subpath = subpath.path_nodes
        else:
            # TODO: check also if nodes and edges are Node or Edge classes.
            if mode == 'edges':
                try:
                    _subpath = self.edges_to_path(subpath)
                except Exception:
                    return False
            else:  # default mode == 'nodes'
                _subpath = subpath
        # check if all elements of the sub path are in the path
        if set(_subpath).issubset(set(self.path_nodes)):
            # check the order of the elements
            # consider also elements which appear multiple times in the path
            idx = [i for i, x in enumerate(self.path_nodes)
                   if x == _subpath[0]]
            return any(all(self._check_path(i+j, v) for j, v in
                           enumerate(_subpath)) for i in idx)
        else:
            return False

    def _check_path(self, index, value):
        """Help function to check of the index exist"""
        try:
            return self.path_nodes[index] == value
        except Exception:
            return False

    def edges_to_path(self, edges: List(EdgeType)) -> List(NodeType):
        """Returns a list of node ids representing the path.

        Parameters
        ----------
        edges : list of edge ids
            The path defined as a list of consecutive edges.

        Returns
        -------
        List(NodeType)
            Returns a list of node ids representing the path object

        Raises
        ------
        An error will be raised if there is no corresponding path.

        """
        if isinstance(edges, str):
            edges = [edges]

        # TODO: Something is wrong here
        e2n = self.edge_to_nodes_map
        try:
            # add first edge
            _path = [e2n[edges[0]][0], e2n[edges[0]][1]]
            # add remaining edges
            _path += [e2n[edges[e]][1] for e in range(1, len(edges))]
            # return path
            return _path
        except Exception:
            log.error('The edges "{}" could not be mapped to the path "{}"!'
                      ''.format('-'.join(edges), self.name))
            raise

    def path_to_edges(self, id: bool = True):
        """Returns a list of edge ids representing the path.

        """
        n2e = self.node_to_edges_map
        _edges = []
        for i in range(len(self)-1):
            _edge = n2e[(self.path[i], self.path[i+1])]
            if len(_edge) > 1:
                log.warning('More than one edge was found between node {} and'
                            ' {}'.format(self.path[i], self.path[i+1]))
            if not id:
                _edges.append(self.edges[_edge[0]])
            else:
                _edges.append(self.edges[_edge[0]].id)
        return _edges

    def subpath(self, subpath: Any, mode: str = 'nodes') -> Path:
        """Returns a sup path of the path.

        Parameters
        ----------
        subpath : list of node or edge ids
            The sub path is a list of consecutive nodes or edges describing the
            path.

        mode : str, 'nodes' or 'edges', optional (default = 'nodes') The
            mode defines how the sup path is defined, i.e. as a list of node
            ids or a list of edge ids. If the sub path is a path object, the
            mode does not matter.

        Returns
        -------
        :py:class:`Path`
            Returns a Path object containing the sub path and the attributes of
            the parent path object.

        Examples
        --------
        >>> from pathpy import Path
        >>> p = Path(['a','b','c','d'])
        >>> q = p.subpath(['a','b','c'])
        >>> q.name
        a-b-c

        Sub path from edge list

        >>> q = p.subpath(['c-d'])
        >>> q.name
        c-d

        """
        # check if the sub path is in the path
        if self.has_subpath(subpath, mode=mode):
            if mode == 'edges':
                _subpath = self.edges_to_path(subpath)
            else:  # default mode == 'nodes'
                _subpath = subpath
        else:
            log.error('Path "{}" has not sub path "{}"!'
                      ''.format(self.name, '-'.join(subpath)))
            raise ValueError

        # create a new path opject
        subpath = self.PathClass()

        # copy the attributes of the parent path
        subpath.update(**self.attributes)

        # get node dict to map the edges
        n2e = super().node_to_edges_map

        # go thought the sub path and add the edges
        for i in range(len(_subpath)-1):
            _e = self.edges[n2e[_subpath[i], _subpath[i+1]][0]]
            subpath.add_edge(_e)

        return subpath

    def subpaths(self, min_length: int = None, max_length: int = None,
                 include_path: bool = False) -> List(str):
        """Returns a paths object with all sub paths.

        Parameters
        ----------

        min_length : int, optional (default = None)
            Parameter which defines the minimum length of the sub paths. This
            parameter has to be smaller then the maximum length parameter.

        max_length : int, optional (default = None)
            Parameter which defines the maximum  length of the sub paths. This
            parameter has to be greater then the minimum length parameter. If
            the parameter is also greater then the maximum length of the path,
            the maximum path length is used instead.

        include_path : bool, optional (default = Flase)
            If this option is enabled also the current path is added as a
            sub path of it self.

        Returns
        -------
        List(str)
            Returns a paths object containing all the sub paths fulfilling the
            length criteria.

        Examples
        --------
        >>> from pathpy import Path
        >>> p = Path(['a','b','c','d','e'])
        >>> P = p.subpaths()
        >>> for q in P:
        ...     print(q.name)
        a-b
        b-c
        c-d
        d-e
        a-b-c
        b-c-d
        c-d-e
        a-b-c-d
        b-c-d-e

        >>> P = p.subpaths(min_length = 3, max_length = 3)
        >>> for q in P:
        >>>     print(q.name)
        a-b-c
        b-c-d
        c-d-e

        Note
        ----
        If the minimum length is larger then the maximum length, an error will
        raised. If the maximum length is larger then the actual path length,
        the actual path length will be used.

        """
        if min_length is None:
            min_length = 1
        if max_length is None:
            max_length = len(self)-1
        if min_length > max_length:
            log.error('The minimum path length {} must be smaller then the '
                      'maximum path length {}!'.format(min_length, max_length))
            raise ValueError
        max_length = min(max_length, len(self)-1)
        min_length = max(min_length, 2)

        subpaths = []
        for i in range(min_length-1, max_length):
            for j in range(len(self)-i):
                _id = self.separator.join(self.path_nodes[j: j+i+1])
                subpaths.append(_id)

        if len(subpaths) == 0 and len(self) == 2:
            subpaths.append(self.id)
        elif len(self) <= max_length+1 and include_path:
            subpaths.append(self.id)

        # TODO: Return a object not a list
        # if len(subpaths) == 0 and len(self) == 2:
        #     subpaths.add_path(self.copy())
        # elif len(self) <= max_length+1 and include_path:
        #     subpaths.add_path(self.copy())

        # subpaths = Paths(name='sub paths of '+self.name)
        # for i in range(min_length-1, max_length):
        #     for j in range(len(self)-i):
        #         subpaths.add_path(self.subpath(self.path[j:j+i+1]))

        # if len(subpaths) == 0 and len(self) == 2:
        #     subpaths.add_path(self.copy())
        # elif len(self) <= max_length+1 and include_path:
        #     subpaths.add_path(self.copy())

        return subpaths

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
