"""Base components for the core module."""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : __init__.py • base -- Initialize base constructurs for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Sat 2020-04-18 10:24 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
# flake8: noqa
# pylint: disable=unused-import

# from .attributes import (
#     Attributes,
#     TemporalAttributes
# )

from .containers import (
    Properties,
    NodeContainer,
    EdgeContainer,
)

from .classes import (
    BaseNode,
    BaseEdge,
    BaseNetwork,
    # BaseHigherOrderNetwork,
    # BaseTemporalNetwork,
    # BaseStaticNetwork,
    # BaseDirectedNetwork,
    # BaseUndirectedNetwork,
    # BaseDirectedTemporalNetwork,
    # BaseUndirectedTemporalNetwork,
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
