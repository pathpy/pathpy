"""Module for temporal objects"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : temporal.py -- Classes to make PathPyObject temporal
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2021-05-21 10:27 juergen>
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
            self._events[self._start:self._end] = kwargs  # type: ignore
        else:
            self._events.chop(self._start, self._end)

    def start(self, total=False):
        """start of the object"""
        return self._events.begin() if total else self._start

    def end(self, total=False):
        """end of the object"""
        return self._events.end() if total else self._end


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
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
