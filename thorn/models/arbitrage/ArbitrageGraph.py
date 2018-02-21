import time
import datetime
import os
import json
import math
import networkx as nx

import asyncio
import ccxt.async as ccxt

import numpy as np
np.seterr(all='raise', divide='raise', over='raise', under='raise', invalid='raise')

from thorn.utils import get_highest_trading_fee

class ArbitrageNode(object):

    def __init__(self, currency, exchange_name):
        self.currency = str(currency)
        self.exchange_name = str(exchange_name)
        self.id = self.currency + '_' + self.exchange_name

    def __eq__(self, other):
        if type(other) == type(self):
            return self.currency == other.currency and self.exchange_name == other.exchange_name
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return self.id

class DiArbitrageEdge(object):
    '''Directed edge for Arbitrage Graph.
    '''
    def __init__(self, start_node, end_node, price, ts=None):
        self.start_node = start_node
        self.end_node = end_node
        self.price = price
        self.ts = ts
        self.id = self.start_node.id + '_' + self.end_node.id

    def __eq__(self, other):
        if type(other) == type(self):
            return self.id == other.id and self.price == other.price
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return "{} --> {}: {}".format(self.start_node.id, self.end_node.id, self.price)


class ArbitrageGraph(object):

    def __init__(self, pairs=[]):
        '''
        Expected format for `pairs`:
        [
            {
                'exchange':ccxt.gemini(),
                'pair': 'ETH/BTC',
                'price': 0.001
            },
        ...
        ]
        '''
        self.nodes = set()
        self.node_map = {}
        self.children = {}
        self.parents = {}
        self.edges = set()
        self.edge_map = {}
        if len(pairs) > 0:
            for p in pairs:
                self.add_pair(p)

    def __len__(self):
        return len(self.edges)

    def parse_pair(self, p):
        ret = {}
        try:
            pair = p['pair']
            ret['base'] = pair[:pair.find('/')]
            ret['quote'] = pair[pair.find('/')+1:]
            ret['exchange'] = p['exchange']
            ret['exchange_name'] = p['exchange'].id
            ret['price'] = float(p['price'])
            if 'ts' in p:
                ret['ts'] = p['ts']
            else:
                ret['ts'] = None
        except KeyError:
            raise KeyError('Invalid `pair` format')
        return ret

    def add_pair(self, pair):
        p = self.parse_pair(pair)
        b = ArbitrageNode(p['base'], p['exchange_name'])
        q = ArbitrageNode(p['quote'], p['exchange_name'])
        self.add_node(b)
        self.add_node(q)
        fee = get_highest_trading_fee(p['exchange'])
        fee = 0
        # add forward exchange rate
        self.add_edge(b, q, p['price']*(1.0+fee), p['exchange'], ts=p['ts'])
        # add reverse exchange rate
        self.add_edge(q, b, (1.0/p['price'])*(1.0+fee), p['exchange'], ts=p['ts'])

    def add_node(self, node):
        if node in self.nodes:
            return None
        self.nodes.add(node)
        self.node_map[node.id] = node
        self.children[node] = {}
        self.parents[node] = {}

    def add_edge(self, start_node, end_node, price, exchange, ts=None):
        if start_node not in self.nodes:
            self.add_node(start_node)
        if end_node not in self.nodes:
            self.add_node(end_node)

        new_price = -np.log(price)

        e = DiArbitrageEdge(start_node, end_node, new_price, ts=ts)
        if e.id in self.edge_map:
            print('edge already in edge map', e.id)
            return None
        self.children[start_node][end_node] = e
        self.parents[end_node][start_node] = e
        self.edges.add(e)
        self.edge_map[e.id] = e

    def update_pair(self, pair):
        p = self.parse_pair()
        b = ArbitrageNode(p['base'], p['exchange_name'])
        q = ArbitrageNode(p['quote'], p['exchange_name'])

        try:
            tail = self.node_map[b.id]
            head = self.node_map[q.id]
        except KeyError:
            print('pair not in graph')
            return None

        if self.has_edge(tail, head) and self.has_edge(head, tail):

            fee = get_highest_trading_fee(p['exchange'])
            fee=0

            new_price = -np.log(p['price']*(1.0+fee))
            new_price_rev = -np.log((1.0/p['price'])*(1.0+fee))

            self.children[tail][head].price = new_price
            self.children[tail][head].ts = p['ts']
            self.children[head][tail].price = new_price_rev
            self.children[head][tail].ts = p['ts']

    def get_node(self, name):
        return self.node_map.get(name)

    def has_edge(self, tail, head):
        if isinstance(tail, str):
            tail = self.node_map[tail]
        if isinstance(head, str):
            head = self.node_map[head]
        return tail in self.nodes and head in self.children[tail]

    def get_edge(self, tail, head):
        if isinstance(tail, str):
            tail = self.node_map[tail]
        if isinstance(head, str):
            head = self.node_map[head]
        if tail not in self.nodes:
            raise ValueError("The tail node is not present in this digraph.")
        if head not in self.nodes:
            raise ValueError("The head node is not present in this digraph.")
        if head not in self.children[tail].keys():
            raise ValueError("The edge ({}, {}) is not in this digraph.".format(tail, head))

        return self.children[tail][head]

    def get_edge_price(self, tail, head):
        return np.exp(-1.0*self.get_edge(tail, head).price)

    def remove_edge(self, tail, head):
        '''Removes the directed arc from `tail` to `head`.'''
        if isinstance(tail, str):
            tail = self.node_map[tail]
        if isinstance(head, str):
            head = self.node_map[head]

        if tail not in self.nodes:
            return None
        if head not in self.nodes:
            return None

        e = self.children[tail][head]
        del self.edge_map[e.id]
        self.edges.remove(e)
        del self.children[tail][head]
        del self.parents[head][tail]

    def remove_node(self, node):
        '''Removes the node from this digraph. Also removes all arcs incident on
        the input node.
        '''
        if isinstance(node, str):
            node = self.node_map[node]

        if node not in self.nodes:
            print('node not in node list')
            return None

        # Unlink children:
        for child in self.children[node]:
            del self.edge_map[self.parents[child][node].id]
            self.edges.remove(self.parents[child][node])
            del self.parents[child][node]

        # Unlink parents:
        for parent in self.parents[node]:
            del self.edge_map[self.children[parent][node].id]
            self.edges.remove(self.children[parent][node])
            del self.children[parent][node]

        del self.node_map[node.id]
        self.nodes.remove(node)
        del self.children[node]
        del self.parents[node]

    def get_parents(self, node):
        '''Returns all parents of `node`.'''
        if node not in self.nodes:
            return []
        return list(self.parents[node].keys())

    def get_children(self, node):
        '''Returns all children of `node`.'''
        if node not in self.nodes:
            return []
        return list(self.children[node].keys())

    def print_edges(self):
        print(list(map(lambda x: x.id, self.edges)))

    def print_nodes(self):
        print(list(map(lambda x: x.id, self.nodes)))

    def as_networkx(self, real=True):
        G = nx.DiGraph()
        if real:
            for edge in self.edges:
                G.add_edge(edge.start_node.id, edge.end_node.id, weight=self.get_edge_price(edge.start_node, edge.end_node))
        else:
            for edge in self.edges:
                G.add_edge(edge.start_node.id, edge.end_node.id, weight=edge.price)
        return G
