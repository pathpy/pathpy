#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : progress.py -- A progress bar for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2019-10-09 11:24 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from tqdm.auto import tqdm as _tqdm
from .. import config


class tqdm(_tqdm):
    """Progress bar based on tqdm.

    See Also
    --------
    https://github.com/tqdm/tqdm

    """

    def __init__(self, *args, **kwargs):
        """Intitialize the progress bar."""

        # if progress is enabled show bar
        if config.getboolean('progress', 'enabled'):
            _disable = False

            # otherwise disable progress.
        else:
            _disable = True

        # setup parent class
        super().__init__(*args, disable=_disable, **kwargs)
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
