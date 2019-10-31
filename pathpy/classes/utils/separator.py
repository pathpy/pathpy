#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : separator.py -- Util method for separating objects
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-10-31 11:45 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from typing import Any, Dict

from ... import config


def separator(mode=None, **kwargs: Any) -> Dict[str, str]:
    """Function to generate a dict with separators."""

    # initializing the separator
    separator = {}

    # list of objects
    objects = ['edge', 'path', 'hon']

    # get default values from the config file
    for obj in objects:
        separator[obj] = config[obj]['separator']

    # if a mode is specified check if an other separator is specified
    if mode is not None:
        _separator = {}

        for obj in objects:
            _separator[obj] = kwargs.get(obj+'_separator')

        _separator[mode] = kwargs.get('separator')

        for k, v in _separator.items():
            if v is not None:
                separator[k] = v

    # return the separator
    return separator


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
