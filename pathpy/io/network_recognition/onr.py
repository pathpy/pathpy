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
from typing import TYPE_CHECKING, Optional, Union

from pathpy import config, logger

from pathpy.models.network import Network
from numpy import sqrt, pi


def check_intersect(line, circle):
    """
    """
    l = sqrt((line[0]-line[2])**2 + (line[1]-line[3])**2)
    return ((circle[0] - line[0]) * (line[3] - line[1]) - (circle[1]-line[1])* (line[2]-line[0])/l)<=circle[2]

def check_connected(line, v, w, tol=2):
    """
    """
    dist_1 = sqrt( (line[0]-v['coordinates'][0])**2 + (line[1]-v['coordinates'][1])**2 )
    dist_2 = sqrt( (line[2]-w['coordinates'][0])**2 + (line[3]-w['coordinates'][1])**2 )
    return dist_1 <= tol*v['size'] and dist_2 <= tol*w['size']


def from_image(file: str, node_radius: tuple=(10,100), min_node_dist: int=50, min_edge_length: int=100, max_edge_gap: int=200, intersect_tolerance_factor: int=7) -> Network:
    """
    """
    import cv2

    img = cv2.imread(file, cv2.IMREAD_ANYCOLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize = 3)
    
    # TODO: apply watershed technique
    lines = cv2.HoughLinesP(edges, rho=5, theta=pi/180, threshold=140, minLineLength=min_edge_length, maxLineGap=max_edge_gap)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=2, minDist=min_node_dist, param1=50, param2=45, minRadius=node_radius[0], maxRadius=node_radius[1])

    # create network
    n = Network(directed=False)

    # create nodes
    i = 0
    for c in circles[0]:    
        n.add_node(str(i), coordinates=[c[0], c[1]], size=c[2])
        i+=1

    # create edges
    for v in n.nodes:
        for w in n.nodes:
                connected = False
                # nodes are connected if any line intersects both nodes
                for l in lines:                
                    if check_connected(l[0], v, w, tol=intersect_tolerance_factor):
                        connected = True
                if connected and (v.uid,w.uid) not in n.edges:
                    n.add_edge(v, w)
    return n