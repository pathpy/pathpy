"""Module for graph generation."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : __init__.py -- Initialize generators
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Mon 2020-04-27 01:13 ingo>
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
                                             k_regular_random
                                             )
from pathpy.generators.lattice import (lattice_network)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
