#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test_state_file_export.py -- Test export of state files
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Thu 2021-05-06 16:59 ingos>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================

import pytest
from collections import Counter, OrderedDict
import pathpy as pp
import io


@pytest.fixture
def paths():
    # a simple toy example
    pc = pp.PathCollection()
    pc.add('a', 'b', count=1, uid='a-b')
    pc.add('b', 'c', 'd', count=1, uid='b-c-d')
    pc.add('c', 'd', 'a', 'c', count=1, uid='c-d-a-c')
    pc.add('b', 'c', 'b', 'a', 'c', count=1, uid='b-c-b-a-c')
    return pc


def test_state_file_export(paths):
    pp.io.infomap.to_state_file(paths, 'pathpy/tests/data/test.state', max_memory=1)
    with io.open('pathpy/tests/data/test.state', 'r') as f:
        lines1 = f.readlines()
    # cross check with ground truth for toy example
    with io.open('pathpy/tests/data/correct.state', 'r') as f:
        lines2 = f.readlines()
    assert sorted(lines1) == sorted(lines2)
        
    


