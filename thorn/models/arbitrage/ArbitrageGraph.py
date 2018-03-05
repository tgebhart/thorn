import time
import datetime
import os
import json
import math
import networkx as nx
import matplotlib.pyplot as plt

import asyncio
import ccxt.async as ccxt

import numpy as np
np.seterr(all='raise', divide='raise', over='raise', under='raise', invalid='raise')

from thorn.utils import get_highest_trading_fee

class ArbitragePair(object):
    '''A container class for pair information used by the ArbitrageGraph algorithm.

    Args:
        exchange (ccxt.exchange): An instantiated ccxt exchange (ex: ccxt.gemini())
            from which the pair information originated.
        pair (str or tuple): A string representation of the pair (ex: 'ETH/BTC')
            or a tuple where the first argument is the price and the second is
            the quantity.
        price (float): The price, or exchange rate, of the pair.
        quantity (float, optional): The quantity (bid or ask) at the price level.
        ts (int): The timestamp of the pair price information.
    '''

    def __init__(self, exchange, pair, price, quantity=None, ts=None):
        self.exchange = exchange
        self.pair = pair
        self.quantity = quantity
        if isinstance(price, list):
            self.price = price[0]
            self.quantity = price[1]
        elif isinstance(price, float):
            self.price = price
        else:
            raise AttributeError('Price not in valid format!')
        self.ts = ts

    def __eq__(self, other):
        if type(self) == type(other):
            if self.quantity is not None and other.quantity is not None:
                return self.exchange.id == other.exchange.id and self.pair == other.pair and self.price == other.price and self.quantity == other.quantity
            return self.exchange.id == other.exchange.id and self.pair == other.pair and self.price == other.price
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.pair, self.price, self.quantity, self.exchange.id)

class ArbitrageOp(object):
    '''A container class representing an arbitrage opportunity. This is the
    class output of the ArbitrageGraph's `find_opportunities` method.

    Args:
        path (list): The exchange path across the arbitrage graph. The first entry
            is the starting currency, and the last entry is the starting currency.
            The list is ordered according to the order of the nodes one must visit
            through the graph.
        exchange (ccxt.exchange): An instantiated exchange object at which the
            opportunity exists.
        graph (ArbitrageGraph): The arbitrage graph from which the opportunity
            was derived.
        ts (int, optional): The timestamp associated to the opportunity.
    '''

    def __init__(self, path, exchange, graph, ts=None):
        if len(path) > 0:
            self.op, self.gain = self.reformat_path(path, graph)
        self.path = path
        self.exchange = exchange
        self.start = self.path[0].currency
        self.ts = ts

    def __len__(self):
        return len(self.op)

    def __hash__(self):
        return hash(self.start, self.op, self.exchange.id)

    def __eq__(self, other):
        if type(self) == type(other):
            return self.op == other.op and self.gain == other.gain
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        s = '{}: Return: {:.2f}, Cycle of length {} \n'.format(self.start, self.gain, len(self))
        for o in self.op:
            s += '{} --> {} @ {:.4f} \n'.format(o['from'], o['to'], o['price'])
        return s

    def reformat_path(self, path, graph):
        '''Takes opportunity in the form of `path` (a list of pairs)
        '''
        ret = []
        m = 1.0
        for i in range(len(path)-1):
            price = graph.get_edge_price(path[i], path[i+1])
            m = m*price
            p = {'from':path[i].currency,
                'to':path[i+1].currency,
                'price':price}
            ret.append(p)
        return ret, m

