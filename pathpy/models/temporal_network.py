"""Temporal network class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : temporal_network.py -- Class for temporal networks
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2021-05-20 09:52 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional, Union, cast
from collections import defaultdict
from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9
# import pandas as pd
# import numpy as np

from collections.abc import MutableMapping

from pathpy import logger, config
from pathpy.core.node import Node, NodeCollection
from pathpy.core.edge import Edge, EdgeCollection
from pathpy.models.network import Network

# from pathpy.core.base.attributes import TemporalAttributes

from pathpy.models.classes import BaseTemporalNetwork

# # pseudo load class for type checking
# if TYPE_CHECKING:
#     from pathpy.core.edge import EdgeSet


# create logger for the Network class
LOG = logger(__name__)
TIMESTAMP = config['temporal']['timestamp']


# class Timestamp:
#     """Class to store timestamps."""

class TemporalDict(MutableMapping):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""

    def __init__(self, *args, **kwargs):
        self._store = dict()
        self._start = kwargs.pop('start', float('-inf'))
        self._end = kwargs.pop('end', float('inf'))
        self._dt = kwargs.pop('delta', 1)
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        return self._store[self._keytransform(key)]

    def __setitem__(self, key, value):
        self._store[self._keytransform(key)] = value

    def __delitem__(self, key):
        del self._store[self._keytransform(key)]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def __repr__(self):
        return self._store.__repr__()

    @singledispatchmethod
    def _keytransform(self, key):
        """Helper function to generate the correct key"""
        return (self._start, self._end, key)

    @_keytransform.register(tuple)  # type: ignore
    def _(self, key: tuple) -> tuple:
        """
        TODO: explain what is happening here
        """

        if len(key) == 2:
            if isinstance(key[0], (slice, int, float)):
                _key = (key[0], key[1])
            elif len(key) == 2 and isinstance(key[-1], (slice, int, float)):
                _key = (key[1], key[0])
            else:
                raise KeyError

            start, end, _ = _get_start_end(_key[0])
            key = (start, end, _key[1])
        elif len(key) == 1:
            start, end, _ = _get_start_end()
            key = (start, end, key[0])
        elif len(key) != 3:
            raise KeyError

        return key

    def update(self, *args, **kwargs):
        """Update the TemporalDict"""
        if args and isinstance(args[0], TemporalDict):
            for key, value in dict(*args, **kwargs).items():
                self.__setitem__(key, value)
        else:
            for key, value in dict(**kwargs).items():
                self.__setitem__((*args, key), value)

    def sort(self):
        """Sort the keys"""
        self._store = dict(
            sorted(self._store.items(), key=lambda item: item[0]))
        return self


def _get_start_end(*args, **kwargs):
    """Helper function to extract the start and end time"""

    # get keywords defined in the config file
    start = kwargs.pop(config['temporal']['start'], float('-inf'))
    end = kwargs.pop(config['temporal']['end'], float('inf'))
    timestamp = kwargs.pop(config['temporal']['timestamp'], None)
    duration = kwargs.pop(config['temporal']['duration'], None)

    # check if timestamp is given
    if isinstance(timestamp, (int, float)):
        if isinstance(duration, (int, float)):
            start = timestamp
            end = timestamp + duration
        else:
            start = timestamp
            end = timestamp + config['temporal']['duration_value']

    if args:
        if len(args) == 1 and isinstance(args[0], slice):
            start = args[0].start if args[0].start is not None else start
            end = args[0].stop if args[0].stop is not None else end
        elif len(args) == 1 and isinstance(args[0], (int, float)):
            start = args[0]
            end = args[0] + config['temporal']['duration_value']
        elif len(args) == 2 and all(isinstance(a, (int, float)) for a in args):
            start = args[0]
            end = args[1]
    return start, end, kwargs


# class TemporalAttributes:
#     """Activities of temporal objects"""

#     def __init__(self):

#         self.attributes = pd.DataFrame(columns=['interval', 'key', 'value'])
#         self._dt = 1

#     def __repr__(self) -> str:
#         """Return the description of the underlying data frame."""
#         return self.attributes.__repr__()

#     @ singledispatchmethod
#     def __setitem__(self, key, value) -> None:
#         """Set single item."""
#         raise NotImplementedError

#     # @__setitem__.register(slice)  # type: ignore
#     # @__setitem__.register(int)  # type: ignore
#     # @__setitem__.register(float)  # type: ignore
#     # def _(self, key: Union[slice, int, float], value: bool) -> None:
#     #     start, stop = self._time(key)
#     #     self._setitem(start, stop, 'active', value)

#     @ __setitem__.register(tuple)  # type: ignore
#     def _(self, key: tuple, value: Any) -> None:

#         if isinstance(key[0], (slice, int, float)):
#             key = (key[0], key[1])
#         elif isinstance(key[-1], (slice, int, float)):
#             key = (key[1], key[0])
#         else:
#             raise AttributeError

#         start, stop = self._time(key[0])

#         self._setitem(start, stop, key[1], value)

#     @ __setitem__.register(str)  # type: ignore
#     def _(self, key: str, value: Any) -> None:

#         start, stop = self._time(None)

#         return self._setitem(start, stop, key, value)

#     def _setitem(self, start, stop, key, value) -> None:
#         """Helper function to set the item value"""
#         self.attributes = self.attributes.append(
#             {'interval': pd.Interval(start, stop), 'key': key, 'value': value},
#             ignore_index=True)

#     def _time(self, time) -> tuple:
#         """Helper function to get the start and stop time."""
#         if isinstance(time, slice):
#             start = time.start if time.start is not None else -float('inf')
#             stop = time.stop if time.stop is not None else float('inf')
#         elif isinstance(time, (int, float)):
#             start = time
#             stop = time + self._dt
#         else:
#             start = -float('inf')
#             stop = float('inf')
#         return start, stop

#     @ singledispatchmethod
#     def __getitem__(self, key):
#         """Get single item."""
#         raise NotImplementedError

#     @ __getitem__.register(slice)  # type: ignore
#     @ __getitem__.register(int)  # type: ignore
#     @ __getitem__.register(float)  # type: ignore
#     def _(self, key: Union[slice, int, float]) -> pd.DataFrame:

#         start, stop = self._time(key)
#         return self._getitem(start, stop, key=None)

#     @ __getitem__.register(tuple)  # type: ignore
#     def _(self, key: tuple) -> pd.DataFrame:

#         if isinstance(key[0], (slice, int, float)):
#             key = (key[0], key[1])
#         elif isinstance(key[-1], (slice, int, float)):
#             key = (key[1], key[0])
#         else:
#             raise AttributeError

#         start, stop = self._time(key[0])

#         return self._getitem(start, stop, key=key[1])

#     @ __getitem__.register(str)  # type: ignore
#     def _(self, key: str) -> pd.DataFrame:

#         start, stop = self._time(None)

#         return self._getitem(start, stop, key=key)

#     def _getitem(self, start, stop, key=None):
#         """Helper function to get the item"""
#         data = self.attributes
#         item = None

#         if key and key in list(self.attributes['key']):
#             data = self.attributes[self.attributes['key'] == key]
#         elif key is not None:
#             return pd.DataFrame(
#                 {'interval': [pd.Interval(start, stop)],
#                  'key': [key], 'value': [None]})

#         # if key in list(self.activities['key']):
#         item = data[
#             (data
#              .set_index('interval')
#              .index.overlaps(pd.Interval(start, stop))
#              )]

#         return item

#     def update(self, uid: str = None, **kwargs: Any) -> None:
#         """Update the values"""

#         if kwargs:
#             start, end, kwargs = _time(**kwargs)
#             # active = kwargs.pop('active', True)

#             # self._setitem(start, end, 'active', active)

#             for key, value in kwargs.items():
#                 self._setitem(start, end, key, value)

#     def get(self, key, default: Any = None) -> Any:
#         """Get item from object for given key."""
#         return self[key]


# class TemporalActivities(TemporalAttributes):
#     """Activities of temporal objects"""

#     @ singledispatchmethod
#     def __setitem__(self, key, value) -> None:
#         """Set single item."""
#         raise NotImplementedError

#     @ __setitem__.register(slice)  # type: ignore
#     @ __setitem__.register(int)  # type: ignore
#     @ __setitem__.register(float)  # type: ignore
#     def _(self, key: Union[slice, int, float], value: bool) -> None:
#         start, stop = self._time(key)
#         self._setitem(start, stop, 'active', value)

#     def update(self, uid: str = None, **kwargs: Any) -> None:
#         """Update the values"""

#         if kwargs:
#             start, end, kwargs = _time(**kwargs)
#             active = kwargs.pop('active', True)

#             self._setitem(start, end, 'active', active)


class TemporalNode(Node):
    """Base class of a temporal node."""

    def __init__(self, uid: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the node object."""

        # initialize the parent class
        super().__init__(uid=uid)

        self.attributes = TemporalDict()
        self.activities = TemporalDict()
        self.update(active=True, **kwargs)

    def update(self, *args, active: bool = False, **kwargs: Any) -> None:
        """Update the attributes of the object. """

        start, end, kwargs = _get_start_end(*args, **kwargs)

        self.attributes.update(start, end, **kwargs)
        if active:
            self.activities[start, end, self.uid] = self

    def active(self, *args, **kwargs) -> None:
        """Activate node."""
        start, end, kwargs = _get_start_end(*args, **kwargs)
        self.activities[start, end, self.uid] = self


