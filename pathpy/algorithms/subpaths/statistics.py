#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : statistics.py -- Module for sub-path statistics
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2019-10-31 11:07 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Any, List, Dict, Tuple, Optional
from functools import singledispatch
from collections import Counter
import datetime
import sys

from ...classes.base import BaseNetwork, BaseHigherOrderNetwork

from ... import logger

# create logger for the Edge class
log = logger(__name__)


@singledispatch
def subpath_info(self):
    raise NotImplementedError('Unsupported class')


@subpath_info.register(BaseNetwork)
def _(self):
    log.debug('I\'m a Network')
    log.debug('start generate subpath statistics')
    a = datetime.datetime.now()

    path_counter = self.paths.counter()
    # observed paths of length k
    op = Counter()
    for uid, count in path_counter.items():
        op[len(uid.split(self.separator['path']))] += count

    print('op', op)

    # unique paths of length k
    up = Counter()
    for uid in self.paths:
        up[len(uid.split(self.separator['path']))] += 1

    print(up)

    # subpaths of length k
    sp = Counter()

    # NOTE: Very time consuming method!
    spc = self.subpath_counter()

    # print(spc)
    for uid, count in spc.items():

        # print(uid, count)
        split = uid.split(self.separator['path'])
        if len(split) == 1:
            if split[0] in self.nodes:
                sp[0] += count
            elif split[0] in self.edges:
                sp[1] += count

        elif len(split) >= 2:
            sp[len(split)] += count

    print(sp)

    # get max length
    max_length = max(max(up), max(sp))
    min_length = min(min(up), min(sp))
    for i in range(min_length, max_length+1):
        _values = {
            'k': i-min_length,
            'op': op[i],
            'up': up[i],
            'sp': sp[i],
            'tp': op[i] + sp[i]
        }
        print('k={k}: {op} / {up} / {sp} / {tp}'.format(**_values))

    # total paths of length k

    b = datetime.datetime.now()
    log.debug('end generate subpath statistics:' +
              ' {} seconds'.format((b-a).total_seconds()))


# @sub_info.register(BaseHigherOrderNetwork)
# def _(self):
#     log.debug('I\'m a HigherOrderNetwork')

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
