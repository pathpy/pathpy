"""Progressbar for pathpy."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : progress.py -- A progress bar for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Sun 2020-04-19 07:32 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from typing import Any
from tqdm import tqdm as tq  # pylint: disable=import-error
from tqdm.notebook import tqdm as tqn  # pylint: disable=import-error
from pathpy import config


def tqdm_disabled(it, *args, **kwargs):
    """Disable the progress bar and return initial iterator."""
    return it


def tqdm_console(*args, **kwargs):
    """Progressbar for a console environment."""
    if len(args[0]) > config['progress']['min_iter']:
        return tq(*args, **kwargs)
    else:
        return args[0]


def tqdm_notebook(*args, **kwargs):
    """Progressbar for a notebook environment."""
    if len(args[0]) > config['progress']['min_iter']:
        return tqn(*args, **kwargs)
    else:
        return args[0]


# overwrite original tqdm typing
tqdm: Any

# if progress is enabled show bar
if config['progress']['enabled']:
    if config['environment']['interactive'] and config['environment']['IDE'] != 'vs code':
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