class TemporalEdge(Edge):
    """Base class of an temporal edge."""

    def __init__(self, v: TemporalNode, w: TemporalNode,
                 uid: Optional[str] = None, **kwargs: Any) -> None:

        # initializing the parent class
        super().__init__(v=v, w=w, uid=uid)

        self.attributes = TemporalDict()
        self.activities = TemporalDict()
        self.update(active=True, **kwargs)

    def update(self, *args, active: bool = False, **kwargs: Any) -> None:
        """Update the attributes of the object. """

        start, end, kwargs = _get_start_end(*args, **kwargs)

        self.attributes.update(start, end, **kwargs)
        if active:
            self.activities[start, end, self.uid] = self

    def active(self, *args, **kwargs) -> None:
        """Activate edge"""
        start, end, kwargs = _get_start_end(*args, **kwargs)
        self.activities[start, end, self.uid] = self


class TemporalNodeCollection(NodeCollection):
    """A collection of temporal nodes"""

    def __init__(self) -> None:
        """Initialize the NodeCollection object."""

        # initialize the base class
        super().__init__()

        # class of objects
        self._node_class: Any = TemporalNode

    def _if_exist(self, node: Any, **kwargs: Any) -> None:
        """Helper function if node already exists."""
        # get the node
        if isinstance(node, str):
            _node = cast(TemporalNode, self[node])
            _node.update(active=True, **kwargs)
        elif isinstance(node, TemporalNode):
            pass
        else:
            raise KeyError

        # update the node


