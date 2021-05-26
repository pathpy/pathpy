#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : errors.py -- Errors raises by pathpy functions
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Tue 2021-04-27 13:21 ingos>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================

class FileFormatError(Exception):
    pass

class NetworkError(Exception):
    pass

class MissingModuleError(Exception):
    pass

class ParameterError(Exception):
    pass