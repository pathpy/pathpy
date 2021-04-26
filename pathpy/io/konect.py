"""Functions to read files from the Koblenz Network Collection (konect.cc)."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : konect.py -- Read konect data files
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Sat 2020-08-22 17:58 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
import tarfile
import io
from urllib import request
from urllib.error import HTTPError

from typing import Union, Optional

import pandas as pd  # pylint: disable=import-error

from pathpy import logger
from pathpy.io.pandas import to_network, to_temporal_network
from pathpy.core.network import Network
from pathpy.models.temporal_network import TemporalNetwork

# create logger
LOG = logger(__name__)


def read_network(file: str, ignore_temporal: bool=False) -> Union[Network, TemporalNetwork]:
    """Reads a KONECT data file in TSV format and returns a pp.Network instance.

    The unified KONECT data format is a compressed .tar.bz2 file containing two
    files meta.* and out.*. The key-value attributes in the meta file
    (typically containing data descriptions and link to original data source)
    are stored as attributes in the returned instance of pp.Network.

    Depending on the data file, the generated network will be a single -or
    multi-edge network with directed or undirected edges, or a Temporal Network. The type of the
    network will be automatically determined based on the data file. Weight and
    Time attributes are stored as edge attributes.

    Parameters
    ----------

    file: str, Bytes

        Filename or byte stream from which data should be loaded

    ignore_temporal: bool=False
        
        If False (default), a temporal or static network will be returned depending on the data.
        If True, a static network will be returned even if the edges of the KONECT network contain a time attribute. 

    """

    # implicit semantics of columns in TSV files
    tsv_columns = ['v', 'w', 'weight', 'time']

    if isinstance(file, str):
        tar = tarfile.open(file, mode='r:bz2')
    elif isinstance(file, bytes):
        tar = tarfile.open(fileobj=io.BytesIO(file), mode='r:bz2')

    # network-level attributes
    attributes = {}

    directed = False
    multiedges = False
    network_data: pd.DataFrame = None

    for tarinfo in tar:
        if tarinfo.isfile():
            f = tarinfo.path.split('/')[-1]

            # read meta-data into attributes
            if f.startswith('meta.'):
                bytedata = tar.extractfile(tarinfo)
                if bytedata:
                    with io.TextIOWrapper(bytedata) as buffer:
                        for line in buffer.readlines():
                            s = line.split(': ', 1)
                            # ignore empty lines
                            if len(s) == 2:
                                attributes[s[0].strip()] = s[1].strip()
                else:
                    LOG.error('Could not extract tar file {0}'.format(f))

            # read network data
            elif f.startswith('out.'):
                bytedata = tar.extractfile(tarinfo)
                if bytedata:
                    with io.TextIOWrapper(bytedata) as buffer:
                        # check whether network is directed
                        directed = 'asym' in buffer.readline()

                        # read pandas data frame
                        network_data = pd.read_csv(
                            buffer, sep=r'\s+', header=None, comment='%')
                        network_data = network_data.dropna(axis=1, how='all')

                        # extract which columns are present
                        network_data.columns = [tsv_columns[i]
                                                for i in range(len(network_data.columns))]
                        duplicates = len(
                            network_data[network_data.duplicated(['v', 'w'], keep=False)])
                        if duplicates > 0:
                            LOG.info('Found {} duplicate edges'.format(duplicates))
                            multiedges = True
                        LOG.info('Detected columns: {0}'.format(str([c for c in network_data.columns])))
                else:
                    LOG.error('Could not extract file {0}'.format(f))
    if 'timeiso' in attributes:
        try:
            dt = pd.to_datetime(attributes['timeiso'])
            attributes['time'] = attributes['timeiso']            
        except ValueError:
            LOG.warning('KONECT data contains invalid timeiso: {}'.format(
                attributes['timeiso']))
    if 'time' in network_data.columns and not ignore_temporal:
        network_data.rename(columns= {'time': 'timestamp'}, inplace=True)
        return to_temporal_network(network_data, 
                directed=directed, multiedges=multiedges, **attributes)
    else:
        return to_network(network_data, 
            directed=directed, multiedges=multiedges, **attributes)


def read_konect_name(name, ignore_temporal: bool=False, base_url="http://konect.cc/files/download.tsv.") -> Optional[Union[Network, TemporalNetwork]]:
    """Retrieves a KONECT data set with a given name and returns a corresponding
    instance of pp.Network.

    The unified KONECT data format is a compressed .tar.bz2 file containing two
    files meta.* and out.*. The key-value attributes in the meta file
    (typically containing data descriptions and link to original data source)
    are stored as attributes in the returned instance of pp.Network.

    Depending on the data file, the generated network will be a single -or
    multi-edge network with directed or undirected edges. The type of the
    network will be automatically determined based on the data file. Weight and
    Time attributes are stored as edge attributes.

    Parameters
    ----------

    name: str

        Name of the data set to retrieve from the KONECT database,
        e.g. 'moreno_bison'

    base_url: str

        Base url of the KONECT service that will be used to retrieve data
        set. Default is "http://konect.cc/files/download.tsv.". This
        method assumes that the KONECT data file with name X can be retrieved
        via HTTP under the URL
        "http://konect.cc/files/download.tsv.X.tar.bz2"

    ignore_temporal: bool=False
        
        If False (default), a temporal or static network will be returned depending on the data.
        If True, a static network will be returned even if the edges of the KONECT network contain a time attribute. 

    """
    try:
        f = request.urlopen(base_url + name + ".tar.bz2").read()
        return read_network(f, ignore_temporal)
    except HTTPError:
        LOG.error('HTTP 404 Error, could not open URL.')
        return None


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
