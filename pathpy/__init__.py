"""Pathpy"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : __init__.py -- pathpy init file
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2020-09-17 08:33 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
# flake8: noqa
# pylint: disable=unused-import
__version__ = '3.0.0a2'

# import os
import sys

# import utils
from pathpy.utils.config import config  # noqa: F401
from pathpy.utils.logger import logger  # noqa: F401
from pathpy.utils.progress import tqdm  # noqa: F401


# import symbols into root namespace
from pathpy.core.api import (Node,
                             Edge,
                             HyperEdge,
                             Path,
                             PathCollection,
                             Network,
                             )


from pathpy.models.api import (TemporalNetwork,
                               DirectedAcyclicGraph,
                               HigherOrderNetwork,
                               NullModel,
                               MultiOrderModel
                               )

from pathpy.visualisations.api import (plot,
                                       layout)

# import models
# from pathpy.models.api import (NullModel,
#                                MultiOrderModel)
from pathpy.models.api import (MOGen)


# import submodules
from pathpy import io
from pathpy import converters
from pathpy import algorithms
from pathpy import statistics
from pathpy import processes
from pathpy import generators


from .__about__ import (
    __title__,
    __version__,
    __author__,
    __email__,
    __copyright__,
    __license__,
    __maintainer__,
    __status__
)

# create logger for the the init file
LOG = logger(__name__)

# check in which environment pathpy is running
try:
    from IPython import get_ipython  # noqa: F401
except ModuleNotFoundError:
    config['environment']['IDE'] = 'console'
    config['environment']['interactive'] = False
else:
    try:
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

LOG.debug('pathpy version %s', __version__)
LOG.debug('platform is %s', sys.platform)
LOG.debug('pathpy runs in a %s environment', config['environment']['IDE'])

if config['environment']['IDE'] == 'vs code':
    _html = """
    <script charset="utf-8">
    // Load via requireJS if available (jupyter notebook environment)
    try {
    require.config({
    paths: {
    d3: "https://d3js.org/d3.v5.min.js".replace(".js", "")
    }
    });
    console.log("OKAY: requireJS was detected");
    }
    catch(err){
    console.log(err);
    console.log("ERROR: NO requireJS was detected");
    };
    require(['d3'], function(d3){
    console.log("OKAY: d3js was detected");
    });
    </script>
    """

    try:
        from IPython.display import display, HTML
        display(HTML(_html))
    except ImportError:
        pass
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
