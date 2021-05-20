"""Temporal network class"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : temporal_network.py -- Class for temporal networks
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2021-05-20 18:51 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, Optional, Union, cast, Tuple
from collections import defaultdict
from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9
import pandas as pd
# import numpy as np

from intervaltree import IntervalTree

from collections.abc import MutableMapping

from pathpy import logger, config
from pathpy.core.core import PathPyObject
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


def _get_start_end(*args, **kwargs) -> tuple:
    """Helper function to extract the start and end time"""

    # get keywords defined in the config file
    start = kwargs.pop(config['temporal']['start'], float('-inf'))
    end = kwargs.pop(config['temporal']['end'], float('inf'))
    timestamp = kwargs.pop(config['temporal']['timestamp'], None)
    duration = kwargs.pop(config['temporal']['duration'], None)

    if isinstance(start, str):
        start = pd.Timestamp(start)
    if isinstance(end, str):
        end = pd.Timestamp(end)

    # check if timestamp is given
    if isinstance(timestamp, (int, float)):
        start = timestamp
        if isinstance(duration, (int, float)):
            end = timestamp + duration
        else:
            end = timestamp + config['temporal']['duration_value']
    elif isinstance(timestamp, str):
        start = pd.Timestamp(timestamp)
        if isinstance(duration, str):
            end = start + pd.Timedelta(duration)
        else:
            end = start + pd.Timedelta(config['temporal']['duration_value'],
                                       unit=config['temporal']['unit'])

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


class TemporalIterator:

    def __init__(self, obj):
        # object reference
        self._obj = obj

        # iterator over the temporal relations
        self._iter = iter(obj._temp_relations)

    def __iter__(self):
        return self

    def __next__(self):
        ''''Returns the next value from the temporal relations object '''
        # if self._index < self._stop:
        start, end, uid = next(self._iter)

        return self._obj


class TemporalNode(Node):
    """Base class of a temporal node."""

    def __init__(self, *node: Union[str, PathPyObject],
                 uid: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the node object."""

        # initialize the parent class
        super().__init__(*node, uid=uid)

        self._start = float('-inf')
        self._end = float('inf')

        # initialize an intervaltree to save events
        self._events = IntervalTree()

        # add new events
        self.event(**kwargs)

        # variable to store changes in the events
        self._len_events = len(self._events)

    def __iter__(self):
        # clean events
        self._clean_events()

        # create generator
        for start, end, attributes in sorted(self._events):
            # update start and end time as well as attributes
            self._start, self._end = start, end
            self._attributes = {**{'start': start, 'end': end}, **attributes}
            yield self

    @singledispatchmethod
    def __getitem__(self, key: Any) -> Any:
        self._clean_events()

        # get the last element
        *_, last = iter(self._events)
        return last.data.get(key, None)

    @__getitem__.register(tuple)  # type: ignore
    def _(self, key: tuple) -> Any:
        return {k: v for o in self.__getitem__(key[0]) for
                k, v in o.attributes}.get(key[1], None) if (
                    len(key) == 2 and isinstance(
                        key[0], (int, float, slice))) else None

    @__getitem__.register(slice)  # type: ignore
    @__getitem__.register(int)  # type: ignore
    @__getitem__.register(float)  # type: ignore
    def _(self, key: Union[int, float, slice]) -> Any:

        for start, end, attributes in sorted(self._events[key]):
            # update start and end time as well as attributes
            self._start, self._end = start, end
            self._attributes = {**{'start': start, 'end': end}, **attributes}
            yield self

        # return {k: v for d in sorted(
        #     self._events[key]) for k, v in d.data.items()}

    @singledispatchmethod
    def __setitem__(self, key: Any, value: Any) -> None:
        self.event(start=self.start(total=True),
                   end=self.end(total=True), **{key: value})

    @__setitem__.register(tuple)  # type: ignore
    def _(self, key: tuple, value: Any) -> None:
        if len(key) == 2:
            if isinstance(key[0], (int, float)):
                self.event(timestamp=key[0], **{key[1]: value})
            elif isinstance(key[0], slice):
                self.event(start=key[0].start,
                           end=key[0].stop, **{key[1]: value})
            else:
                raise KeyError
        else:
            raise KeyError

    def _clean_events(self):
        """helper function to clean events"""
        def reducer(old, new):
            return {**old, **new}

        if len(self._events) != self._len_events:
            # split overlapping intervals
            self._events.split_overlaps()

            # combine the dict of the overlapping intervals
            self._events.merge_equals(data_reducer=reducer)

            # update the length of the events
            self._len_events = len(self._events)

    def event(self, *args, **kwargs) -> None:
        """Add a temporal event."""

        # check if object is avtive or inactive
        active = kwargs.pop('active', True)

        # get start and end time of the even
        self._start, self._end, kwargs = _get_start_end(*args, **kwargs)

        if active:
            self._events[self._start:self._end] = kwargs
        else:
            self._events.chop(self._start, self._end)

    def start(self, total=False):
        """start of the object"""
        return self._events.begin() if total else self._start

    def end(self, total=False):
        """end of the object"""
        return self._events.end() if total else self._end


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
                    ) -> Union[Edge, TemporalEdgeCollection]:
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
