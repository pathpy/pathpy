#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : multi_order_models.py -- Multi order models for pathpy
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Wed 2019-11-20 16:09 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import datetime
import numpy as np
from scipy.stats import chi2
from .. import logger, config
from ..core import HigherOrderNetwork
from ..utils import window
from . null_model import NullModel

# create logger
Log = logger(__name__)


class MultiOrderModel:
    """A mulit-order model for higher order networks."""

    def __init__(self, network, max_order=1):
        """Initialize multi-oder model."""
        self.network = network
        self.null = NullModel(self.network)
        self.max_order = max_order

        # initialize variables

        self.layers = {}
        self.null_models = {}
        self.transition_matrices = {}

    def _current_max_order(self):
        """The current maximum order of the multi-order model"""
        orders = list(self.layers.keys())
        if not orders:
            return -1
        else:
            return max(orders)

    def add_layer(self, order):
        """Add layer to the multi-order model."""

        Log.debug('Generating {}-th order layer ...'.format(order))
        # generate higher order network
        _hon = HigherOrderNetwork(self.network, order=order)

        # assign higher-order network to the model
        self.layers[order] = _hon

        # calculate transition matrices for the higher-order networks
        self.transition_matrices[order] = _hon.transition_matrix(
            transposed=True)

    def add_layers(self, max_order):
        """Add higher-order layers up to the given maximum order."""
        orders_to_add = list(range(self._current_max_order()+1, max_order+1))

        for order in sorted(orders_to_add):
            self.add_layer(order)

    def generate(self, max_order=1):
        """Generate a multi-order model."""

        self.add_layers(max_order)

    def summary(self):
        """Returns a summary of the multi-order model."""

        # TODO: Find better solution for printing
        # TODO: Move to util
        line_length = 54
        row = {}
        row['==='] = '='*line_length
        row['s| s | s'] = '{:^6s} | {:^29s} | {:^13s}'
        row['s|sss|ss'] = '{:^6s} | {:^9s} {:^9s} {:^9s} | {:^6s} {:^6s}'
        row['d|ddd|dd'] = '{:>6d} | {:>9d} {:>9d} {:>9d} | {:>6d} {:>6d}'

        # initialize summary text
        summary: list = [
            row['==='],
            'Multi-order model',
            '- General '.ljust(line_length, '-')
        ]

        # add general information
        summary.append(row['s| s | s'].format('layer', 'network', 'DoF'))
        summary.append(row['s|sss|ss'].format(
            'order', 'nodes', 'edges', 'paths', 'paths', 'ngrams'))

        # add row for each order
        data = [[], [], [], [], []]

        for order, hon in self.layers.items():
            data[0].append(hon.number_of_nodes(unique=True))
            data[1].append(hon.number_of_edges(unique=True))
            data[2].append(hon.number_of_paths(unique=True))
            # TODO : Use the better method to estimate the DoF
            data[3].append(hon.degrees_of_freedom(mode='path'))
            data[4].append(hon.degrees_of_freedom(mode='ngram'))

            summary.append(row['d|ddd|dd'].format(
                order, *[v[-1] for v in data]))

        # add double line
        summary.append('='*line_length,)

        # if logging is enabled print summary as INFO log
        if config['logging']['enabled']:
            for line in summary:
                Log.info(line.rstrip())
            return None

        # otherwise return the summary as string
        else:
            return '\n'.join(summary)

    def estimate(self):
        """Estimate the optimal order for a multi-order network."""

        Log.debug('start estimate optimal order')
        a = datetime.datetime.now()

        # initialize variables
        observations = None
        max_accepted_order = 1
        max_considerd_order = 6
        threshold = 0.01

        for order in range(2, max_considerd_order+1):
            Log.debug('---')
            Log.debug('> estimating order {}'.format(order))
            accept, p_value = self.likelihood_ratio_test(
                observations, null=order-1, order=order, threshold=threshold)

            if accept:
                max_accepted_order = order

        print(max_accepted_order)

        b = datetime.datetime.now()
        Log.debug('end estimate optiomal order:' +
                  ' {} seconds'.format((b-a).total_seconds()))

    def likelihood_ratio_test(self, observations=None, null=0, order=1,
                              threshold=0.01):

        Log.debug('start likelihood ratio test')
        a = datetime.datetime.now()

        # calculate likelihoods
        likelihood_0 = self.likelihood(observations, order=null, log=True)
        likelihood_1 = self.likelihood(observations, order=order, log=True)

        # calculate test statistics x = -2 * (log L0 - log L1)
        x = -2*(likelihood_0 - likelihood_1)

        # # calculate degrees of freedom
        dof_0 = self.degrees_of_freedom(order=null)
        dof_1 = self.degrees_of_freedom(order=order)

        # calculate the additional degrees of freedom in the alternative model
        delta_dof = dof_1 - dof_0

        # calculate p-value
        p_value = 1 - chi2.cdf(x, delta_dof)

        # reject the null hypothesis if p-value is below the threshold
        accept = p_value < threshold

        # some information
        Log.debug('Likelihood ratio test for order = {}'.format(order))
        Log.debug('test statistics x = {}'.format(x))
        Log.debug('additional degrees of freedom = {}'.format(delta_dof))
        Log.debug('p-value = {}'.format(p_value))
        Log.debug('reject the null hypothesis = {}'.format(accept))

        b = datetime.datetime.now()
        Log.debug('end likelihood ratio test:' +
                  ' {} seconds'.format((b-a).total_seconds()))

        return accept, p_value

    def degrees_of_freedom(self, order=1, mode='path'):

        # TODO add checks for the max order
        max_order = order

        # initialize degrees of freedom
        dof = 0

        for order in range(0, max_order + 1):

            # check if the null model for the given order is
            # already calculated if not calculate new null model
            if self.null_models.get(order, None) is None:
                self.null_models[order] = self.null(order)

            dof += self.null_models[order].degrees_of_freedom(mode=mode)

        return dof

    def likelihood(self, observations=None, order=1, log=True):
        # add log-likelihoods of multiple model layers,
        # assuming that paths are independent

        # TODO add checks for the max order
        max_order = order

        # initialize likelihood
        likelihood = np.float64(0)

        for order in range(0, max_order + 1):
            likelihood += self.layer_likelihood(
                observations=observations, order=order,
                longer_paths=(order == max_order), log=True)

        if not log:
            likelihood = np.exp(likelihood)

        return likelihood

    def layer_likelihood(self, observations=None, order=1,
                         longer_paths=True, log=True,
                         min_length=None):

        if observations is None:
            observations = self.network.paths

        path_lengths = observations.lengths()

        if min_length is None:
            min_length = order
        else:
            min_length = max(order, min_length)
            Log.debug('Add warning')

        if longer_paths:
            max_length = max(path_lengths)
        else:
            max_length = order

        # initialize likelihood
        likelihood = 0

        for uid, path in observations.items():
            if min_length <= len(path) <= max_length:
                likelihood += self.path_likelihood(path, order=order, log=True)

        if not log:
            likelihood = np.exp(likelihood)

        return likelihood

    def path_likelihood(self, observation, order=1, log=True):

        # initialize likelihood
        likelihood = 0

        # get path frequency
        frequency = observation.attributes.frequency

        # 1.) transform the path into a sequence of (two or more)
        # l-th-order edges
        edges = self.path_to_higher_order_edge_uids(observation, order)

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
            transitions[_order] = self.path_to_higher_order_edge_uids(
                observation, _order)[0]

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
        n = list(self.layers[order].nodes.keys())

        for e in edges:
            # calculate the log-likelihood
            likelihood += np.log(self.transition_matrices[order][
                n.index(self.layers[order].edges[e].w.uid),
                n.index(self.layers[order].edges[e].v.uid)])*frequency

        for _order, e in transitions.items():

            # get a list of nodes for the matrix indices
            n = list(self.layers[_order].nodes.keys())

            # calculate the log-likelihood
            likelihood += np.log(self.transition_matrices[_order][
                n.index(self.layers[_order].edges[e].w.uid),
                n.index(self.layers[_order].edges[e].v.uid)])*frequency

        if not log:
            likelihood = np.exp(likelihood)

        return likelihood

    def path_to_higher_order_edge_uids(self, path, order):
        separator = path.separator

        if order == 0:
            edges = ['start'+separator['hon']+w for w in path.as_nodes]

        elif order == 1:
            edges = [path.edges[e].v.uid +
                     separator['hon'] +
                     path.edges[e].w.uid for e in path.as_edges]
        else:
            nodes = [separator['path'].join(
                e) for e in window(path.as_edges, size=order-1)]
            edges = [v+separator['hon']+w for v,
                     w in zip(nodes[:-1], nodes[1:])]

        return edges

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