class TemporalEdgeCollection(EdgeCollection):
    """A collection of temporal edges"""

    def __init__(self, directed: bool = True, multiedges: bool = False,
                 nodes: Optional[TemporalNodeCollection] = None) -> None:
        """Initialize the network object."""

        # collection of nodes
        self._nodes: TemporalNodeCollection = TemporalNodeCollection()
        if nodes is not None:
            self._nodes = nodes

        # initialize the base class
        super().__init__(directed=directed, multiedges=multiedges,
                         nodes=nodes)

        # class of objects
        self._node_class: Any = TemporalNode
        self._edge_class: Any = TemporalEdge

    def _if_exist(self, edge: Any, **kwargs: Any) -> None:
        """Helper function if edge already exists."""
        # get the edge

        if isinstance(edge, (tuple, list)):
            _edge = cast(TemporalEdge, self[edge[0], edge[1]])
            _edge.update(active=True, **kwargs)
        elif isinstance(edge, str):
            _edge = cast(TemporalEdge, self[edge])
            _edge.update(active=True, **kwargs)
        elif isinstance(edge, TemporalEdge):
            _edge = cast(TemporalEdge, self[edge.v, edge.w])
            _edge.attributes.update(edge.attributes)
            for key in edge.activities:
                _edge.activities[key[0], key[1], _edge.uid] = _edge
        else:
            raise KeyError


