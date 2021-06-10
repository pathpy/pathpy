#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : plot.py -- Plotting function for pathpy objects
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2021-06-10 16:25 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
import os
import importlib
from typing import Any, Optional, Dict
from pathpy import logger

# create logger for the Plot class
LOG = logger(__name__)


# supported backends
_backends: set = {'d3js', 'tikz', 'matplotlib'}

# supported file formats
_formats: Dict = {'.html': 'd3js', '.tex': 'tikz',
                  '.pdf': 'tikz', '.png': 'matplotlib'}


def plot(obj, filename, backend, **kwargs):
    pass


# def plot(data, kind, **kwargs):
#     # Importing pyplot at the top of the file (before the converters are
#     # registered) causes problems in matplotlib 2 (converters seem to not
#     # work)
#     import matplotlib.pyplot as plt

#     if kwargs.pop("reuse_plot", False):
#         ax = kwargs.get("ax")
#         if ax is None and len(plt.get_fignums()) > 0:
#             with plt.rc_context():
#                 ax = plt.gca()
#             kwargs["ax"] = getattr(ax, "left_ax", ax)
#     plot_obj = PLOT_CLASSES[kind](data, **kwargs)
#     plot_obj.generate()
#     plot_obj.draw()
#     return plot_obj.result


def network_plot(obj, filename: Optional[str] = None,
                 backend: Optional[str] = None, **kwargs: Any):
    """Plot a static network"""
    plot_backend = _get_plot_backend(backend, filename)
    plot_config = {filename}
    plot_data = {obj}
    return plot_backend.network_plot(plot_data, plot_config, **kwargs)


def _get_plot_backend(backend: Optional[str] = None, filename: str = None,
                      default: str = 'd3js'):
    """ Return the plotting backend to use. """

    _backend: str = default
    if isinstance(filename, str):
        _backend = _formats.get(os.path.splitext(filename)[1], default)

    # if no backend was found use the backend suggested for the file format
    if backend is not None and backend not in _backends and filename is not None:
        LOG.warning('The backend %s was not found.', backend)

    # if no backend was given use the backend suggested for the file format
    elif isinstance(backend, str) and backend in _backends:
        _backend = backend

    try:
        module = importlib.import_module('pathpy.visualisations._%s' % _backend)
    except ImportError:
        LOG.error('The %s backend could not be imported.', _backend)
        raise ImportError from None

    return module


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
