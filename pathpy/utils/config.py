#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : config.py -- Module to read and parse configuration files
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2019-10-09 11:16 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import os
from configparser import ConfigParser

# get pathpy base config
_base_config = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'config.cfg')

# setup config
config = ConfigParser()

# load config files
config.read([_base_config, 'config.cfg'])


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
