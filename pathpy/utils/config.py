#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : config.py -- Module to read and parse configuration files
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2019-11-08 09:54 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import os
from configparser import ConfigParser
from collections import defaultdict

# get pathpy base config
_base_config = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'config.cfg')

# setup parser
parser = ConfigParser()

# load config files
parser.read([_base_config, 'config.cfg'])

# setup parser
config: dict = defaultdict(dict)


# TODO: Find a better way to load the config file.
config['logging']['enabled'] = parser.getboolean('logging', 'enabled')
config['logging']['verbose'] = parser.getboolean('logging', 'verbose')
config['logging']['level'] = parser.get('logging', 'level')

config['progress']['enabled'] = parser.getboolean('progress', 'enabled')
config['progress']['leave'] = parser.getboolean('progress', 'leave')

config['attributes']['history'] = parser.getboolean('attributes', 'history')
config['attributes']['multiple'] = parser.getboolean('attributes', 'multiple')
config['attributes']['frequency'] = parser.get('attributes', 'frequency')


config['computation']['check_code'] = parser.getboolean(
    'computation', 'check_code')

config['edge']['separator'] = parser.get('edge', 'separator')


config['path']['separator'] = parser.get('path', 'separator')
config['path']['max_name_length'] = parser.getint('path', 'max_name_length')
config['hon']['separator'] = parser.get('hon', 'separator')

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
