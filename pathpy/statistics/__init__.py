"""Statistics module for pathpy"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : __init__.py -- Initialize statistics methods for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2020-08-31 07:16 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
# flake8: noqa
# pylint: disable=unused-import

from pathpy.statistics.degrees import (degree_sequence,
                                       degree_distribution,
                                       degree_assortativity,
                                       degree_central_moment,
                                       degree_raw_moment,
                                       degree_generating_function,
                                       mean_degree,
                                       mean_neighbor_degree,
                                       )

from pathpy.statistics.clustering import (local_clustering_coefficient,
                                          avg_clustering_coefficient,
                                          closed_triads,
                                          )

from pathpy.statistics.modularity import (Q_modularity,
                                          Q_max_modularity,
                                          Q_assortativity_coefficient,
                                          )

from pathpy.statistics import likelihoods

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
