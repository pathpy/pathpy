#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : MOGen.py -- MOGen models for pathpy
# Author    : Christoph Gote <cgote@ethz.ch>
# Time-stamp: <Thu 2020-07-13 17:27 cgote>
#
# Copyright (c) 2016-2020 Pathpy Developers
# =============================================================================

import datetime
import numpy as np
import collections
import itertools
import pandas as pd
import multiprocessing
from tqdm import tqdm
import math
from copy import copy
from scipy.sparse import dok_matrix, csr_matrix, eye, issparse
from scipy.linalg import toeplitz
from scipy.special import binom
import scipy.sparse.linalg as sla
import matplotlib.pyplot as plt
from pathpy import logger, config, Network

# create logger
LOG = logger(__name__)

###############################################################################

class MultiOrderMatrix:
    def __init__(self, matrix, node_id_dict):
        assert matrix.shape[0] == matrix.shape[1] #square matrix
        assert len(node_id_dict) == matrix.shape[0] #entry for each matrix row/col exists
        assert min(node_id_dict.values()) == 0
        assert max(node_id_dict.values()) == len(node_id_dict) - 1
        assert len(set(node_id_dict.values())) == len(node_id_dict)
        assert sum([type(x)==int for x in node_id_dict.values()]) == len(node_id_dict)
        
        self.matrix = csr_matrix(matrix)
        self.node_id_dict = {(k,) if not type(k) == tuple else k: v for k, v in node_id_dict.items()}
        self.id_node_dict = {v: k for k, v in self.node_id_dict.items()}
        self.nodes = list(set((fon,) for hon in self.node_id_dict.keys() for fon in hon if not fon == '+'))
        self.nodes += list(set(hon[-2:] for hon in self.node_id_dict.keys() if hon[-1] == '+'))
        self.nodes = sorted(self.nodes, key=lambda x: (x[-1] == '+', len(x), x[-1]))
        
    def __str__(self):
        decimals = 2
        
        idx = [self.id_node_dict[i] for i in range(self.matrix.shape[0])]
        
        if issparse(self.matrix):
            matrix = self.matrix.todense()
        else:
            matrix = self.matrix
        
        out = '\t'
        for node in idx:
            out += ','.join(node) + '\t'
        row = 0
        for node in idx:
            out += '\n' + ','.join(node) + '\t'
            for col in range(matrix.shape[1]):
                if matrix[row, col] == 0:
                    out += '.' + '\t'
                else:
                    out += '{:.{}f}'.format(matrix[row, col], decimals) + '\t'
            row += 1
        return out

    def __repr__(self):
        return self.__str__()
    
    def __add__(self, other):
        assert self.node_id_dict == other.node_id_dict
        return MultiOrderMatrix(self.matrix + other.matrix, self.node_id_dict)
    
    def __sub__(self, other):
        assert self.node_id_dict == other.node_id_dict
        return MultiOrderMatrix(self.matrix - other.matrix, self.node_id_dict)
    
    def to_dataframe(self, decimals=None):
        idx = [self.id_node_dict[i] for i in range(self.matrix.shape[0])]
        if decimals:
            matrix = np.round(self.matrix.todense(), decimals)
        else:
            matrix = self.matrix.todense()
        return pd.DataFrame(matrix, index=idx, columns=idx)
    
    def _repr_html_(self):
        return self.to_dataframe(decimals=2).to_html()
    
    def display(self, decimals=2):
        display(self.to_dataframe(decimals=decimals))
        
    def remove_zero_order(self):
        assert ('*',) in self.node_id_dict.keys()
        
        idx = list(self.node_id_dict.values())
        idx.remove(self.node_id_dict[('*',)])
        for node in self.node_id_dict.keys():
            if node[-1] == '+':
                idx.remove(self.node_id_dict[node])
        matrix = self.matrix[idx][:,idx]
        
        node_id_dict = {self.id_node_dict[idx]: v for v, idx in enumerate(sorted(idx))}
                
        return MultiOrderMatrix(matrix, node_id_dict)
        
    def integrate_zero_order(self):
        assert ('*',) in self.node_id_dict.keys()
        start_nodes = [('*',)]
        end_nodes = [x for x in self.node_id_dict.keys() if x[-1] == '+']
        idx = list(v for k, v in self.node_id_dict.items() if not k in start_nodes + end_nodes)

        start_dist = self.matrix[self.node_id_dict[('*',)],idx]
                
        end_prob = self.matrix[idx,:][:,[self.node_id_dict[x] for x in end_nodes]]
        
        matrix = self.matrix[idx][:,idx].todense() + end_prob.sum(axis=1) @ start_dist
        
        node_id_dict = {self.id_node_dict[idx]: v for v, idx in enumerate(sorted(idx))}
        
        return MultiOrderMatrix(matrix, node_id_dict)
    
    def start_distribution(self):
        assert ('*',) in self.node_id_dict.keys()
        start_nodes = [('*',)]
        end_nodes = [x for x in self.node_id_dict.keys() if x[-1] == '+']
        
        start_dist = self.to_dataframe().loc[
            start_nodes,
            [x for x in self.node_id_dict.keys() if x not in start_nodes + end_nodes]]
        return start_dist
    
    def end_probability(self):
        assert ('*',) in self.node_id_dict.keys()
        start_nodes = [('*',)]
        end_nodes = [x for x in self.node_id_dict.keys() if x[-1] == '+']
        
        end_prob = self.to_dataframe().loc[
            [x for x in self.node_id_dict.keys() if x not in start_nodes + end_nodes],
            end_nodes]
        return end_prob
    
    def to_first_order(self):
        fon_id_dict = {n: i for i, n in enumerate(self.nodes)}
        
        hon = np.matrix([fon_id_dict[(self.id_node_dict[i][-1],)
                                     if self.id_node_dict[i][-1] != '+' else self.id_node_dict[i][-2:]]
                         for i in range(max(self.id_node_dict) + 1)])
        fon = np.matrix([fon_id_dict[n] for n in self.nodes])
        N = csr_matrix(np.equal(hon.T,fon))
        
        matrix = N.T / N.T.sum(axis=1)[:, None] @ self.matrix @ N
                
        return MultiOrderMatrix(matrix, fon_id_dict)

