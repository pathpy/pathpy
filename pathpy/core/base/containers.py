#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : containers.py -- Base containers for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2020-03-31 16:35 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List, Dict, Optional, Sequence
from collections import defaultdict, Counter

import pandas as pd
from ... import config, logger

log = logger(__name__)


class RelatedObjects:
    def __init__(self) -> None:
        """Initialize the BaseDict object."""
        self.nodes = dict()
        self.edges = dict()
        self.paths = set()

    def update(self, other):
        self.nodes.update(other.nodes)
        self.edges.update(other.edges)
        self.paths.update(other.paths)

    def add_edge(self, edge):
        self.edges[edge.uid] = edge

    def remove_edge(self, edge):
        del self.edges[edge.uid]

    def add_node(self, node):
        self.nodes[node.uid] = node

    def remove_node(self, node):
        del self.nodes[node.uid]

    def add_path(self, path):
        self.paths[path.uid] = path

    def remove_path(self, path):
        self.paths = {p for p in self.paths}
        self.paths.remove(path)


class BaseDict(defaultdict):
    """Base class to store pathpy objects."""

    def __init__(self, *args: Any) -> None:
        """Initialize the BaseDict object."""

        # initialize related objects dictionary
        self._related: defaultdict = defaultdict(dict)

        # generate counter
        self._counter: defaultdict = defaultdict(int)

        # initialize the base class
        super().__init__(*args)

    def __setitem__(self, key, value):
        self._related[key] = RelatedObjects()
        defaultdict.__setitem__(self, key, value)

    def delete(self, key):
        del self._related[key]
        del self[key]

    @property
    def related(self):
        return self._related

    def increase_counter(self, key, count: int) -> None:
        """Increase the object counter."""

        # if key is a string update single object
        if isinstance(key, str):
            self._counter[key] += count
        # otherwise update a list of objects
        else:
            for k in key:
                self._counter[k] += count

    def decrease_counter(self, key, count: int) -> None:
        """Decrease the object counter."""

        # if key is a string update single object
        if isinstance(key, str):
            self._counter[key] -= count
        # otherwise update a list of objects
        else:
            for k in key:
                self._counter[k] -= count

    def to_frame(self) -> pd.DataFrame:
        """Return a pandas data frame of all objects."""
        # data = [obj.attributes.to_dict() for obj in self.values()]
        # return pd.DataFrame(data)
        data: List = []
        # iterate throug all stored objects
        for obj in self.values():

            # get the attributes
            _df = obj.attributes.to_frame()

            # check if attributes are available
            if _df.empty:
                # if not make a new entry with the object uid
                _df = pd.DataFrame()
                _df['uid'] = [obj.uid]
            else:
                # otherwise add uid to the data frame
                _df.insert(0, 'uid', obj.uid)

            # append the data frame
            data.append(_df)

        # return the new data frame
        if len(data) > 0:
            return pd.concat(data, ignore_index=True, sort=False)
        else:
            return pd.DataFrame()

    def counter(self) -> Counter:
        """Return a counter of the objects."""
        data: Dict = {k: self._counter[k] for k in self.keys()}
        return Counter(data)


class TemporalDict(BaseDict):
    """Base class to store temporal objects"""

    def __init__(self, *args: Any) -> None:
        """Initialize the TemporalDict object."""

        # initialize the base class
        super().__init__(*args)

    @property
    def temporal(self):
        """Returns true if a temporal object is observed."""
        return any([v.attributes.temporal for v in self.values()])

    def to_temporal_frame(self, frequency=None, interpolate=[], **kwargs):

        # check in which unit the time shoudl be stored
        if frequency is None:
            frequency = config['temporal']['unit']

        # initialize varialbes
        data: List = []

        # get data frame of all objects
        df = self.to_frame()

        # get global start and end times
        start = df['time'].min()
        end = df['time'].max()

        # get frequency of time stamps
        # TODO: add function to find time
        frequency = frequency

        # generate a temporal index from the start to the end time
        index = pd.date_range(start=start, end=end, freq=frequency)

        # assign start time to objects which don't have attributes
        df.loc[df['time'].isnull(), 'status'] = 'start'
        df.loc[df['time'].isnull(), 'active'] = True
        df['time'] = df['time'].fillna(start)

        # re-index time by the nearest given time frame

        _index = index.to_series()

        def nearest(items, pivot):
            return min(items, key=lambda x: abs(x - pivot))

        df['time'] = df['time'].apply(lambda x: nearest(_index, x))

        # set the time as index
        df = df.set_index('time')

        # group data frame by uids
        df = df.groupby('uid')

        # iterate over all groups
        for uid, group in df:

            # if no end time is given add the last observed time
            if group['active'].iat[-1]:
                group = group.append(
                    pd.DataFrame(
                        group[-1:].values,
                        index=[end],
                        columns=group.columns),
                    sort=False)
                # change the status at the end
                group.at[group.index[-1], 'status'] = 'end'

            # resample group by the given time frame
            group = (
                group
                # make sub-group based on the object activities
                .groupby((group['status'] == 'start').cumsum())
                # resample values in the sub-groups
                .apply(lambda group: group.asfreq(freq=frequency))
                .reset_index(level=0, drop=True)
                .sort_index()
            )

            # interpolate values
            for key in interpolate:
                group[key] = group[key].interpolate(
                    method='linear',
                    limit_direction='forward'
                )

            # fill the remaining missing values
            group['status'] = group['status'].fillna(value='active')

            group = (
                group
                .fillna(method='ffill')
                .fillna(method='bfill')
            )

            # append the group to the data
            data.append(group)

        # combine different objects
        df = (pd.concat(data, ignore_index=False, sort=False)
              .rename_axis('time').reset_index())

        # return new data frame
        return df


