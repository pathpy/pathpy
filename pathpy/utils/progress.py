#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : progress.py -- A progress bar for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2019-10-22 08:10 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from tqdm.auto import tqdm as _tqdm
from .. import config


class tqdm_disabled(_tqdm):
    """Progress bar based on tqdm.

    See Also
    --------
    https://github.com/tqdm/tqdm

    """

    def __init__(self, *args, **kwargs):
        """Intitialize the disabled progress bar."""
        # setup parent class
        super().__init__(*args, disable=True, **kwargs)


# if progress is enabled show bar
if config['progress']['enabled']:
    tqdm = _tqdm

# otherwise use the disable progress bar.
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