class TemporalNetwork(BaseTemporalNetwork, Network):
    """Base class for a temporal networks."""

    # # load external functions to the network
    # to_paths = to_paths.to_path_collection  # type: ignore

    def __init__(self, uid: Optional[str] = None,
                 directed: bool = True, multiedges: bool = False,
                 **kwargs: Any) -> None:
        """Initialize the temporal network object."""

        # initialize the base class
        super().__init__(uid=uid, directed=directed,
                         multiedges=multiedges, **kwargs)

        # # add network properties
        # self._properties['nodes'] = set()

        # a container for node objects
        self._nodes: TemporalNodeCollection = TemporalNodeCollection()

        # a container for edge objects
        self._edges: TemporalEdgeCollection = TemporalEdgeCollection(
            directed=directed,
            multiedges=multiedges,
            nodes=self._nodes)

    @property
    def tedges(self) -> TemporalDict:
        """Return a temporal dictionary of temporal edges"""

        tedges = TemporalDict()
        for active in [edge.activities for edge in self.edges]:
            tedges.update(active)

        return tedges.sort()

    @property
    def tnodes(self) -> TemporalDict:
        """Return a temporal dictionary of temporal nodes"""

        tnodes = TemporalDict()
        for active in [node.activities for node in self.nodes]:
            tnodes.update(active)

        return tnodes.sort()

    def start(self, inf: bool = False):
        """Start of the temporal network"""
        start, _ = self._get_start_end(self.tnodes, self.tedges, inf=inf)
        return start

    def end(self, inf: bool = False):
        """End of the temporal network"""
        _, end = self._get_start_end(self.tnodes, self.tedges, inf=inf)
        return end

    def _get_start_end(self, tnodes={}, tedges={}, inf: bool = False):
        """Helper function to get the start end end times"""

        keys = list(tnodes.keys()) + list(tedges.keys())
        start, end, _ = zip(*keys)
        start_times = sorted(list(set(start)))[:2]
        end_times = sorted(list(set(end)))[-2:]

        start = start_times[0]
        end = end_times[-1]
        if not inf:
            if start == float('-inf'):
                start = start_times[-1]
            if end == float('inf'):
                end = end_times[0]
        return start, end

    def summary(self) -> str:
        """Returns a summary of the network.

        The summary contains the name, the used network class, if it is
        directed or not, the number of nodes and edges.

        If logging is enabled (see config), the summary is written to the log
        file and showed as information on in the terminal. If logging is not
        enabled, the function will return a string with the information, which
        can be printed to the console.

        Returns
        -------
        str
            Returns a summary of important network properties.

        """

        tnodes = self.tnodes
        tedges = self.tedges
        start, end = self._get_start_end(tnodes, tedges)

        summary = [
            'Uid:\t\t\t{}\n'.format(self.uid),
            'Type:\t\t\t{}\n'.format(self.__class__.__name__),
            'Directed:\t\t{}\n'.format(str(self.directed)),
            'Multi-Edges:\t\t{}\n'.format(str(self.multiedges)),
            'Number of unique nodes:\t{}\n'.format(self.number_of_nodes()),
            'Number of unique edges:\t{}\n'.format(self.number_of_edges()),
            'Number of temp nodes:\t{}\n'.format(len(tnodes)),
            'Number of temp edges:\t{}\n'.format(len(tedges)),
            'Observation periode:\t{} - {}'.format(start, end)
        ]
        attr = self.attributes
        if len(attr) > 0:
            summary.append('\n\nNetwork attributes\n')
            summary.append('------------------\n')
        for k, v in attr.items():
            summary.append('{}:\t{}\n'.format(k, v))

        return ''.join(summary)


