#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : utils.py -- Plotting utils
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Fri 2019-12-20 10:31 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
import os
import numpy as np


def _check_filename(self, filename, fileformat):

    # set default environment
    _filename = self.filename
    _fileformat = self.fileformat

    # if only filename is given check file ending
    if filename is not None and fileformat is None:
        _filename = filename
        extension = os.path.splitext(filename)[1].replace('.', '')
        if extension not in self.fileformats:
            _filename = '{}.{}'.format(filename, _fileformat)
        else:
            _fileformat = extension
    # if only fileformat is given
    elif filename is None and fileformat is not None:
        if fileformat in self.fileformats:
            _fileformat = fileformat
        _filename = '{}.{}'.format(_filename, _fileformat)

    # if filename and fileformat is given
    elif filename is not None and fileformat is not None:

        extension = os.path.splitext(filename)[1].replace('.', '')
        if extension not in self.fileformats:
            extension = None
        if fileformat not in self.fileformats:
            fileformat = None

        if extension is not None and fileformat is None:
            _filename = filename
            _fileformat = extension
        elif extension is None and fileformat is not None:
            _filename = '{}.{}'.format(filename, fileformat)
            _fileformat = fileformat
        elif extension is not None and fileformat is not None:
            if extension == fileformat:
                _filename = filename
                _fileformat = fileformat
            else:
                _filename = '{}.{}'.format(
                    os.path.splitext(filename)[0], fileformat)
                _fileformat = fileformat
        else:
            _filename = '{}.{}'.format(_filename, _fileformat)
    return _filename, _fileformat


def _clean_dict(d, keep=None):
    keys_to_delete = set()
    for key, value in d.items():
        if value is None or (isinstance(value, float) and np.isnan(value)):
            keys_to_delete.add(key)
        if keep:
            if key not in keep:
                keys_to_delete.add(key)

    for key in keys_to_delete:
        d.pop(key)
    return d


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
