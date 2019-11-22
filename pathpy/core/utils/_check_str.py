#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : _check_str.py -- Helper function to check the str format
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2019-11-22 12:20 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any
from ... import logger, config


# create a logger
log = logger(__name__)


def _check_str(self, *args: Any, expected=None, **kwargs: Any) -> str:
    """Helper function to check input strings."""

    # initialize list of objects
    _objects = []
    _data = []
    _level = {'node': 0, 'edge': 1, 'path': 2, 'hon': 3}
    _separator = {v: self.separator.get(k, '') for k, v in _level.items()}
    if expected is None:
        expected_level = max(_level.values())
    else:
        expected_level = _level[expected]

    def _split(string, separator=config['object']['separator']):
        if separator in string:
            values = string.split(separator)
            observed = True
        else:
            values = [string]
            observed = False
        return string, observed, values

    def __reduce(n, values, stop=1):
        reduced = []

        for string in values:
            _, _, values = _split(string, _separator[n])
            reduced.append(values)
        if n == stop+1:
            return reduced[0]
        else:
            return __reduce(n-1, values, stop=stop)

    def _reduce(uid, from_mode='hon', to_mode='node'):
        return __reduce(_level[from_mode], uid, _level[to_mode])

    # split args
    if args and len(args) == 1:
        # TODO add "," to config file
        _objects = args[0].split(',')

    # otherwise get args as list
    else:
        _objects = [v for v in args]

    # get types of the objects
    # TODO: FIX THIS VERY UGLY CODE
    for string in _objects:

        uid = [string]
        # TODO: check also hon input more in detail (e.g. see path)
        if self.separator['hon'] in string:
            _data.append({'uid': uid, 'mode': 'hon', 'type': 'hon'})

        elif self.separator['path'] in string:
            if _level['path'] > expected_level:
                uid = _reduce(uid, from_mode='path', to_mode='edge')
                _data.append({'uid': uid, 'mode': 'path', 'type': 'edge'})
            else:
                _data.append({'uid': uid, 'mode': 'path', 'type': 'path'})

        elif (self.separator['edge'] in string and
                len(string.split(self.separator['edge'])) > 2):
            if _level['path'] > expected_level:
                uid = _reduce(uid, from_mode='path', to_mode='node')
                _data.append({'uid': uid, 'mode': 'path', 'type': 'node'})
            else:
                _data.append({'uid': uid, 'mode': 'path', 'type': 'path'})

        elif self.separator['edge'] in string:
            _data.append({'uid': uid, 'mode': 'edge', 'type': 'edge'})

        else:
            _data.append({'uid': uid, 'mode': 'node', 'type': 'node'})

    # return list with uids and estimated type
    return [(d['uid'], d['type']) for d in _data]


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
