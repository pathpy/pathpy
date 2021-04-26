"""Base components for the core module."""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : __init__.py • base -- Initialize base constructurs for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2020-05-14 15:52 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
# flake8: noqa
# pylint: disable=unused-import

# from .attributes import (
#     Attributes,
#     TemporalAttributes
# )

from pathpy.core.collections import (
    BaseCollection,
)

from .classes import (
    BaseClass,
    BaseNode,
    BaseEdge,
    BasePath,
    BaseModel,
    # BaseNetwork,
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
