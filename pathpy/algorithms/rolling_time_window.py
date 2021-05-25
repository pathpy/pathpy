"""Methhods to generate time slice graphs from temporal networks"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : rolling_time_window.py
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Mon 2021-04-27 01:12 ingo>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================
from pathpy.models.temporal_network import TemporalNetwork
from pathpy.models.network import Network

from typing import Union, Tuple, List, Optional

class RollingTimeWindow:
    """
    An iterable rolling time window that can be used to perform time slice
    analyses of temporal networks.
    """

    def __init__(self, temporal_net: TemporalNetwork, window_size: int, step_size: int=1, return_window: bool=False):
        """
        Initialises a RollingTimeWindow instance that can be used to
        iterate through a sequence of time-slice networks for a given
        temporal network

        Parameters:
        -----------
        temporal_net:   TemporalNetwork
            TemporalNetwork instance that will be used to generate the
            sequence of time-slice networks.
        window_size:    int
            The width of the rolling time window used to create
            time-slice networks.
        step_size:      int
            The step size in time units by which the starting time of the rolling
            window will be incremented on each iteration. Default is 1.
        directed:       bool
            Whether or not the generated time-slice networks should be directed.
            Default is true.
        return_window: bool
            Whether or not the iterator shall return the current time window
            as a second return value. Default is False.

        Returns
        -------
        RollingTimeWindow
            An iterable sequence of tuples Network, [window_start, window_end]

        Examples
        --------
            >>> t = pathpy.TemporalNetwork.read_file(DATA)
            >>>
            >>> for n in pathpy.RollingTimeWindow(t, window_size=100):
            >>>     print(n)
            >>>
            >>> for n, w in pathpy.RollingTimeWindow(t, window_size=100, step_size=10, return_window=True):
            >>>     print('Time window starting at {0} and ending at {1}'.format(w[0], w[1]))
            >>>     print(network)
        """
        self.temporal_network = temporal_net
        self.window_size = window_size
        self.step_size = step_size
        self.current_time = temporal_net.start()
        self.max_time = temporal_net.end()
        self.directed = temporal_net.directed
        self.return_window = return_window

    def __iter__(self):
        return self

    def __next__(self) -> Union[Network, Tuple[Network, List]]:
        if self.current_time+self.window_size <= self.max_time:
            time_window = [self.current_time, self.current_time+self.window_size]
            n = Network.from_temporal_network(self.temporal_network, min_time=self.current_time,
                                              max_time=self.current_time+self.window_size,
                                              directed=self.directed)
            self.current_time += self.step_size
            if self.return_window:
                return n, time_window
            else:
                return n
        else:
            raise StopIteration()
