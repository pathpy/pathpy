#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : plot.py -- Module to plot networks as a tikz-network
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2020-03-25 13:32 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
import os
from .. import logger
from .easel import D3JS, PDF, CSV, TEX, PNG
from .utils import _check_filename

log = logger(__name__)

def _repr_html_(network):
    easel = D3JS()
    easel.draw(network)
    easel.show()

def plot(network, filename: str=None, **kwargs):
    """Plots a network."""

    if filename==None:     
        easel = D3JS()
        easel.draw(network, **kwargs)
        easel.show(**kwargs)
    else:
        easel_classes = {'html': D3JS, 'csv': CSV,
                        'tex': TEX, 'pdf': PDF, 'png': PNG}
        format_str = filename.split('.')[-1]
        easel = easel_classes[format_str]()
        easel.draw(network, **kwargs)
        easel.save(filename=filename)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
