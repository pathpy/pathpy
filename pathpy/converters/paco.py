#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : paco.py -- Implementation of the PaCo algorithm
# Author    : Luka Petrović <petrovic@ifi.uzh.ch>
# Time-stamp: <Sun 2020-10-04 10:01 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional, Union, cast
from collections import defaultdict

from pathpy import logger
from pathpy.core.path import PathCollection

# create logger for the Network class
LOG = logger(__name__)


def all_paths_from_temporal_data(tn,
                                 delta,
                                 skip_first=0,
                                 up_to_k=10):

    # all the entries that are at max distance delta away from the current entry
    delta_window = []

    path_stack = PathCollection()

    # current_path_stack[i][p] is the number of paths p that go from
    # current_edge of index i.
    current_path_stack = defaultdict(lambda: defaultdict(int))

    # for e, current_edge in enumerate(D):
    for e, (uid, edge, timestamp, end) in enumerate(tn.edges.items(temporal=True)):
        current_edge = (edge.v.uid, edge.w.uid, timestamp)
        # since we go in forward direction, delta window is back in time.
        # not every entry from delta window is important for the current
        # considered current_edge some are happening at the same time.

        # check if there is anything to update about delta window
        # and current stack
        if len(delta_window) > 0:
            # I throw away the ones in delta_window that are too far away
            # (in temporal sense)
            i = 0
            didnt_find_one_yet = True
            # since the data is sorted, I just need to find the one that
            # is inside the delta time window.
            # This while loop identifies the first entry saved in delta window,
            # that is inside the new delta window so it only loops through the
            # ones that are outside the new delta window.
            while i < len(delta_window) and didnt_find_one_yet:
                # i'th entry [i], then I need the entry,
                # and not the ennumerator [1],
                # and then I need time, which is the third column[2]
                if delta_window[i][1][2] >= current_edge[2]-delta:
                    didnt_find_one_yet = False
                else:
                    # i didn't find yet one which is inside the new delta window.
                    i += 1

            # keep all starting from the first that is inside the
            # new delta window.
            if i < len(delta_window):
                first_index_in_delta_window = delta_window[i][0]
                old_inx = [
                    e for (e, current_edge) in delta_window if e < first_index_in_delta_window]
                delta_window = delta_window[i:]
            else:
                # all from delta window should be removed.
                # asign current index
                first_index_in_delta_window = e
                old_inx = [
                    e for (e, current_edge) in delta_window if e < first_index_in_delta_window]
                delta_window = []
            # delta_window is now corresponding to the current_edge that I am
            # considering.
            # go through outdated indices
            for j in old_inx:
                # remove them from the current stack.
                del current_path_stack[j]
        # all stacks updated now.

        # compute for the next
        for enu, past_edge in delta_window:
            # if target of the link in delta_window is the same as the
            # source in considered entry
            if past_edge[1] == current_edge[0]:
                # the interactions should not happen at the same time!
                # the considered one should happen AFTER the one from the
                # delta window.
                if current_edge[2] > past_edge[2]:
                    # i know that the link happened in the appropriate time,
                    # and that the link continues the link I consider.
                    # so I can add the paths to the current_path_stack
                    for path in current_path_stack[enu]:
                        p = (*path, current_edge[1])
                        if len(p)-1 <= up_to_k:
                            current_path_stack[e][p] += current_path_stack[enu][path]

                            if e >= skip_first:
                                if p not in path_stack:
                                    path_stack.add(
                                        p, frequency=current_path_stack[enu][path])
                                else:
                                    path_stack[p]['frequency'] += current_path_stack[enu][path]
        current_path_stack[e][(current_edge[0], current_edge[1])] += 1

        if e >= skip_first:
            p = (current_edge[0], current_edge[1])
            print(p)
            if p not in path_stack:
                path_stack.add(p, frequency=1)
            else:
                path_stack[p]['frequency'] += 1

        # add this current_edge at the end of delta_window,
        # so that the next current_edge can have all the entries it needs.
        delta_window.append((e, current_edge))

    return path_stack

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
