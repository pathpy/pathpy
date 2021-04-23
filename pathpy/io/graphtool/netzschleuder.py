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
from pathpy.models.temporal_network import TemporalNetwork
from pathpy.io.graphtool.graphtool import parse_graphtool_format
from typing import TYPE_CHECKING, Optional, Union

from pathpy import config, logger

from pathpy.models.network import Network

from urllib import request
from urllib.error import HTTPError
import json

# create logger
LOG = logger(__name__)


def list_netzschleuder_records(base_url: str='https://networks.skewed.de', **kwargs) -> Union[list, dict]:
    """Reads a list of data sets available at the netzschleuder repository.

    Parameters
    ----------
    
    base_url: str='https://networks.skewed.de'

        Base URL of netzschleuder repository
    
    **kwargs

        Keyword arguments that will be passed to the netzschleuder repository as HTTP GET parameters. 
        For supported parameters see https://networks.skewed.de/api


    Examples
    --------
    Return a list of all data sets

    >>> import pathpy as pp
    >>> pp.io.graphtool.list_netzschleuder_records()
    ['karate', 'reality_mining', 'sp_hypertext', ...]

    Return a list of all data sets with a given tag

    >>> pp.io.graphtool.list_netzschleuder_records(tags='temporal')
    ['reality_mining', 'sp_hypertext', ...]

    Return a dictionary containing all data set names (keys) as well as all network attributes
    
    >>> pp.io.graphtool.list_netzschleuder_records(full=True)
    { 'reality_mining': [...], 'karate': [...] }


    Returns
    -------

    Either a list of data set names or a dictionary containing all data set names and network attributes.

    """ 
    url = '/api/nets'
    for k, v in kwargs.items():
        url += '?{0}={1}'.format(k, v)
    f = request.urlopen(base_url + url).read()
    return json.loads(f)


def read_netzschleuder_record(name: str, base_url: str='https://networks.skewed.de') -> dict:
    """
    Reads metadata of a single data record with given name from the netzschleuder repository

    Parameters
    ----------

    name: str

        Name of the data set for which to retrieve the metadata

    base_url: str='https://networks.skewed.de'

        Base URL of netzschleuder repository

    Examples
    --------

    Retrieve metadata of karate club network
    >>> import pathpy as pp
    >>> metdata = pp.io.graphtool.read_netzschleuder_record('karate')
    >>> print(metadata)
    { 
        'analyses': {'77': {'average_degree': 4.52... } }
    }

    Returns
    -------

    Dictionary containing key-value pairs of metadata
    """ 
    url = '/api/net/{0}'.format(name)
    return json.loads(request.urlopen(base_url + url).read())


def read_netzschleuder_network(name: str, net: Optional[str]=None, 
        ignore_temporal: bool=False, 
        base_url: str='https://networks.skewed.de') -> Optional[Union[Network, TemporalNetwork]]:
    """Reads a pathpy network record from the netzschleuder repository.

    Parameters
    ----------
    name: str

        Name of the network data sets to read from

    net: Optional[str]=None

        Identifier of the network within the data set to read. For data sets 
        containing a single network only, this can be set to None.

    ignore_temporal: bool=False

        If False, this function will return a static or temporal network depending 
        on whether edges contain a time attribute. If True, pathpy will not interpret
        time attributes and thus always return a static network.

    base_url: str=https://networks.skewed.de

        Base URL of netzschleuder repository

    Examples
    --------

    Read network '77' from karate club data set

    >>> import pathpy as pp
    >>> n = pp.io.graphtool.read_netzschleuder_network('karate', '77')
    >>> print(type(n))
    >>> pp.plot(n)
    pp.Network

    Read a temporal network from a data set containing a single network only
    (i.e. net can be omitted):

    >>> n = pp.io.graphtool.read_netzschleuder_network('reality_mining')
    >>> print(type(n))
    >>> pp.plot(n)
    pp.TemporalNetwork

    Read temporal network but ignore time attribute of edges:

    >>> n = pp.io.graphtool.read_netzschleuder_network('reality_mining', ignore_temporal=True)
    >>> print(type(n))
    >>> pp.plot(n)
    pp.Network


    Returns
    -------

    Depending on whether the network data set contains an edge attribute
    'time' (and whether ignore_temporal is set to True), this function 
    returns an instance of Network or TemporalNetwork

    """
    try:
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
    except ModuleNotFoundError:
        LOG.error('Package zstandard is needed to decode graphtool files. Please install module, e.g., using "pip install zstandard.')