class ArbitrageNode(object):
    '''Node object used by the ArbitrageGraph. A node is defined by a currency and
    the exchange the currency is from. The initialization method creates an id
    for the node by concatenating the currency and the exchange name. This id is
    then used to override the equals, not equals, hash, and represenation methods.

    Args:
        currency (str): The currency represented by the node. Ex: BTC
        exchange_name (str): The exchange on which the currency is traded. Ex: gemini

    Returns:
        ArbitrageNode: An instance of the ArbitrageNode class.
    '''
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
    '''Directed edge representation for Arbitrage Graph. The object takes a
    start node, an end node, and a price. The direction of the edge is from start
    to end node and the weight on the edge is represented by the price. The
    initialization method records these data (plus the optioinal timestamp) and
    creates an id for the edge by concatenating the id of the start node with
    the id of the end node. This id is used to override the equals, not equals,
    hash, and representations methods.

    Args:
        start_node (ArbitrageNode): The node from which the directed edge originates.
        end_node (ArbitrageNode): The node at which the edge ends.
        price (float): The price (edge weight) associated with the edge. This
            is intended to represent the exchange rate either with or without fees.
        ts (int, optional): Timestamp at which the price was added or updated.

    Returns:
        DiArbitrageEdge: A DiArbitrageEdge instance.
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
    '''A graphical representation of a currency market. The nodes of this graph
    (of class ArbitrageNode) represent specific currencies. Connections between
    nodes (of class DiArbitrageEdge) represent the conversion rate between
    currencies. This representation may be used to efficiently search for arbitrage
    opportunities.

    The ArbitrageGraph class tracks every node and edge added with a `set` data
    structure. It tracks a map of edges and nodes that map strings of ids to the
    associated ArbitrageNode or DiArbitrageEdge instances. The graph connections
    themselves are tracked through a parent and children dictionary by the class.

    The graph takes dictionary representations of pair price updates that list
    the exchange object, the pair, and the price (exchange rate) of the currency
    pair. This is then parsed and added (via `parse_pair` and `add_pair` methods)
    to the graph in its graphical representation.

    Args:
        pairs (list[dict], optional): A list of pair price dictionaries.
        fees (list[float], optional): An optional list of fees accompanying each
            pair.
    '''

    def __init__(self, pairs=[], fees=[]):
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
        if len(pairs) > 0 and len(fees) == len(pairs):
            for i in range(len(pairs)):
                self.add_pair(pairs[i], fee=fees[i])
        else:
            for p in pairs:
                self.add_pair(p, fee=None)

    def __len__(self):
        return len(self.edges)

    def parse_pair(self, p):
        '''Takes a pair object (shown below) and parses into a dictionary format
        used by following class methods.

        ```
        pair = {
            'exchange':ccxt.gemini(),
            'pair': 'ETH/BTC',
            'price': 0.001
        }
        ```

        Args:
            p (dict): Pair object containing an instantiated exchange, a string
                representing the pair ("Curr1/Curr2") and a float price.

        Raises:
            KeyError: Will raise a KeyError exception if pair is invalid or incorrectly
                formatted.

        Returns:
            dict: An expanded dictionary representation containing information
                necessary for the graphical representation of the pair update.
        '''
        ret = {}
        if isinstance(p, ArbitragePair):
            pair = p.pair
            ret['base'] = pair[:pair.find('/')]
            ret['quote'] = pair[pair.find('/')+1:]
            ret['exchange'] = p.exchange
            ret['exchange_name'] = p.exchange.id
            ret['price'] = float(p.price)
            ret['ts'] = p.ts
            return ret
        elif isinstance(p, dict):
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
                raise KeyError('Invalid `pair` format for dict object')
            return ret
        else:
            raise KeyError('Could not decode pair object')

    def add_pair(self, pair, fee=None):
        '''Adds a pair price update object (dict) to the graph. This method also
        adds trading fees to the price according to `get_highest_trading_fee`.
        The prices on the edges are also computed here wherein the base currency
        (the numerator of "Curr/Curr2" pair) is the source of the edge which
        inherits the `price`.

        Args:
            pair (dict): Pair object containing an instantiated exchange, a string
                representing the pair ("Curr1/Curr2") and a float price. See
                `parse_pair` for an example of the dict structure.
            fee (float, optional): The trading fee for the exchange rate. This
                will default to whatever is returned by `get_highest_trading_fee`
                if not specified.

        Returns:
            None
        '''
        p = self.parse_pair(pair)
        b = ArbitrageNode(p['base'], p['exchange_name'])
        q = ArbitrageNode(p['quote'], p['exchange_name'])
        self.add_node(b)
        self.add_node(q)
        fee = get_highest_trading_fee(p['exchange']) if fee is None else fee
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

    def update_pair(self, pair, fee=None):
        p = self.parse_pair(pair)
        b = ArbitrageNode(p['base'], p['exchange_name'])
        q = ArbitrageNode(p['quote'], p['exchange_name'])

        try:
            tail = self.node_map[b.id]
            head = self.node_map[q.id]
        except KeyError:
            print('pair not in graph')
            return None

        if self.has_edge(tail, head) and self.has_edge(head, tail):

            fee = get_highest_trading_fee(p['exchange']) if fee is None else fee

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

    def draw(self):
        G = self.as_networkx(real=True)
        pos = nx.circular_layout(G)
        nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), node_size = 500)
        labels = nx.get_edge_attributes(G,'weight')
        nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos, arrows=True)
        plt.draw()
        plt.ion()
        plt.show()

    def update_draw(self):
        G = self.as_networkx(real=True)
        pos = nx.circular_layout(G)
        nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), node_size = 500)
        labels = nx.get_edge_attributes(G,'weight')
        nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos, arrows=True)
        plt.draw()
        plt.pause(0.05)

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
    comp = d[node] + graph.get_edge(node, neighbour).price
    if d[neighbour] > comp and not np.isclose(d[neighbour], comp):
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
    '''A python implementation of the Bellman-Ford algorithm. The algorithm
    looks for shortest paths. Unlike Djikstra, the algorithm allows for negative
    edge weights. This allowance provides the opportunity for negative cycle
    detection. This negative cycle detection is useful for determining arbitrage
    opportunities in a graph of currencies.

    The algorithm requires a ArbitrageGraph object and a ArbitrageNode or the
    string representing that node's id (ex: "BTC_gemini") as the source. The
    algorithm then searches for negative cycles and returns the paths that create
    these negative cycles.

    Args:
        graph (ArbitrageGraph): The instantiated ArbitrageGraph over which negative
            cycles are sought.
        source (ArbitrageNode or str): An ArbitrageNode object or the string id
            of such a node. This is the source from which we search for shortest
            paths and, consequently, negative edge cycles.

    Returns:
        list[ArbitrageNode]: If the algorithm finds a negative cycle, it returns
            a list of the nodes that represent this cycle. Otherwise, return None.
    '''
    if isinstance(source, str):
        source = graph.node_map[source]
    d,p = initialize(graph, source)
    for i in range(len(graph.nodes)-1):
        for u in graph.nodes:
            for v in graph.get_children(u):
                relax(u, v, graph, d, p)

    for u in graph.nodes:
        for v in graph.get_children(u):
            comp = d[u] + graph.get_edge(u,v).price
            if d[v] > comp:
                return retrace_negative_loop(p,source)
    return None

def find_opportunities(graph, exchange=None):
    '''Given an ArbitrageGraph object, this function runs all-pairs Bellman-Ford
    to search for arbitrage opportunities. The opportunities are represented as
    paths that cycle from source node back to source node.

    Args:
        graph (ArbitrageGraph): The currency graph upon which to search for opportunities.

    Returns:
        list: A list of paths represented by the node IDs and the price between
            them.
    '''
    ops = []
    for node in graph.nodes:
        path = bellman_ford(graph, node)
        if path is not None and len(path)-1 > 2:
            op = ArbitrageOp(path, exchange, graph)
            if op not in ops:
                ops.append(op)
    return ops