class NodeDict(TemporalDict):
    """Base class to store node objects."""

    def __init__(self, *args: Any) -> None:
        """Initialize the NodeDict object."""

        # initialize the base class
        super().__init__(*args)

        # initialize nodes attributes
        self._attributes = defaultdict(dict)
        self._attributes['successors'] = defaultdict(dict)
        self._attributes['predecessors'] = defaultdict(dict)
        self._attributes['outgoing'] = defaultdict(dict)
        self._attributes['incoming'] = defaultdict(dict)
        self._attributes['adjacent_nodes'] = defaultdict(dict)
        self._attributes['adjacent_edges'] = defaultdict(dict)
        self._attributes['indegrees'] = defaultdict(float)
        self._attributes['outdegrees'] = defaultdict(float)
        self._attributes['degrees'] = defaultdict(float)

    def add_edges(self, edges):
        for edge in edges.values():
            self.add_edge(edge, edges.related[edge.uid])

    def add_edge(self, edge, other=None):
        v = edge.v
        w = edge.w

        if v.uid not in self._related:
            self._related[v.uid] = RelatedObjects()
        if w.uid not in self._related:
            self._related[w.uid] = RelatedObjects()

        if other is not None:
            self._related[v.uid].update(other)
            self._related[w.uid].update(other)

        self._related[v.uid].add_edge(edge)
        self._related[w.uid].add_edge(edge)

        self._related[v.uid].add_node(w)
        self._related[w.uid].add_node(v)

        self._attributes['successors'][v.uid][w.uid] = edge.w
        self._attributes['adjacent_nodes'][v.uid][w.uid] = edge.w
        self._attributes['outgoing'][v.uid][edge.uid] = edge
        self._attributes['adjacent_edges'][v.uid][edge.uid] = edge

        self._attributes['predecessors'][w.uid][v.uid] = edge.v
        self._attributes['adjacent_nodes'][w.uid][v.uid] = edge.v
        self._attributes['incoming'][w.uid][edge.uid] = edge
        self._attributes['adjacent_edges'][w.uid][edge.uid] = edge

        self._update_degrees(v.uid)
        self._update_degrees(w.uid)

        self.update({v.uid: v})
        self.update({w.uid: w})

    def remove_edge(self, edge):
        v = edge.v
        w = edge.w

        self._related[v.uid].remove_edge(edge)
        self._related[w.uid].remove_edge(edge)

        # Fix this for multi edges
        self._related[v.uid].remove_node(w)
        self._related[w.uid].remove_node(v)

        del self._attributes['successors'][v.uid][w.uid]
        del self._attributes['adjacent_nodes'][v.uid][w.uid]
        del self._attributes['outgoing'][v.uid][edge.uid]
        del self._attributes['adjacent_edges'][v.uid][edge.uid]

        del self._attributes['predecessors'][w.uid][v.uid]
        del self._attributes['adjacent_nodes'][w.uid][v.uid]
        del self._attributes['incoming'][w.uid][edge.uid]
        del self._attributes['adjacent_edges'][w.uid][edge.uid]

        self._update_degrees(v.uid)
        self._update_degrees(w.uid)

    def remove_path(self, path):
        for node in path.nodes:
            self._related[node].remove_path(path)

    def delete(self, key):
        del self._attributes['successors'][key]
        del self._attributes['predecessors'][key]
        del self._attributes['adjacent_nodes'][key]
        del self._attributes['outgoing'][key]
        del self._attributes['incoming'][key]
        del self._attributes['adjacent_edges'][key]
        del self._attributes['indegrees'][key]
        del self._attributes['outdegrees'][key]
        del self._attributes['degrees'][key]
        del self._related[key]
        del self[key]

    def _update_degrees(self, key):
        tuples = [('indegrees', 'incoming'),
                  ('outdegrees', 'outgoing'),
                  ('degrees', 'adjacent_edges')]
        for degree, edges in tuples:
            self._attributes[degree][key] = len(
                self._attributes[edges][key])

    @property
    def successors(self):
        """Retuns a dict with sets of successors."""
        return self._attributes['successors']

    @property
    def predecessors(self):
        """Retuns a dict with sets of predecessors."""
        return self._attributes['predecessors']

    @property
    def outgoing(self):
        """Retuns a dict with sets of outgoing edges."""
        return self._attributes['outgoing']

    @property
    def incoming(self):
        """Retuns a dict with sets of incoming edges."""
        return self._attributes['incoming']

    @property
    def adjacent_nodes(self):
        """Retuns a dict with sets of adjacent nodes."""
        return self._attributes['adjacent_nodes']

    @property
    def adjacent_edges(self):
        """Retuns a dict with sets of adjacent edges."""
        return self._attributes['adjacent_edges']

    def _degrees(self, degree, edges, weight):
        """Helper function to get the degrees"""
        if weight is None:
            d = self._attributes[degree]
        else:
            d = defaultdict(float)
            for uid in self:
                d[uid] = sum([e.weight(weight)
                              for e in self._attributes[edges][uid].values()])
        return d

    def indegrees(self, weight=None):
        """Retuns a dict with indegrees of the nodes."""
        return self._degrees('indegrees', 'incoming', weight)

    def outdegrees(self, weight=None):
        """Retuns a dict with outdegrees of the nodes."""
        return self._degrees('outdegrees', 'outgoing', weight)

    def degrees(self, weight=None):
        """Retuns a dict with degrees of the nodes."""
        return self._degrees('degrees', 'adjacent_edges', weight)