class OldTemporalEdgeCollection(EdgeCollection):
    """A collection of temporal edges"""

    def __init__(self, directed: bool = True, multiedges: bool = False,
                 nodes: Optional[TemporalNodeCollection] = None) -> None:
        """Initialize the network object."""

        # collection of nodes
        self._nodes: TemporalNodeCollection = TemporalNodeCollection()
        if nodes is not None:
            self._nodes = nodes

        # initialize the base class
        super().__init__(directed=directed, multiedges=multiedges,
                         nodes=nodes)

        # map intervals to edges
        self._intervals: IntervalTree = IntervalTree()

        # map edges to intervals
        self._interval_map: defaultdict = defaultdict(set)

    @ property
    def intervals(self):
        """Return an interval tree of the temporal edges."""
        return self._intervals

    def temporal(self):
        """Return a list of temporal edges."""
        return [(i.data.uid, i.data, i.begin, i.end)
                for i in sorted(self._intervals)]

    def _if_exist(self, edge: Any, **kwargs: Any) -> None:
        """Helper function if edge already exists."""
        # get the edge
        if isinstance(edge, (tuple, list)):
            _edge = cast(Edge, self[edge[0], edge[1]])
        elif isinstance(edge, (str, Edge)):
            _edge = cast(Edge, self[edge])
        else:
            raise KeyError
        begin = kwargs['begin']
        end = kwargs['end']

        if kwargs:
            _edge.update(**{**kwargs, **{TIMESTAMP: begin}})

        self._intervals.addi(begin, end, _edge)
        self._interval_map[_edge].add((begin, end))

    def _add(self, edge: Edge) -> None:
        """Add an edge to the set of edges."""
        begin = edge.attributes['begin']
        end = edge.attributes['end']

        # attributes = TemporalAttributes()
        # attributes.update(**{**edge.attributes.to_dict(), **{TIMESTAMP: begin}})
        # edge.attributes = attributes

        self._intervals.addi(begin, end, edge)
        self._interval_map[edge].add((begin, end))

        super()._add(edge)

    def items(self, temporal=False):
        """Return a new view of the edge’s items ((key, value) pairs)."""
        if not temporal:
            return self._map.items()
        else:
            return self.temporal()

    def __getitem__(self, key: Union[str, tuple, Edge]
                    ) -> Union[Edge, EdgeSet, TemporalEdgeCollection]:
        """Returns a edge object."""
        _item: Any
        if isinstance(key, (int, float, slice)):
            _item = self._new_from_intervals(self._intervals[key])
        else:
            _item = super().__getitem__(key)
        return _item

    def _new_from_intervals(self, intervals: IntervalTree) -> TemporalEdgeCollection:
        """Helper function which creates a new collection from an interval."""

        # TODO: FIX THIS EDGE ASSIGMENT
        new = TemporalEdgeCollection()
        for begin, end, uid in intervals:
            print('uid', uid)
            new.add(self[uid], begin=begin, end=end)

        # new = []
        # for begin, end, edge in intervals:
        #     print('uid', edge.uid)
        #     new.append((edge, begin, end))

        return new

    def slice(self, begin, end) -> TemporalEdgeCollection:
        """Return a temporal slice of the collection."""

        tree = self._intervals.copy()
        tree.slice(begin)
        tree.slice(end)
        tree.remove_envelop(self._intervals.begin(), begin)
        tree.remove_envelop(end, self._intervals.end())

        return self._new_from_intervals(tree)

    def begin(self, finite=True) -> float:
        """Begin time of the temporal edges."""

        _begin = self._intervals.begin()
        _end = float('inf')
        if finite:
            for b, _, _ in sorted(self._intervals):
                if b > float('-inf'):
                    _begin = b
                    break
            _end = sorted(self._intervals, key=lambda x: x[1])[0][1]
            if _begin == float('-inf') and _end < float('inf'):
                _begin = _end
        return min(_begin, _end)

    def end(self, finite=True) -> float:
        """End time if the temporal edges."""
        _begin = float('-inf')
        _end = self._intervals.end()
        if finite:
            for _, e, _ in sorted(self._intervals, key=lambda x: x[1],
                                  reverse=True):
                if e < float('inf'):
                    _end = e
                    break
            _begin = sorted(self._intervals)[-1][0]
            if _begin > float('-inf') and _end == float('inf'):
                _end = _begin
        return max(_begin, _end)


def _time(*args, **kwargs):
    """Helper function to extract the start and end time"""

    # get keywords defined in the config file
    start = kwargs.pop(config['temporal']['start'], float('-inf'))
    end = kwargs.pop(config['temporal']['end'], float('inf'))
    timestamp = kwargs.pop(config['temporal']['timestamp'], None)
    duration = kwargs.pop(config['temporal']['duration'], None)

    # check if timestamp is given
    if isinstance(timestamp, (int, float)):
        if isinstance(duration, (int, float)):
            start = timestamp
            end = timestamp + duration
        else:
            start = timestamp
            end = timestamp + config['temporal']['duration_value']

    return start, end, kwargs

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
