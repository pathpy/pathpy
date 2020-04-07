#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : progress.py -- A progress bar for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2019-11-08 15:25 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from typing import Any
from tqdm import tqdm as tq
from tqdm.notebook import tqdm as tqn
from pathpy import config

def tqdm_disabled(it, *args, **kwargs):
    return it

def tqdm_console(*args, **kwargs):
    return tq(*args, **kwargs)

def tqdm_notebook(*args, **kwargs):
    return tqn(*args, **kwargs)

# if progress is enabled show bar
if config['progress']['enabled']:
    if config['environment']['interactive'] and config['environment']['IDE']!='vs code':
        tqdm = tqdm_notebook
    else:
        tqdm = tqdm_console
else:
    tqdm = tqdm_disabled

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
