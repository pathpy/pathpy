#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : setup.py -- Setup script for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Tue 2020-07-14 08:03 juergen>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
"""
Setup script for pathpy.

You can install networkx with

python setup.py install

The pathpy build options can be modified with a setup.cfg file.
See setup.cfg.template for more information.
"""
import sys
import os
from setuptools import setup, find_packages

about = {}
base_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(base_dir, 'pathpy', '__about__.py'), 'rb') as f:
    exec(f.read(), about)

#version = about['__version__']
from ._version import __version__

# Minimum required python version
min_version = (3, 7)

# Check the python version. Pathpy requires Python 3.7+.
if sys.version_info[:2] < min_version:
    error = """
    Pathpy {} requires Python {} or later ({} detected).

    """.format(version,
               '.'.join(map(str, min_version)),
               '.'.join(map(str, sys.version_info[:2])))
    sys.exit(error)


# Initialize setup parameters
DISTNAME = 'pathpy3'

#VERSION = version

PYTHON_REQUIRES = '>={}'.format('.'.join(map(str, min_version)))

DESCRIPTION = "pathpy: path data analysis"

LONG_DESCRIPTION = """\
An OpenSource python package for the analysis of time series data on networks
using higher-order and multi-order graphical models.
"""

MAINTAINER = 'Ingo Scholtes, Jürgen Hackl'

MAINTAINER_EMAIL = 'info@pathpy.net'

URL = 'https://www.pathpy.net'

LICENSE = 'AGPL-3.0+'

DOWNLOAD_URL = 'https://github.com/pathpy/pathpy'

PROJECT_URLS = {
    "Issue Tracker": "https://github.com/pathpy/pathpy/issues",
    "Documentation": "https://pathpy.github.io/",
    "Source Code": "https://github.com/pathpy/pathpy",
}

INSTALL_REQUIRES = [
    'numpy>=1.17.0',
    'scipy>=1.3.1',
    'tqdm>=4.36.1',  # TODO: Get rid of this dependency!
    'pandas>=0.25.2',
    'singledispatchmethod>=1.0',  # TODO: this is not needed for python 3.8 remove late
]

PACKAGES = find_packages()

PLATFORMS = ['Linux', 'Mac OSX', 'Windows', 'Unix']

CLASSIFIERS = [
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Science/Research',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    'Topic :: Scientific/Engineering :: Visualization',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Scientific/Engineering :: Mathematics',
    'Topic :: Scientific/Engineering :: Physics',
    'Operating System :: OS Independent',
]


setup(
    name=DISTNAME,
    author=MAINTAINER,
    author_email=MAINTAINER_EMAIL,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    license=LICENSE,
    url=URL,
    project_urls=PROJECT_URLS,
    #version=VERSION,
    download_url=DOWNLOAD_URL,
    install_requires=INSTALL_REQUIRES,
    packages=PACKAGES,
    classifiers=CLASSIFIERS,
    platforms=PLATFORMS,
    zip_safe=False,
    include_package_data=True,
    python_requires=PYTHON_REQUIRES,
    setup_requires=['pytest-runner', 'flake8', 'incremental'],
    tests_require=['pytest'],
    use_incremental=True,
    install_requires=['incremental']
)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
