"""Multi-Order Model"""
# !/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : multi_order_models.py -- Multi order models for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Sun 2020-09-06 12:02 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================
from __future__ import annotations
from typing import Optional, Any
import datetime
from itertools import islice
import numpy as np
from scipy.stats import chi2
from collections import defaultdict

# from singledispatchmethod import singledispatchmethod

from pathpy import logger
from pathpy.models.classes import BaseModel
from pathpy.models.higher_order_network import HigherOrderNetwork
from pathpy.models.null_model import NullModel
from pathpy.core.path import PathCollection

# create logger
LOG = logger(__name__)


class MultiOrderModel(BaseModel):
    """A mulit-order model for higher order networks."""

    def __init__(self, uid: Optional[str] = None, max_order: int = 1,
                 **kwargs: Any) -> None:
        """Initialize multi-oder model."""

        # initialize the base class
        super().__init__(uid=uid, **kwargs)

        # initialize max order
        self._max_order = max_order

        # initialize layers
        self.layers: defaultdict = defaultdict(dict)
        self.data: PathCollection

    def __str__(self) -> str:
        """Print the summary of the MultiOrderModel"""
        return self.summary()

    @property
    def max_order(self):
        """Return the max order."""
        return self._max_order

    def _current_max_order(self):
        """The current maximum order of the multi-order model"""
        orders = list(self.layers.keys())
        if not orders:
            return -1
        else:
            return max(orders)

    def degrees_of_freedom(self, order: int = 1, mode: str = 'path') -> int:

        # TODO add checks for the max order
        max_order = order

        # initialize degrees of freedom
        dof = 0

        for order in range(0, max_order + 1):

            # check if the null model for the given order is
            # already calculated if not calculate new null model
            if self.layers[order].get('null', None) is None:
                self.layers[order]['null'] = NullModel.from_paths(
                    self.data, order=order)

            dof += self.layers[order]['null'].degrees_of_freedom(mode=mode)

        return dof

    def fit(self, data: PathCollection, max_order: Optional[int] = None,
            null_models: bool = True) -> None:
        """Fit data to a MultiOrderModel"""

        # Check max order
        if max_order is not None:
            self._max_order = max_order

        # store data
        self.data = data

        for order in list(range(self._current_max_order()+1, self.max_order+1)):

            LOG.debug('Generating %s-th order layer ...', order)

            # generate higher order network
            _hon = HigherOrderNetwork.from_paths(data, order=order,
                                                 subpaths=True)

            # calculate transition matrices for the higher-order networks
            _T = _hon.transition_matrix(weight='frequency', transposed=True)

            _null = None
            if null_models:
                # generate null model
                _null = NullModel.from_paths(data, order=order)

            self.layers[order]['hon'] = _hon
            self.layers[order]['T'] = _T
            self.layers[order]['null'] = _null

    def predict(self, data: Optional[PathCollection] = None, threshold=0.01):
        """Predict the optimal order for a multi-order model."""

        LOG.debug('start estimate optimal order')
        start = datetime.datetime.now()

        if data is None:
            data = self.data

        # initialize variables
        max_accepted_order = 1
        max_considerd_order = self._current_max_order()

        for order in range(2, max_considerd_order+1):
            LOG.debug('---')
            LOG.debug('> estimating order %s', order)

            accept, p_value = self.likelihood_ratio_test(data, null=order-1,
                                                         order=order,
                                                         threshold=threshold)

            if accept:
                max_accepted_order = order

        end = datetime.datetime.now()
        LOG.debug('end estimate optiomal order:' +
                  ' {} seconds'.format((end-start).total_seconds()))
        return max_accepted_order

    def likelihood_ratio_test(self, data, null=0, order=1, threshold=0.01):

        LOG.debug('start likelihood ratio test')
        start = datetime.datetime.now()

        # calculate likelihoods
        likelihood_0 = self.likelihood(data, order=null, log=True)
        likelihood_1 = self.likelihood(data, order=order, log=True)

        # calculate test statistics x = -2 * (log L0 - log L1)
        x = -2*(likelihood_0 - likelihood_1)

        # calculate degrees of freedom
        dof_0 = self.degrees_of_freedom(order=null)
        dof_1 = self.degrees_of_freedom(order=order)

        # calculate the additional degrees of freedom in the alternative model
        delta_dof = dof_1 - dof_0

        # calculate p-value
        p_value = 1 - chi2.cdf(x, delta_dof)

        # reject the null hypothesis if p-value is below the threshold
        accept = p_value < threshold

        # some information
        LOG.debug('Likelihood ratio test for order = %s', order)
        LOG.debug('test statistics x = %s', x)
        LOG.debug('additional degrees of freedom = %s', delta_dof)
        LOG.debug('p-value = %s', p_value)
        LOG.debug('reject the null hypothesis = %s', accept)

        end = datetime.datetime.now()
        LOG.debug('end likelihood ratio test:' +
                  ' {} seconds'.format((end-start).total_seconds()))

        return accept, p_value

    def likelihood(self, data, order=1, log=True):
        # add log-likelihoods of multiple model layers,
        # assuming that paths are independent

        # TODO add checks for the max order
        max_order = order

        # initialize likelihood
        likelihood = np.float64(0)

        for order in range(0, max_order + 1):
            likelihood += self.layer_likelihood(
                data=data, order=order,
                longer_paths=(order == max_order), log=True)

        if not log:
            likelihood = np.exp(likelihood)

        return likelihood

    def layer_likelihood(self, data, order=1,
                         longer_paths=True, log=True,
                         min_length=None):

        path_lengths = [len(p) for p in data]

        if min_length is None:
            min_length = order
        else:
            min_length = max(order, min_length)
            LOG.debug('Add warning')

        if longer_paths:
            max_length = max(path_lengths)
        else:
            max_length = order

        # initialize likelihood
        likelihood = 0

        for path in data.values():
            if min_length <= len(path) <= max_length:
                likelihood += self.path_likelihood(path, order=order, log=True)

        if not log:
            likelihood = np.exp(likelihood)

        return likelihood

    def path_likelihood(self, path, order=1, log=True):

        # initialize likelihood
        likelihood = 0

        # get path frequency
        frequency = path.attributes.get('frequency', 1)

        # 1.) transform the path into a sequence of (two or more)
        # l-th-order edges
        edges = self._path_to_hon(path, order=order)

        # 2.) nodes[0] is the prefix of the k-th order transitions, which
        # we can transform into multiple transitions in lower order
        # models. Example: for a path a-b-c-d of length three, the node
        # sequence at order l=3 is ['a-b-c', 'b-c-d'] and thus the prefix
        # is 'a-b-c'.
        # prefix = nodes[0]

        # 3.) We extract the transitions for the prefix based on models of
        # orders k_<l. In our example, we have the transitions ... (a-b,
        # b-c) for k_=2 (a, b) for k_=1, and (start, a) for k_=0
        transitions = {}

        # iterate through all orders and add prefix
        for _order in range(order):
            transitions[_order] = self._path_to_hon(path, _order)[0]

        # 4.) Using Bayes theorem, we calculate the likelihood of a path
        # a-b-c-d-e of length four for l=4 as a single transition in a
        # fourth-order model, and four additional transitions in the k_=0,
        # 1, 2 and 3-order models, i.e. we have ... P(a-b-c-d-e) =
        # P(e|a-b-c-d) * [ P(d|a-b-c) * P(c|a-b) * P(b|a) * P(a) ] If we
        # were to model the same path based on model hierarchy with a
        # maximum order of l=2, we instead have three transitions in the
        # second-order model and two additional transitions in the k_=0 and
        # k_=1 order models for the prefix 'a-b' ... P(a-b-c-d-e) =
        # P(e|c-d) * P( d|b-c) * P(c|a-b) * [ P(b|a) * P(a) ]

        # get a list of nodes for the matrix indices
        n = self.layers[order]['hon'].nodes.index

        if order == 0:
            for _n in edges:
                likelihood += np.log(self.layers[order]['hon']
                                     .nodes[(_n,)]['frequency']) * frequency
        else:
            for _v, _w in edges:
                # calculate the log-likelihood
                likelihood += np.log(self.layers[order]['T'][
                    n[self.layers[order]['hon'].nodes[_w].uid],
                    n[self.layers[order]['hon'].nodes[_v].uid]])*frequency

        for _order, _e in transitions.items():
            if _order == 0:
                likelihood += np.log(self.layers[_order]['hon']
                                     .nodes[(_e,)]['frequency']) * frequency
            else:
                # get a list of nodes for the matrix indices
                n = self.layers[_order]['hon'].nodes.index
                _v = _e[0]
                _w = _e[1]
                # calculate the log-likelihood
                likelihood += np.log(self.layers[_order]['T'][
                    n[self.layers[_order]['hon'].nodes[_w].uid],
                    n[self.layers[_order]['hon'].nodes[_v].uid]])*frequency

        if not log:
            likelihood = np.exp(likelihood)

        return likelihood

    def _path_to_hon(self, path, order):
        """Helper function to convert path to hon node tuples."""

        nodes: list = []

        if order == 0:
            return list(path.nodes)

        elif order == 1:
            nodes.extend([tuple([n]) for n in path.nodes])

        elif 1 < order <= len(path):

            for subpath in self.window(path.edges, size=order-1):
                nodes.append(subpath)

        return list(zip(nodes[:-1], nodes[1:]))

    @staticmethod
    def window(iterable, size=2):
        """Sliding window for path length"""
        ite = iter(iterable)
        result = tuple(islice(ite, size))
        if len(result) == size:
            yield result
        for elem in ite:
            result = result[1:] + (elem,)
            yield result

    def summary(self):
        """Returns a summary of the multi-order model."""

        # TODO: Find better solution for printing
        # TODO: Move to util
        line_length = 54
        row = {}
        row['==='] = '='*line_length
        row['s| s| s'] = '{:^6s} | {:^21s} | {:^20s}'
        row['s|ss|ss'] = '{:^6s} | {:^10s} {:^10s} | {:^10s} {:^10s}'
        row['d|dd|dd'] = '{:>6d} | {:>10d} {:>10d} | {:>10d} {:>10d}'

        # initialize summary text
        summary: list = [
            row['==='],
            'Multi-order model',
            '- General '.ljust(line_length, '-')
        ]

        # add general information
        summary.append(row['s| s| s'].format('layer', 'network', 'DoF'))
        summary.append(row['s|ss|ss'].format(
            'order', 'nodes', 'edges', 'paths', 'ngrams'))

        # add row for each order
        data = [[], [], [], []]

        for order, models in self.layers.items():
            hon = models['hon']
            null = models['null']
            data[0].append(hon.number_of_nodes())
            data[1].append(hon.number_of_edges())
            # data[2].append(1)
            if null is not None:
                # TODO : Use the better method to estimate the DoF
                data[2].append(null.degrees_of_freedom(mode='path'))
                data[3].append(null.degrees_of_freedom(mode='ngram'))
            else:
                data[2].append(-1)
                data[3].append(-1)

            summary.append(row['d|dd|dd'].format(
                order, *[v[-1] for v in data]))

        # add double line
        summary.append('='*line_length,)

        return '\n'.join(summary)

    @classmethod
    def from_paths(cls, paths: PathCollection, **kwargs: Any):
        """Create multi-oder network from paths."""

        max_order: int = kwargs.get('max_order', 1)

        mom = cls(max_order=max_order)
        mom.fit(paths)

        return mom


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