###############################################################################

def unwrap_self_count_transitions(arg, **kwarg):
    return MOGen._count_transitions(arg, **kwarg)

def unwrap_self_get_log_likelihood_path(arg, **kwarg):
    return MOGen._get_log_likelihood_path(arg, **kwarg)

def unwrap_self_generate_paths_chunk(arg, **kwarg):
    return MOGen._generate_path_chunk(arg, **kwarg)

class MOGen:
    """A generative mulit-order model for variable-length paths in networks."""
    
    def __init__(self, paths, max_order=1, model_selection=True):       
        """Initialise MOGen."""
        self.paths = {tuple(x.uid for x in p.nodes): paths[p]['frequency'] for p in paths}
        self.network = Network()
        for e in paths.edges:
            self.network.add_edge(e)
        self.max_order = max_order
        self.model_selection = model_selection

        # initialise variables
        self.optimal_maximum_order = None
        self.A = None
        self.T = None
        self.log_L = None
        self.dof = None
        self.AIC = None
        self.models = collections.defaultdict(lambda: {})
        self.log_L_offset = None
        
    def update_max_order(self, max_order):
        """Updates the maximum order considered by MOGen's model selection.
           Note that a new estimate is required for this to take effect."""
        self.max_order = max_order
        
    def update_model_selection(self, model_selection):
        """Updates the model_selection parameter. If True models up to max_order will be considered.
           Otherwise only the model with max_order is computed.
           Note that a new estimate is required for this to take effect."""
        self.model_selection = model_selection

    def _get_log_likelihood_offset(self, paths):
        """Computes the log likelihood offset."""
        def log_factorial(n, thresh=1000):
            """Computes the log factorial of a given number."""
            # For n < thresh we compute the log factorial directly.
            if n < thresh:
                return math.log(math.factorial(n))
            # For larger n we use Stirling's approximation
            else:
                return n * math.log(n) - n + 1 # Stirling's approximation
                
        return log_factorial(sum(self.paths.values())) - sum(map(log_factorial, self.paths.values()))
        
    def _chunks(self, iterable, n):
        if n > len(iterable):
            n = len(iterable)
            
        chunksize = len(iterable) / n
        for i in range(n):
            iterator = itertools.islice(iterable, int(i*chunksize), int((i+1)*chunksize))
            if type(iterable) is list:
                yield list(iterator)
            elif type(iterable) is dict:
                yield {x: iterable[x] for x in iterator}
            else:
                assert True==False
                
    def _count_transitions(args):
        counter = collections.Counter()

        for path, frequency in args['paths'].items():
            mask = toeplitz(min(len(path), args['order'])*[1] + \
                            (len(path)-args['order'])*[0], \
                            1*[1] + (len(path)-1)*[0])
            multi_order_path = tuple(map(lambda x: tuple(x[x != None]), np.where(mask, path, None)))
            multi_order_path = (('*',),) + multi_order_path + (multi_order_path[-1] + ('+',),)

            for s, t in zip(multi_order_path, multi_order_path[1:]):
                counter[(s,t)] += frequency

        return counter  
    
    def _get_multi_order_transitions(self, order, no_of_processes=multiprocessing.cpu_count(), verbose=True):
        n = min(int(np.ceil(len(self.paths)/config['MOGen']['paths_per_chunk'])), no_of_processes)
        
        args = [{'paths': path_chunk, 'order': order} for path_chunk in self._chunks(self.paths, n)]
        
        counter = collections.Counter()
        with multiprocessing.Pool(no_of_processes) as p:
            with tqdm(total=len(args),
                      desc='order:{1:>3}; T     ({0} prcs)'.format(no_of_processes, order),
                      disable=not verbose) as pbar:
                for c in p.imap_unordered(unwrap_self_count_transitions, args, chunksize=1):
                    counter += c
                    pbar.update(1)
            
        return counter

    
    def _get_multi_order_adjacency_matrix(self, order, no_of_processes=multiprocessing.cpu_count(), verbose=True):
        multi_order_transitions = self._get_multi_order_transitions(order,
                                                                    no_of_processes=no_of_processes,
                                                                    verbose=verbose)

        nodes = list(set(n for transition in multi_order_transitions.keys() for n in transition))
        nodes.sort(key=lambda x: (x[-1] == '#', len(x), x[-1]))
        node_id_dict = dict(zip(nodes, range(len(nodes))))

        row = []
        col = []
        data = []
        for s, t in multi_order_transitions:
            row.append(node_id_dict[s])
            col.append(node_id_dict[t])
            data.append(multi_order_transitions[(s,t)])
        A = dok_matrix((len(node_id_dict), len(node_id_dict)))
        A[row, col] = data
        
        return MultiOrderMatrix(A, node_id_dict)
    
    
    def _get_multi_order_transition_matrix(self, order, no_of_processes=multiprocessing.cpu_count(),
                                           A=None, verbose=True):
        if not A:
            A = self._get_multi_order_adjacency_matrix(order,
                                                       no_of_processes=multiprocessing.cpu_count(),
                                                       verbose=verbose)
        
        T = copy(A)
        T.matrix = T.matrix / T.matrix.sum(axis=1)[:, None]
        
        return T
    
    
    def _get_log_likelihood_path(args):
        log_L = 0
        for path, frequency in args['paths'].items():
            mask = toeplitz(min(len(path), args['order'])*[1] + \
                            (len(path)-args['order'])*[0], \
                            1*[1] + (len(path)-1)*[0])
            multi_order_path = tuple(map(lambda x: tuple(x[x != None]), np.where(mask, path, None)))
            multi_order_path = (('*',),) + multi_order_path + (multi_order_path[-1] + ('+',),)          

            for s, t in zip(multi_order_path, multi_order_path[1:]):
                if s in args['node_id_dict'] and t in args['node_id_dict']:
                    log_L += np.log(args['T'][args['node_id_dict'][s], args['node_id_dict'][t]]) * frequency
                else: # the transition is not in the model and therefore has probability 0
                    log_L += -np.inf
        return log_L
    
    def _compute_log_likelihood(self, order, T, no_of_processes=multiprocessing.cpu_count(), verbose=True):      
        n = min(int(np.ceil(len(self.paths)/config['MOGen']['paths_per_chunk'])), no_of_processes)
        
        args = [{'paths': path_chunk,
                 'order': order,
                 'T': T.matrix,
                 'node_id_dict': T.node_id_dict} for path_chunk in self._chunks(self.paths, n)]
        
        log_L = 0
        with multiprocessing.Pool(no_of_processes) as p:
            with tqdm(total=len(args),
                      desc='order:{1:>3}; log_L ({0} prcs)'.format(no_of_processes, order),
                      disable=not verbose) as pbar:
                for log_likelihood_path in p.imap_unordered(unwrap_self_get_log_likelihood_path, args, chunksize=1):
                    log_L += log_likelihood_path
                    pbar.update(1)
                
        return log_L
    
    def _compute_degrees_of_freedom(self, order):
        # generate binary adjacency matrix
        A = self.network.adjacency_matrix(weight=None)
                
        # compute k
        P = A.copy()
        dof = A.shape[0] - 1 + P.sum()
        for i in range(1, order):
            P *= A
            dof += P.sum()
        return int(dof)
    
    def _compute_AIC(self, order, T, no_of_processes=multiprocessing.cpu_count(), verbose=True):
        
        log_L = self._compute_log_likelihood(order, T, no_of_processes=no_of_processes, verbose=verbose) + \
                self.log_L_offset
        dof = self._compute_degrees_of_freedom(order)
        
        AIC = 2*dof - 2*log_L

        return AIC, log_L, dof
    
    def _compute_order(self, order, no_of_processes=multiprocessing.cpu_count(), verbose=True):
        A = self._get_multi_order_adjacency_matrix(order, no_of_processes=no_of_processes, verbose=verbose)
        T = self._get_multi_order_transition_matrix(order, no_of_processes=no_of_processes, A=A, verbose=verbose)
        AIC, log_L, dof  = self._compute_AIC(order, T, no_of_processes=no_of_processes, verbose=verbose)

        self.models[order]['A'] = A
        self.models[order]['T'] = T
        self.models[order]['log_L'] = log_L
        self.models[order]['dof'] = dof
        self.models[order]['AIC'] = AIC
    
    def summary(self, print_summary=True):
        """Returns a summary of the multi-order model."""

        # TODO: Find better solution for printing
        # TODO: Move to util
        line_length = 54
        row = {}
        row['==='] = '='*line_length
        row['s|ss|sss'] = '{:^3s} | {:^9s} {:^9s} | {:^9s} {:^6s} {:>9s}'
        row['d|dd|fdf'] = '{:^3d} | {:^9d} {:^9d} | {:^9.2f} {:^6d} {:>9.2f}'
        row['d|dd|fdf (highlight)'] = '\033[1m{:^3d}\033[0m | \033[1m{:^9d} {:^9d}\033[0m |' + \
                                      ' \033[1m{:^9.2f} {:^6d} {:>9.2f}\033[0m'
        
        # initialize summary text
        summary: list = [
            row['==='],
            'MOGen model',
            '- Model Selection '.ljust(line_length, '-')
        ]

        # add general information
        summary.append(row['s|ss|sss'].format(
            'K', 'nodes', 'edges', 'log L', 'dof', 'AIC'))

        # add row for each order
        data = [[], [], [], [], []]

        if self.model_selection:
            orders = list(range(1, self.max_order+1))
        else:
            orders = [self.max_order]
        
        for order in orders:           
            try:
                data[0].append(len(self.models[order]['A'].node_id_dict))
                data[1].append(int(np.sum(np.sum(self.models[order]['A'].matrix))))
                data[2].append(self.models[order]['log_L'])
                data[3].append(self.models[order]['dof'])
                data[4].append(self.models[order]['AIC'])
            except KeyError:
                if print_summary:
                    print('Model has not been fit')
                    return None
                else:
                    return 'Model has not been fit'
            if order == self.optimal_maximum_order:
                summary.append(row['d|dd|fdf (highlight)'].format(
                    order, *[v[-1] for v in data]))
            else:
                summary.append(row['d|dd|fdf'].format(
                    order, *[v[-1] for v in data]))
                
        # add double line
        summary.append('='*line_length,)

        if print_summary:
            for line in summary:
                print(line.rstrip())
            return None
        else:
            return '\n'.join(summary)
    
    def __str__(self):
        return self.summary(print_summary=False)

    def __repr__(self):
        return self.summary(print_summary=False)
    
    def fit(self, no_of_processes=multiprocessing.cpu_count(), verbose=True):
        """Estimate the optimal MOGen from all models up to max_order."""
        
        LOG.debug('start estimate optimal order')
        a = datetime.datetime.now()

        # log likelihood offset
        if self.log_L_offset == None:
            self.log_L_offset = self._get_log_likelihood_offset(self)
        
        # orders that still have to be computed
        cur_orders = set(self.models.keys())
        if self.model_selection:
            req_orders = set(range(1, self.max_order+1))
        else:
            req_orders = {self.max_order}
            
        # compute orders not yet computed
        for order in req_orders.difference(cur_orders):
            self._compute_order(order, no_of_processes=no_of_processes, verbose=verbose)
            
        AICs = collections.defaultdict(lambda: list())
        for order in req_orders:
            AICs[self.models[order]['AIC']].append(order)
            
        self.optimal_maximum_order = min(AICs[min(AICs.keys())])
        if verbose:
            print('Selected optimal maximum order K={} from candidates.'
                  .format(self.optimal_maximum_order))
            self.summary()
        
        self.A = self.models[self.optimal_maximum_order]['A']
        self.T = self.models[self.optimal_maximum_order]['T']
        self.log_L = self.models[self.optimal_maximum_order]['log_L']
        self.dof = self.models[self.optimal_maximum_order]['dof']
        self.AIC = self.models[self.optimal_maximum_order]['AIC']

        b = datetime.datetime.now()
        LOG.debug('end estimate optiomal order:' +
                  ' {} seconds'.format((b-a).total_seconds()))
        
        return self

    def plot(self):
        if self.model_selection:
            orders = list(range(1, self.max_order+1))
        else:
            orders = [self.max_order]
        
        assert all(order in self.models for order in orders)
        
        AIC = collections.OrderedDict((order, self.models[order]['AIC']) for order in orders)
        log_L = collections.OrderedDict((order, self.models[order]['log_L']) for order in orders)
        dof = collections.OrderedDict((order, self.models[order]['dof']) for order in orders)

        style = {'color': '#218380', 'marker': 'o', 'linestyle': 'dashed', 'linewidth': 2, 'markersize': 9}
        highlight = {'color': '#218380', 'marker': 'o','markersize': 20, 'alpha': .3}

        fig = plt.figure(figsize=[21,6])
        plt.subplot(1,3,1)
        plt.plot(self.optimal_maximum_order, self.AIC, **highlight)
        plt.plot(AIC.keys(), AIC.values(), **style)
        plt.xlabel('max order')
        plt.ylabel('AIC')
        plt.yscale('log')
        plt.subplot(1,3,2)
        plt.plot(self.optimal_maximum_order, -self.log_L, **highlight)
        plt.plot(log_L.keys(), [-x for x in log_L.values()], **style)
        plt.xlabel('max order')
        plt.ylabel('-log(L)')
        plt.yscale('log')
        plt.subplot(1,3,3)
        plt.plot(self.optimal_maximum_order, self.dof, **highlight)
        plt.plot(dof.keys(), dof.values(), **style)
        plt.xlabel('max order')
        plt.ylabel('dof')
        plt.yscale('log')
        plt.show()

    def _generate_path_chunk(args):
        generated_paths_hon_chunk = collections.Counter()

        for i in range(args['no_of_paths']):
            generated_path = (args['start_node'],)
            while generated_path[-1][-1] != '+':
                c = np.random.choice(list(args['id_node_dict'].keys()),
                                     p=np.ravel(args['mat'][args['node_id_dict'][generated_path[-1]]].todense()))
                generated_path += ((args['id_node_dict'][c]),)
            
            generated_paths_hon_chunk[generated_path] += 1
        
        return generated_paths_hon_chunk
        
        
    def predict(self, no_of_paths, max_order=None, seed=None, start_node=('*',),
                       no_of_processes=multiprocessing.cpu_count(), paths_per_process=1000):
        
        np.random.seed(None)
        
        if max_order:
            assert max_order in self.models
            mat = self.models[max_order]['T'].matrix
            node_id_dict = self.models[max_order]['T'].node_id_dict
        else:
            mat = self.T.matrix
            node_id_dict = self.T.node_id_dict
        id_node_dict = {v: k for k, v in node_id_dict.items()}
        nodes = [id_node_dict[k] for k in sorted(id_node_dict)]
        
        assert start_node in node_id_dict.keys()

        splits = []
        for i in range(max(1, int(np.floor(no_of_paths / paths_per_process))),0,-1):
            splits.append(round((no_of_paths-sum(splits))/i))
        
        args = [{'no_of_paths': split,
                 'start_node': start_node,
                 'id_node_dict': id_node_dict,
                 'node_id_dict': node_id_dict,
                 'mat': mat} for split in splits]
                
        generated_paths_hon = collections.Counter()
        with multiprocessing.Pool(no_of_processes) as p:
            with tqdm(total=len(args)) as pbar:
                for generated_paths_hon_chunk in p.imap_unordered(unwrap_self_generate_paths_chunk, args, chunksize=1):
                    generated_paths_hon += generated_paths_hon_chunk
                    pbar.update(1)

        generated_paths = {}
        
        for k, v in generated_paths_hon.items():
            if start_node == ('*',):
                generated_paths[tuple(x[-1] for x in k[1:-1])] = v
            else:
                generated_paths[k[0] + tuple(x[-1] for x in k[1:-1])] = v
        
        return generated_paths
    
    
    def pagerank(self, max_order=None):
        if max_order:
            T = self.models[max_order]['T'].integrate_zero_order()
        else:
            T = self.T.integrate_zero_order()

        _, v = sla.eigs(T.matrix.T, k=1, which="LM")
        v = list(map(np.abs, np.real(v)))
        v = v / sum(v)
        c = collections.defaultdict(lambda: 0)
        for node in T.node_id_dict.keys():
            pr = v[T.node_id_dict[node]]
            if pr.imag == 0:
                c[node[-1]] += pr.real
            else:
                assert True==False
        pagerank = pd.DataFrame([v for k, v in c.items()],
                                   index=c.keys(),
                                   columns=['score']).sort_values('score', ascending=False)
        return pagerank
    
    
    def mean_first_passage_time(self, max_order=None, recurrence=False):
        if max_order:
            T = self.models[max_order]['T'].integrate_zero_order()
        else:
            T = self.T.integrate_zero_order()
            
        M = MultiOrderMatrix(np.zeros(shape=(len(T.node_id_dict), len(T.node_id_dict))), T.node_id_dict)
        M.matrix = M.matrix.tolil()
        
        for target in T.node_id_dict.keys():
            T_target = T.matrix.tolil()

            for node in T.node_id_dict:    
                if node == target:
                    T_target[T.node_id_dict[node],:] = 0

            res = np.linalg.inv(np.eye(T_target.shape[0]) - T_target) - np.eye(T_target.shape[0])

            res = MultiOrderMatrix(res, T.node_id_dict)
            
            M.matrix[:,[res.node_id_dict[target]]] = res.matrix @ np.ones(shape=(res.matrix.shape[0],1))

        M = M.to_first_order()
            
        if recurrence:
            pr = self.pagerank(max_order=max_order)
            M.matrix += np.diag([1 / pr.loc[node[-1],'score'] for node in T.nodes])

        return M
    
    
    def fundamental_matrix(self, max_order=None):
        if max_order:
            T = self.models[max_order]['T'].remove_zero_order()
        else:
            T = self.T.remove_zero_order()
        
        N = np.linalg.inv(np.identity(T.matrix.shape[0]) - T.matrix)
        return MultiOrderMatrix(N, T.node_id_dict)
    
    
    def transient_matrix(self, max_order=None):
        N = self.fundamental_matrix(max_order=max_order)
        
        H = (N.matrix - np.identity(N.matrix.shape[0])) @ np.linalg.inv(np.diag(np.diag(N.matrix.todense())))
        
        return MultiOrderMatrix(H, N.node_id_dict)

    
# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
