#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : attributes.py -- Class for pathpy attributes
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-10-31 12:15 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any
from collections import defaultdict

import pandas as pd

from ... import logger, config

# create logger
log = logger(__name__)


class Attributes:
    """Wrapper for the object attributes."""

    def __init__(self, uid: str = None, history: bool = None,
                 multi_attributes: bool = None, frequency: str = None,
                 ** kwargs: Any) -> None:
        """Initialize the attributes class."""

        # check if data history schould be recorded
        if history is None:
            self.history = config['attributes']['history']
        else:
            self.history = history

        # check multiple entries are shown
        if multi_attributes is None:
            self.multi_attributes = config['attributes']['multiple']
        else:
            self.multi_attributes = multi_attributes

        # check the variable name for the frequency
        if frequency is None:
            self._frequency = config['attributes']['frequency']
        else:
            self._frequency = frequency

        # save the uid of the associated object
        # TODO: remove uid variable
        self.uid = uid

        # create an index
        self.index = 0

        # create an empty data frame
        self.data: dict = defaultdict(dict)

        # initialize first row
        self.data[self.index].update(**kwargs)

    @property
    def frequency(self):
        """Returns the frequency of the object."""
        return self.get(self._frequency, 1)

    def _set_single_value(self, key: Any, value: Any) -> None:
        """Set a single value."""
        self.update(**{key: value})

    def _get_single_value(self, key: Any) -> Any:
        """Get single value."""
        return self.get(key)

    def _get_last_dict(self):
        """Returns the last dictionary."""
        return self.data[self.index]

    def __repr__(self) -> str:
        """Return the description of the underlying dict."""
        if self.multi_attributes:
            return self.data.__repr__()
        else:
            return self._get_last_dict().__repr__()

    def __setitem__(self, key: Any, value: Any, **kwargs) -> None:
        """Set single item."""
        if isinstance(key, str):
            self._set_single_value(key, value)
        elif isinstance(key, tuple):
            raise NotImplementedError

    def __getitem__(self, key: Any, **kwargs: Any) -> Any:
        """Get single item."""
        return self._get_single_value(key)

    def __eq__(self, other) -> bool:
        """Returns True if equal, otherwise False."""
        return self.to_dict() == other.to_dict()

    def update(self, uid: str = None, **kwargs: Any) -> None:
        """Update the attributes."""

        # update uid if defined
        if uid:
            self.uid = uid

        # update kwargs if given
        if kwargs:
            # if noting is defiend overwrite empty dict
            if ((len(self.data) == 1 and not self.data[self.index]) or
                    (not self.history)):

                # update attributes
                self.data[self.index].update(**kwargs)

            # otherwise add new row with updated values
            else:

                # increase index
                self.index += 1

                # update attributes
                self.data[self.index] = {**self.data[self.index-1], **kwargs}

    def get(self, key, default: Any = None) -> Any:
        """Get item from object for given key."""
        return self.data[self.index].get(key, default)

    def data_frame(self, history: bool = False):
        """Convert the attributes to a pandas DataFrame"""
        if (self.multi_attributes or history) and self.history:
            return pd.DataFrame.from_dict(self.data, orient='index')
        else:
            return pd.Series(self._get_last_dict(), name=self.uid)

    def to_dict(self, *args: Any, exclude: list = [],
                history: bool = False, transpose: bool = True) -> dict:
        """Convert the attributes to a dict."""
        # check if it is a multi-attribute or if the history is asked
        if (self.multi_attributes or history) and self.history:

            return self._filter_all(self.data, *args, exclude=exclude,
                                    transpose=transpose)

        else:
            return self._filter_single(self._get_last_dict(), *args,
                                       exclude=exclude)
            d = defaultdict(dict)
            for key, value in self._get_last_dict().items():
                if args:
                    if key in args and key not in exclude:
                        d[key] = value
                else:
                    if key not in exclude:
                        d[key] = value
            return d

    @staticmethod
    def _filter_all(dct, *args, exclude=[], transpose=False):
        """Helper function to filter the attributes with history."""
        d = defaultdict(dict)

        for key1, inner in dct.items():
            for key2, value in inner.items():
                if args:
                    if key2 in args and key2 not in exclude:
                        if transpose:
                            d[key2][key1] = value
                        else:
                            d[key1][key2] = value
                else:
                    if key2 not in exclude:
                        if transpose:
                            d[key2][key1] = value
                        else:
                            d[key1][key2] = value

        return d

    @staticmethod
    def _filter_single(dct, *args, exclude=[]):
        """Helper function to filter the attributes without history."""
        d = defaultdict(dict)

        for key, value in dct.items():
            if args:
                if key in args and key not in exclude:
                    d[key] = value
            else:
                if key not in exclude:
                    d[key] = value
        return d


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
