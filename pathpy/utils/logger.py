#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : logger.py -- Module to log output information
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2019-09-09 10:34 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import logging

logging_level = 'INFO'

if True:
    # generate base config for logging
    logging.basicConfig()

    # create stream handler
    console = logging.StreamHandler()

    # set level according to the config file
    console.setLevel(logging._nameToLevel[logging_level])

    # set a format which is simpler for console use
    formatter = logging.Formatter('[%(asctime)s: %(levelname)-5s] %(message)s',
                                  datefmt='%m-%d %H:%M:%S')

    # tell the handler to use this format
    console.setFormatter(formatter)

    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


def logger(name, level=None):
    """A function to generate logger for the modules."""

    # initialize new logger
    logger = logging.getLogger(name)

    # logging messages are not passed to the handlers of ancestor loggers
    logger.propagate = False

    # get formatter options
    logger.addHandler(console)

    # if no level is defined the config level will be used
    if level is None:
        logger.setLevel(logging._nameToLevel[logging_level])
    else:
        logger.setLevel(logging._nameToLevel[level])
    return logger


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