# Step 1: For each node prepare the destination and predecessor
def initialize(graph, source):
	d = {} # Stands for destination
	p = {} # Stands for predecessor
	for node in graph.nodes:
		d[node] = float('Inf') # We start admiting that the rest of nodes are very very far
		p[node] = None
	d[source] = 0 # For the source we know how to reach
	return d, p

def relax(node, neighbour, graph, d, p):
    # If the distance between the node and the neighbour is lower than the one I have now
    if d[neighbour] > d[node] + graph.get_edge(node, neighbour).price:
        d[neighbour] = d[node] + graph.get_edge(node,neighbour).price
        p[neighbour] = node

def retrace_negative_loop(p,start):
    arbitrageLoop = [start]
    next_node = start
    while True and next_node is not None:
        next_node = p[next_node]
        if next_node not in arbitrageLoop:
            arbitrageLoop.append(next_node)
        else:
            arbitrageLoop.append(next_node)
            arbitrageLoop = arbitrageLoop[arbitrageLoop.index(next_node):]
            arbitrageLoop.reverse()
            return arbitrageLoop


def bellman_ford(graph, source):
    if isinstance(source, str):
        source = graph.node_map[source]
    d,p = initialize(graph, source)
    for i in range(len(graph.nodes)+len(graph.nodes)//2):
        for u in graph.nodes:
            for v in graph.get_children(u):
                relax(u, v, graph, d, p)

    for u in graph.nodes:
        for v in graph.get_children(u):
            if d[v] > d[u] + graph.get_edge(u,v).price:
                return retrace_negative_loop(p,source)
    return None

def find_opportunities(graph):
    paths = []
    for node in graph.nodes:
        path = bellman_ford(graph, node)
        if path not in paths and path is not None:
            paths.append(path)
    return paths
