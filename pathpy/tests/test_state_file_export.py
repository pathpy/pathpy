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
    return OrderedDict({
        ('a', 'b'): 1,
        ('b', 'c', 'd'): 1,
        ('c', 'd', 'a', 'c'): 1,
        ('b', 'c', 'b', 'a', 'c'): 1
        })


def test_state_file_export(paths):
    print(paths)
    pp.io.infomap.to_state_file(paths, 'test.state', max_memory=1)
    with io.open('test.state', 'r') as f:
        lines1 = f.readlines()
    # cross check with ground truth for toy example
    with io.open('correct.state', 'r') as f:
        lines2 = f.readlines()
    assert sorted(lines1) == sorted(lines2)
        
    