class EdgeDict(TemporalDict):
    """Base class to store edge objects."""

    def __init__(self, *args: Any) -> None:

        # initialize the base class
        super().__init__(*args)

    def add_edges(self, edges):
        for edge in edges.values():
            self.add_edge(edge, edges.related[edge.uid])

    def add_edge(self, edge, other=None):
        if edge.uid not in self._related:
            self._related[edge.uid] = RelatedObjects()
        if other is not None:
            self._related[edge.uid].update(other)

        self._related[edge.uid].add_node(edge.v)
        self._related[edge.uid].add_node(edge.w)

        self.update({edge.uid: edge})

    def remove_path(self, path):
        for edge in path.edges:
            self._related[edge].remove_path(path)

    def to_frame(self) -> pd.DataFrame:
        """Return a pandas data frame of all edges."""
        df = super().to_frame()

        if not df.empty:
            df['v'] = df['uid'].apply(lambda x: self[x].v.uid)
            df['w'] = df['uid'].apply(lambda x: self[x].w.uid)

        return df

    @property
    def directed(self):
        """Returns true if edges are directed."""
        _directed = None
        if all([v.directed for v in self.values()]):
            _directed = True
        elif not any([v.directed for v in self.values()]):
            _directed = False
        return _directed


class PathDict(BaseDict):
    """Base class to store path objects."""

    def __init__(self, *args: Any) -> None:

        # initialize the base class
        super().__init__(*args)

    def add_path(self, path):
        if path.uid not in self._related:
            self._related[path.uid] = RelatedObjects()

        for node in path.nodes.values():
            self._related[path.uid].add_node(node)
        for edge in path.edges.values():
            self._related[path.uid].add_edge(edge)

        self.update({path.uid: path})

    def to_frame(self) -> pd.DataFrame:
        """Return a pandas data frame of all paths."""
        data = [dict(obj.attributes.to_dict(), **{'len': len(obj)})
                for obj in self.values()]
        return pd.DataFrame(data)

    def lengths(self) -> Counter:
        """Return a dictionary of path uids where key is the length."""
        data = defaultdict(list)
        for obj in self.values():
            data[len(obj)].append(obj.uid)
        return data


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
