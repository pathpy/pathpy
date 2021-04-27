"""Functions to read files from the Koblenz Network Collection (konect.cc)."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : konect.py -- Read konect data files
# Author    : Ingo Scholtes <scholtes@uni-wuppertal>
# Time-stamp: <Tue 2021-04-27 11:12 ingo>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from pathpy.utils.errors import NetworkError
import tarfile
import io
from urllib import request
from urllib.error import HTTPError

from typing import Union, Optional

import pandas as pd  # pylint: disable=import-error

from pathpy import logger
from pathpy.io.pandas import to_network, to_temporal_network
from pathpy.models.api import Network
from pathpy.models.api import TemporalNetwork
from pathpy import FileFormatError, NetworkError

# create logger
LOG = logger(__name__)


def read_tsv_network(file: str, ignore_temporal: bool=False) -> Union[Network, TemporalNetwork]:
    """Reads a KONECT data file in TSV format and returns a pp.Network instance.

    The unified KONECT data format is a compressed .tar.bz2 file containing two
    files meta.* and out.*. The key-value attributes in the meta file
    (typically containing data descriptions and link to original data source)
    are stored as attributes in the returned instance of pp.Network.

    Depending on the data file, the generated network will be a single -or
    multi-edge network with directed or undirected edges, or a Temporal Network. The type of the
    network will be automatically determined based on the data file. Weight and
    Time attributes are stored as edge attributes.

    For more information on the TSV file format, see Section 9 in referenced handbook.

    .. [1] J Kunegis, "Handbook of Network Analysis - The Konect Project", https://github.com/kunegis/konect-handbook/blob/master/konect-handbook.pdf, 2019

    Parameters
    ----------
    file: str, Bytes
        Filename or byte stream from which data should be loaded

    ignore_temporal: bool=False
        If False (default), a temporal or static network will be returned depending on the data.
        If True, a static network will be returned even if the edges of the KONECT network contain a time attribute.

    Returns
    -------
    Network or TemporalNetwork
        a static or temporal network object

    Examples
    --------

    Read a static network

    >>> n = pp.io.konect.read_konect_name('ucidata-zachary.tsv')
    >>> print(n)
    Uid:			0x7f9a6878bb80
    Type:			Network
    Directed:		False
    Multi-Edges:		False
    Number of nodes:	34
    Number of edges:	78

    Read a temporal network

    >>> tn = pp.io.konect.read_konect_name('edit-htwikisource.tsv')
    >>> print(tn)
    Uid:			0x7f9a38914730
    Type:			TemporalNetwork
    Directed:		False
    Multi-Edges:		True
    Number of unique nodes:	115
    Number of unique edges:	157
    Number of temp nodes:	115
    Number of temp edges:	315
    Observation periode:	1151852649 - 1443816055.0

    Read a temporal network as static network

    >>> n = pp.io.konect.read_konect_name('edit-htwikisource.tsv', ignore_temporal=True)
    >>> print(n)
    Uid:			0x7f9a687cbb80
    Type:			Network
    Directed:		False
    Multi-Edges:		True
    Number of nodes:	115
    Number of edges:	315
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
                    msg = 'Could not extract tar file {0}'.format(f)
                    LOG.error(msg)
                    raise FileFormatError(msg)

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
                    msg = 'Could not extract tar file {0}'.format(f)
                    LOG.error(msg)
                    raise FileFormatError(msg)
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
    """Retrieves a data set with a given name from the KONECT repository and returns a corresponding
    instance of pp.Network.

    The unified KONECT data format is a compressed .tar.bz2 file containing two
    files meta.* and out.*. The key-value attributes in the meta file
    (typically containing data descriptions and link to original data source)
    are stored as attributes in the returned instance of pp.Network.

    Depending on the data file, the generated network will be a single -or
    multi-edge network with directed or undirected edges. The type of the
    network will be automatically determined based on the data file. Weight and
    Time attributes are stored as edge attributes.

    .. [1] J Kunegis, "Konect: the koblenz network collection" Proceedings of the 22nd international conference on world wide web. 2013.

    See also
    --------

    read_tsv_network: Read (temporal) network from a TSV file

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

    Returns
    -------

    Instance of Network or TemporalNetwork

    Examples
    --------

    Read a static network from the konect repository

    >>> n = pp.io.konect.read_konect_name('ucidata-zachary')
    >>> print(n)
    Uid:			0x7f9a6878bb80
    Type:			Network
    Directed:		False
    Multi-Edges:		False
    Number of nodes:	34
    Number of edges:	78

    Read a temporal network from the konect repository

    >>> tn = pp.io.konect.read_konect_name('edit-htwikisource')
    >>> print(tn)
    Uid:			0x7f9a38914730
    Type:			TemporalNetwork
    Directed:		False
    Multi-Edges:		True
    Number of unique nodes:	115
    Number of unique edges:	157
    Number of temp nodes:	115
    Number of temp edges:	315
    Observation periode:	1151852649 - 1443816055.0

    Read a temporal network as static network

    >>> n = pp.io.konect.read_konect_name('edit-htwikisource', ignore_temporal=True)
    >>> print(n)
    Uid:			0x7f9a687cbb80
    Type:			Network
    Directed:		False
    Multi-Edges:		True
    Number of nodes:	115
    Number of edges:	315


    """
    try:
        f = request.urlopen(base_url + name + ".tar.bz2").read()
        return read_tsv_network(f, ignore_temporal)
    except HTTPError:
        raise NetworkError('Could not connect to KONECT server at {0}'.format(base_url))


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
