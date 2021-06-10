"""Network plots with tikz"""
#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : network_plots.py -- Network plots with tikz
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2021-06-10 16:44 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from typing import Any, Optional


def network_plot(obj, filename: Optional[str] = None,
                 backend: Optional[str] = None, **kwargs: Any):
    """Plot a static network with tikz"""
    return 'tikz'

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
