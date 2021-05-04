"""Functions to recognize networks in image data."""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : onr.py -- Read networks from image data
# Author    : Ingo Scholtes <scholtes@uni-wuppertal.de>
# Time-stamp: <Sat 2021-04-23 01:11 ingos>
#
# Copyright (c) 2016-2021 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union, Tuple

from pathpy import config, logger

from pathpy.models.network import Network
from pathpy.core.api import Node, Edge
import numpy as np


# def _check_intersect(line, circle):
#     """
#     """
#     l = np.sqrt((line[0]-line[2])**2 + (line[1]-line[3])**2)
#     return ((circle[0] - line[0]) * (line[3] - line[1]) - (circle[1]-line[1])* (line[2]-line[0])/l)<=circle[2]

def _check_connected(line, v, w, tol=2):
    """
    """
    dist_1 = np.sqrt( (line[0][0]-v['x'])**2 + (line[0][1]-v['y'])**2 )
    dist_2 = np.sqrt( (line[1][0]-w['x'])**2 + (line[1][1]-w['y'])**2 )
    return dist_1 <= tol*v['r'] and dist_2 <= tol*w['r']
 


def _detect_nodes(edges, node_radius: Tuple[int, int], num_nodes: int, n):
    """
    """
    from skimage.transform import hough_circle, hough_circle_peaks
    from skimage import color
    from skimage.draw import circle_perimeter

    nodes = []
    
    hough_radii = np.arange(node_radius[0], node_radius[1], 1)
    hough_res = hough_circle(edges, hough_radii)
    accums, cx, cy, radii = hough_circle_peaks(hough_res, hough_radii,
                                            total_num_peaks=num_nodes)

    # fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 10))
    # image = color.gray2rgb(img.copy())
    i = 0
    for center_y, center_x, radius in zip(cy, cx, radii):
        # circy, circx = circle_perimeter(center_y, center_x, radius,
        #                                 shape=image.shape)
        # image[circy, circx] = (255, 20, 20)
        n.add_node(str(i), x=center_x, y=center_y, r=radius, coordinates=(center_x, -center_y))
        i += 1


def _detect_edges(edges, min_edge_length, max_edge_gap, threshold, intersect_tolerance_factor, network: Network):
    """
    """
    from skimage.transform import probabilistic_hough_line
    tested_angles = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)
    lines = probabilistic_hough_line(edges, threshold=threshold, line_length=min_edge_length, line_gap=max_edge_gap)
    
    # fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 10))

    # ax.imshow(img)
    # ax.set_ylim((edges.shape[0], 0))
    # ax.set_axis_off()
    # ax.set_title('Detected lines')
    # print(len(lines))
    # for line in lines:
    #     p0, p1 = line
    #     ax.plot((p0[0], p1[0]), (p0[1], p1[1]))

    # plt.tight_layout()
    # plt.show()

    # create edges
    for v in network.nodes:
        for w in network.nodes:
                connected = False
                # nodes are connected if any line intersects both nodes
                for l in lines:                
                    if _check_connected(l, v, w, tol=intersect_tolerance_factor):
                        connected = True
                if connected and (v.uid,w.uid) not in network.edges:
                    network.add_edge(v, w)


def _preprocess_image(img, sigma=0.25):
    """
    """
    from skimage.color import rgb2gray
    from skimage import feature

    grayscale = rgb2gray(img)
    edges = feature.canny(grayscale, sigma=sigma)

    # plt.imshow(edges, cmap='gray')

    return edges


def from_image(img_path, sigma=0.25, node_radius: tuple=(10,15), num_nodes: int=50, threshold=20, min_edge_length: int=20, max_edge_gap: int=5, intersect_tolerance_factor: int=1.1) -> Network:
    """
    """
    from skimage import io

    img = io.imread(img_path)

    n = Network(directed=False, multiedges=False)

    edges = _preprocess_image(img, sigma)

    _detect_nodes(edges, node_radius, num_nodes, n)
    _detect_edges(edges, min_edge_length, max_edge_gap, threshold, intersect_tolerance_factor, n)

    return n
    