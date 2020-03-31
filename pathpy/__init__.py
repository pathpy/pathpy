#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : __init__.py -- pathpy init file
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2020-03-27 11:57 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
__version__ = '3.0.0a1'

from .__about__ import (  # noqa: F401
    __title__,
    __version__,
    __author__,
    __email__,
    __copyright__,
    __license__,
    __maintainer__,
    __status__
)

from pathpy.utils.config import config  # noqa: F401
from pathpy.utils.logger import logger  # noqa: F401
from pathpy.utils.progress import tqdm  # noqa: F401

from pathpy.core import *
from .algorithms import *
from .models import *
from .generators import *

from .visualizations import plot  # noqa: F401


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
