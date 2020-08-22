"""Functions to read konect files."""
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
import urllib

import pandas as pd  # pylint: disable=import-error

from pathpy import logger
from pathpy.io.io import to_network

# create logger
LOG = logger(__name__)


def read_network(file):
    """Reads a KONECT data file and returns a pp.Network instance.

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

    file: str, Bytes

        Filename or byte stream from which data should be loaded

    """

    tsv_columns = ['v', 'w', 'weight', 'time']

    if isinstance(file, str):
        tar = tarfile.open(file, mode='r:bz2')
    elif isinstance(file, bytes):
        tar = tarfile.open(fileobj=io.BytesIO(file), mode='r:bz2')
    attributes = {}
    directed = False
    multiedges = False
    network_data = None
    for tarinfo in tar:
        if tarinfo.isfile():
            f = tarinfo.path.split('/')[-1]

            # read meta-data into attributes
            if f.startswith('meta.'):
                with io.TextIOWrapper(tar.extractfile(tarinfo)) as buffer:
                    for line in buffer.readlines():
                        s = line.split(': ', 1)
                        # ignore empty lines
                        if len(s) == 2:
                            attributes[s[0].strip()] = s[1].strip()

            # read network data
            elif f.startswith('out.'):
                with io.TextIOWrapper(tar.extractfile(tarinfo)) as buffer:
                    directed = 'asym' in buffer.readline()
                    network_data = pd.read_csv(
                        buffer, sep=r'\s+', header=None, comment='%')
                    network_data = network_data.dropna(axis=1, how='all')

                    # print(network_data.head())
                    network_data.columns = [tsv_columns[i]
                                            for i in range(len(network_data.columns))]
                    duplicates = len(
                        network_data[network_data.duplicated(['v', 'w'], keep=False)])
                    if duplicates > 0:
                        LOG.info('Found {} duplicate edges'.format(duplicates))
                        multiedges = True
                    LOG.info('Detected columns: ', [
                             c for c in network_data.columns])
    if 'timeiso' in attributes:
        try:
            dt = pd.to_datetime(attributes['timeiso'])
            attributes['time'] = attributes['timeiso']
        except ValueError:
            LOG.warning('KONECT data contains invalid timeiso: {}'.format(
                attributes['timeiso']))
    net = to_network(network_data, directed=directed,
                     multiedges=multiedges, **attributes)
    return net


def read_konect_name(name, base_url="http://konect.uni-koblenz.de/downloads/tsv/"):
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
        set. Default is "http://konect.uni-koblenz.de/downloads/tsv/". This
        method assumes that the KONECT data file with name X can be retrieved
        via HTTP under the URL
        "http://konect.uni-koblenz.de/downloads/tsv/X.tar.bz2"

    """
    f = urllib.request.urlopen(base_url + name + ".tar.bz2").read()
    return read_network(f)


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
