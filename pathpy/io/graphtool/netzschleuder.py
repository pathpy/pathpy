#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : netzschleuder.py -- Module for data import/export from netzschleuder repository
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Wed 2021-04-20 12:29 ingo>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations
from pathpy.io.graphtool.graphtool import parse_graphtool_format
from typing import TYPE_CHECKING, Optional, Union


from pathpy import config, logger

from pathpy.models.network import Network

from urllib import request
from urllib.error import HTTPError
import json


# create logger
LOG = logger(__name__)


def list_netzschleuder_records(base_url='https://networks.skewed.de', **kwargs) -> Union[list, dict]:
    """
    Reads a list of data sets from the netzschleuder repository
    """ 
    url = '/api/nets'
    for k, v in kwargs.items():
        url += '?{0}={1}'.format(k, v)
    f = request.urlopen(base_url + url).read()
    return json.loads(f)


def read_netzschleuder_record(name: str, base_url='https://networks.skewed.de') -> dict:
    """
    Reads a single record 
    """ 
    url = '/api/net/{0}'.format(name)
    return json.loads(request.urlopen(base_url + url).read())


def read_netzschleuder_network(name: str, net: Optional[str]=None, ignore_temporal: Optional[bool]=False, base_url='https://networks.skewed.de') -> Network:
    """
    Reads a network from the netzschleuder repository
    """
    import zstandard as zstd 

    # retrieve network properties
    url = '/api/net/{0}'.format(name)
    properties = json.loads(request.urlopen(base_url + url).read())

    # retrieve data
    if not net:
        net = name
    url = '/net/{0}/files/{1}.gt.zst'.format(name, net)
    try:
        f = request.urlopen(base_url + url)
    except HTTPError:
        LOG.error('HTTP 404 Error. Did you specify the network to load from this data set?')
        return None

    # decompress data
    dctx = zstd.ZstdDecompressor()
    reader = dctx.stream_reader(f)
    decompressed = reader.readall()

    # parse graphtool binary format
    n = parse_graphtool_format(bytes(decompressed), ignore_temporal=ignore_temporal)
    if n:
        # store network attributes
        for k, v in properties.items():
            n[k] = v

    return n
