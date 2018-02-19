import time
import datetime
import os
import json
import math

import asyncio
import ccxt.async as ccxt

from thorn.utils import get_highest_trading_fee

# class ArbitrageNode(object):
#
#     def __init__(self, base, quote, exchange_name, price, inv_price=None):
#         self.exchange_name = exchange_name
#         self.base = base
#         self.quote = quote
#         self.price = float(price)
#         self.inv_price = 1.0/price if inv_price is None else inv_price
#         if self.price != self.inv_price:
#             print('PAIR PRICE MISMATCH: {} --> {}: {} vs {} --> {}: {}'.format(
#                 self.base, self.quote, self.price, self.quote, self.base, self.inv_price))

class ArbitrageNode(object):

    def __init__(self, currency, exchange_name):
        self.currency = str(currency)
        self.exchange_name = str(exchange_name)
        self.id = self.currency + '_' + self.exchange_name

class DiArbitrageEdge(object):
    '''Directed edge for Arbitrage Graph.
    '''
    def __init__(self, start_node, end_node, price, ts=None):
        self.start_node = start_node
        self.end_node = end_node
        self.price = price
        self.ts = ts
        self.id = self.start_node.id + '_' + self.end_node.id


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
        # add forward exchange rate
        self.add_edge(b, q, p['price'], p['exchange'], ts=p['ts'])
        # add reverse exchange rate
        self.add_edge(q, b, 1/p['price'], p['exchange'], ts=p['ts'])

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

        fee = get_highest_trading_fee(exchange)
        new_price = math.log(price*(1+fee))

        e = DiArbitrageEdge(start_node, end_node, new_price, ts=ts)
        self.children[start_node][end_node] = e
        self.parents[end_node][start_node] = e
        self.edges.add(e)
        self.edge_map[e.id] = e

    def update_pair(self, pair):
        p = self.parse_pair()
        b = ArbitrageNode(p['base'], p['exchange_name'])
        q = ArbitrageNode(p['quote'], p['exchange_name'])

        try:
            head = self.node_map[b.id]
            tail = self.node_map[q.id]
        except KeyError:
            print('pair not in graph')
            return None

        if self.has_edge(head, tail):

            fee = get_highest_trading_fee(p['exchange'])
            new_price = math.log(p['price']*(1+fee))

            self.children[head][tail].price = new_price
            self.children[head][tail].ts = p['ts']
            self.children[tail][head].price = 1.0/new_price
            self.children[tail][head].ts = p['ts']

    def has_edge(self, tail, head):
        return tail in self.nodes and head in self.children[tail]

    def get_edge_weight(self, tail, head):
        if tail not in self.nodes:
            raise ValueError("The tail node is not present in this digraph.")

        if head not in self.nodes:
            raise ValueError("The head node is not present in this digraph.")

        if head not in self.children[tail].keys():
            raise ValueError("The edge ({}, {}) is not in this digraph.".format(tail, head))

        return self.children[tail][head]

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
            return None

        # Unlink children:
        for child in self.children[node]:
            self.edges.remove(self.parents[child][node])
            del self.parents[child][node]

        # Unlink parents:
        for parent in self.parents[node]:
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

    # Step 1: For each node prepare the destination and predecessor
    def initialize(graph, source):
        d = {} # Stands for destination
        p = {} # Stands for predecessor
        for node in graph:
            d[node] = float('Inf') # We start admiting that the rest of nodes are very very far
            p[node] = None
        d[source] = 0 # For the source we know how to reach
        return d, p

def relax(node, neighbour, graph, d, p):
    # If the distance between the node and the neighbour is lower than the one I have now
    if d[neighbour] > d[node] + graph[node][neighbour]:
        # Record this lower distance
        d[neighbour]  = d[node] + graph[node][neighbour]
        p[neighbour] = node

def retrace_negative_loop(p, start):
	arbitrageLoop = [start]
	next_node = start
	while True:
		next_node = p[next_node]
		if next_node not in arbitrageLoop:
			arbitrageLoop.append(next_node)
		else:
			arbitrageLoop.append(next_node)
			arbitrageLoop = arbitrageLoop[arbitrageLoop.index(next_node):]
			return arbitrageLoop


def bellman_ford(graph, source):
    d, p = initialize(graph, source)
    for i in range(len(graph)-1): #Run this until is converges
        for u in graph:
            for v in graph[u]: #For each neighbour of u
                relax(u, v, graph, d, p) #Lets relax it


    # Step 3: check for negative-weight cycles
    for u in graph:
        for v in graph[u]:
        	if d[v] < d[u] + graph[u][v]:
        		return(retrace_negative_loop(p, source))
    return None
#
# paths = []
#
# graph = download()
#
# for key in graph:
# 	path = bellman_ford(graph, key)
# 	if path not in paths and not None:
# 		paths.append(path)
#
# for path in paths:
# 	if path == None:
# 		print("No opportunity here :(")
# 	else:
# 		money = 100
# 		print "Starting with %(money)i in %(currency)s" % {"money":money,"currency":path[0]}
#
# 		for i,value in enumerate(path):
# 			if i+1 < len(path):
# 				start = path[i]
# 				end = path[i+1]
# 				rate = math.exp(-graph[start][end])
# 				money *= rate
# 				print "%(start)s to %(end)s at %(rate)f = %(money)f" % {"start":start,"end":end,"rate":rate,"money":money}
# 	print "\n"
