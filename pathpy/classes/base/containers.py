#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : containers.py -- Base containers for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-10-31 12:05 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List, Dict, Optional, Sequence
from collections import defaultdict, Counter

import pandas as pd


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

    def data_frame(self) -> pd.DataFrame:
        """Return a pandas data frame of all objects."""
        data = [obj.attributes.data for obj in self.values()]
        return pd.DataFrame(data)

    def counter(self) -> Counter:
        """Return a counter of the objects."""
        data = {k: self._counter[k] for k in self.keys()}
        return Counter(data)


class NodeDict(BaseDict):
    """Base class to store node objects."""

    def __init__(self, *args: Any) -> None:
        """Initialize the NodeDict object."""

        # initialize the base class
        super().__init__(*args)


class EdgeDict(BaseDict):
    """Base class to store edge objects."""

    def __init__(self, *args: Any) -> None:

        # initialize the base class
        super().__init__(*args)

    def data_frame(self) -> pd.DataFrame:
        """Return a pandas data frame of all edges."""
        data = [dict(obj.attributes.df, **{'v': obj.v.uid,
                                           'w': obj.w.uid})
                for obj in self.values()]
        return pd.DataFrame(data)


class PathDict(BaseDict):
    """Base class to store path objects."""

    def __init__(self, *args: Any) -> None:

        # initialize the base class
        super().__init__(*args)

    def data_frame(self) -> pd.DataFrame:
        """Return a pandas data frame of all paths."""
        data = [dict(obj.attributes.df, **{'len': len(obj)})
                for obj in self.values()]
        return pd.DataFrame(data)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End: