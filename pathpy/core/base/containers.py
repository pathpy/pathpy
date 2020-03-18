#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : containers.py -- Base containers for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2020-03-18 08:49 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List, Dict, Optional, Sequence
from collections import defaultdict, Counter

import pandas as pd
from ... import config


class BaseDict(defaultdict):
    """Base class to store pathpy objects."""

    def __init__(self, *args: Any) -> None:
        """Initialize the BaseDict object."""

        # generate counter
        self._counter: defaultdict = defaultdict(int)

        # initialize the base class
        super().__init__(*args)

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


class EdgeDict(TemporalDict):
    """Base class to store edge objects."""

    def __init__(self, *args: Any) -> None:

        # initialize the base class
        super().__init__(*args)

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
