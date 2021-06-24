#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : utils.py -- Helpers for the plotting functions
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Thu 2021-06-24 15:37 juergen>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================


def rgb_to_hex(rgb):
    """Convert rgb color tuple to hex string."""
    return '#%02x%02x%02x' % rgb


def hex_to_rgb(value):
    """Convert hex string to rgb color tuple."""
    value = value.lstrip('#')
    _l = len(value)
    return tuple(int(value[i:i+_l//3], 16) for i in range(0, _l, _l//3))


class Colormap:
    """Very simple colormap class"""

    def __call__(self, values, alpha=None, bytes=False):
        vmin, vmax = min(values), max(values)
        if vmin == vmax:
            vmin -= 1
            vmax += 1
        return [self.color_tuple(v)
                for v in ((x - vmin) / (vmax - vmin)*100 for x in values)]

    @staticmethod
    def color_tuple(n):
        """ color ramp from green to red """
        return (int((255 * n) * 0.01), int((255 * (100 - n)) * 0.01), 0, 255)

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
