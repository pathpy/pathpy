#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : __init__.py -- pathpy init file
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2020-04-07 13:00 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
# flake8: noqa
__version__ = '3.0.0a1'

import sys
import os

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

# import utils
from pathpy.utils.config import config  # noqa: F401
from pathpy.utils.logger import logger  # noqa: F401
from pathpy.utils.progress import tqdm  # noqa: F401

# import submodules
from pathpy import statistics
from pathpy import algorithms
from pathpy import processes
from pathpy import generators
from pathpy.core import io

# import symbols into root namespace
from pathpy.core.api import (Node,
                             Edge,
                             Path,
                             Network,
                             HigherOrderNode,
                             HigherOrderEdge,
                             HigherOrderNetwork,
                             )

from pathpy.models.api import (NullModel,
                               MultiOrderModel)

# create logger for the the init file
LOG = logger(__name__)

# check in which environment pathpy is running
try:
    from IPython import get_ipython
    if 'IPKernelApp' not in get_ipython().config:  # pragma: no cover
        ImportError("console")
except AttributeError:
    config['environment']['IDE'] = 'console'
    config['environment']['interactive'] = False
else:
    config['environment']['interactive'] = True

    # NOTE: Currently this is not working
    # https://github.com/tqdm/tqdm/issues/747
    # https://github.com/microsoft/vscode-python/issues/3429
    # if 'VSCODE_PID' in os.environ:  # pragma: no cover
    #     config['environment']['IDE'] = 'vs code'
    #     LOG.debug('pathpy runs in vs code')
    # else:
    #     config['environment']['IDE'] = 'jupyter notebook'
    #     LOG.debug('pathpy runs in jupyter notebook')

LOG.debug('pathpy version {}'.format(__version__))
LOG.debug('platform is {}'.format(sys.platform))
LOG.debug('pathpy runs in a {} environment'.format(
    config['environment']['IDE']))

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
