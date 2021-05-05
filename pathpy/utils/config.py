#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : config.py -- Module to read and parse configuration files
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2021-04-21 10:00 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import os
from configparser import ConfigParser
from collections import defaultdict

__all__ = ['config']

# get pathpy base config
_base_config = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'config.cfg')

# setup parser
parser = ConfigParser()

# load config files
parser.read([_base_config, 'config.cfg'])

# setup parser
config: dict = defaultdict(dict)

config['environment']['IDE'] = parser.get('environment', 'IDE')
config['environment']['interactive'] = parser.getboolean(
    'environment', 'interactive')

# TODO: Find a better way to load the config file.
config['logging']['enabled'] = parser.getboolean('logging', 'enabled')
config['logging']['verbose'] = parser.getboolean('logging', 'verbose')
config['logging']['level'] = parser.get('logging', 'level')

config['progress']['enabled'] = parser.getboolean('progress', 'enabled')
config['progress']['min_iter'] = parser.getint('progress', 'min_iter')
config['progress']['leave'] = parser.getboolean('progress', 'leave')

config['attributes']['history'] = parser.getboolean('attributes', 'history')
config['attributes']['multiple'] = parser.getboolean('attributes', 'multiple')
config['attributes']['frequency'] = parser.get('attributes', 'frequency')


config['computation']['check_code'] = parser.getboolean(
    'computation', 'check_code')

config['object']['separator'] = parser.get('object', 'separator')

config['edge']['separator'] = parser.get('edge', 'separator')
config['edge']['replace'] = parser.get('edge', 'replace')
config['edge']['v_synonyms'] = parser.get('edge', 'v_synonyms').split(", ")
config['edge']['w_synonyms'] = parser.get('edge', 'w_synonyms').split(", ")


config['path']['separator'] = parser.get('path', 'separator')
config['path']['replace'] = parser.get('path', 'replace')
config['path']['max_name_length'] = parser.getint('path', 'max_name_length')
config['hon']['separator'] = parser.get('hon', 'separator')
config['hon']['replace'] = parser.get('hon', 'replace')

# config['temporal']['begin'] = parser.get('temporal', 'begin')
config['temporal']['start'] = parser.get('temporal', 'start')
config['temporal']['end'] = parser.get('temporal', 'end')
config['temporal']['timestamp'] = parser.get('temporal', 'timestamp')
config['temporal']['duration'] = parser.get('temporal', 'duration')
config['temporal']['duration_value'] = parser.getfloat(
    'temporal', 'duration_value')
config['temporal']['active'] = parser.get('temporal', 'active')
config['temporal']['is_active'] = parser.getboolean('temporal', 'is_active')
config['temporal']['unit'] = parser.get('temporal', 'unit')
config['temporal']['start_synonyms'] = parser.get(
    'temporal', 'start_synonyms').split(", ")
config['temporal']['end_synonyms'] = parser.get(
    'temporal', 'end_synonyms').split(", ")
config['temporal']['timestamp_synonyms'] = parser.get(
    'temporal', 'timestamp_synonyms').split(", ")
config['temporal']['duration_synonyms'] = parser.get(
    'temporal', 'duration_synonyms').split(", ")

config['MOGen']['paths_per_chunk'] = parser.getint('MOGen', 'paths_per_chunk')

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
