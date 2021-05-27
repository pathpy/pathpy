"""Module for temporal objects"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : temporal.py -- Classes to make PathPyObject temporal
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2021-05-27 13:19 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from typing import Any, Optional, Union
from singledispatchmethod import singledispatchmethod  # NOTE: not needed at 3.9
from intervaltree import IntervalTree
import pandas as pd

from pathpy import logger, config
from pathpy.core.core import PathPyObject

# create logger for the Path class
LOG = logger(__name__)


class TemporalPathPyObject(PathPyObject):
    """Base class for a temporal object."""

    def __init__(self, uid: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the temporal object."""

        # initialize the parent class
        super().__init__(uid=uid)

        # default start and end time of the object
        self._start = float('-inf')
        self._end = float('inf')

        # initialize an intervaltree to save events
        self._events = IntervalTree()

        # add new events
        self.event(**kwargs)

        # variable to store changes in the events
        self._len_events = len(self._events)

    def __iter__(self):
        self._clean_events()

        # create generator
        for start, end, attributes in sorted(self._events):
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
        start, end, _ = _get_start_end(key[0])
        values = {k: v for _, _, o in sorted(
            self._events[start:end]) for k, v in o.items()}
        return values.get(key[1], None) if len(key) == 2 else values

    @__getitem__.register(slice)  # type: ignore
    @__getitem__.register(int)  # type: ignore
    @__getitem__.register(float)  # type: ignore
    def _(self, key: Union[int, float, slice]) -> Any:
        start, end, _ = _get_start_end(key)
        self._clean_events()

        # create generator
        for start, end, attributes in sorted(self._events[start:end]):
            self._attributes = {**{'start': start, 'end': end}, **attributes}
            yield self

    @singledispatchmethod
    def __setitem__(self, key: Any, value: Any) -> None:
        self.event(start=self._events.begin(),
                   end=self._events.end(), **{key: value})

    @__setitem__.register(tuple)  # type: ignore
    def _(self, key: tuple, value: Any) -> None:
        start, end, _ = _get_start_end(key[0])
        self.event(start=start, end=end, **{key[1]: value})

    @property
    def start(self):
        """start of the object"""
        return self._start

    @property
    def end(self):
        """end of the object"""
        return self._end

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
        start, end, kwargs = _get_start_end(*args, **kwargs)

        if active:
            self._events[start:end] = kwargs  # type: ignore
            self._attributes = kwargs.copy()
        else:
            self._events.chop(start, end)

        # update start and end times
        self._start = self._events.begin()
        self._end = self._events.end()

    def last(self):
        """return the last added intervall"""
        interval = sorted(self._events)[-1]
        return interval.begin, interval.end, interval.data


def _get_start_end(*args, **kwargs) -> tuple:
    """Helper function to extract the start and end time"""

    # initialize start and end time
    start = kwargs.pop(config['temporal']['start'], float('-inf'))
    end = kwargs.pop(config['temporal']['end'], float('inf'))

    # convert str to pandas timestamp
    if isinstance(start, str):
        start = pd.Timestamp(start)
    if isinstance(end, str):
        end = pd.Timestamp(end)

    # check kwargs
    if kwargs:
        # get keywords defined in the config file
        timestamp = kwargs.pop(config['temporal']['timestamp'], None)
        duration = kwargs.pop(config['temporal']['duration'],
                              config['temporal']['duration_value'])
        unit = kwargs.pop('unit', config['temporal']['unit'])

        # check if timestamp is given
        if timestamp:
            if isinstance(timestamp, str):
                timestamp = pd.Timestamp(timestamp)
                if isinstance(duration, str):
                    duration = pd.Timedelta(duration)
                else:
                    duration = pd.Timedelta(duration, unit=unit)
            start = timestamp
            end = timestamp + duration

    # check args
    if args:
        if len(args) == 1 and isinstance(args[0], slice):
            start, end, _ = _get_start_end(
                start=args[0].start, end=args[0].stop)
        elif len(args) == 1:
            start, end, _ = _get_start_end(timestamp=args[0])
        elif len(args) == 2:
            start, end, _ = _get_start_end(start=args[0], end=args[1])

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
