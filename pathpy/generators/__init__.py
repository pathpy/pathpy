"""Module for Graph generation."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : __init__.py -- Initialize generators
# Author    : Ingo Scholtes <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2020-04-20 12:26 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
# flake8: noqa
# pylint: disable=unused-import

from pathpy.generators.random_graphs import (ER_nm,
                                             ER_np,
                                             ER_nm_randomize,
                                             ER_np_randomize,
                                             Watts_Strogatz,
                                             is_graphic_Erdos_Gallai,
                                             Molloy_Reed,
                                             Molloy_Reed_randomize,
                                             max_edges,
                                             generate_degree_sequence,                                             
                                             )

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
