import unittest
import time
import math
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

import ccxt.async as ccxt
from thorn.models import ArbitrageGraph
from thorn.models import bellman_ford, find_opportunities

pairs = [
    {
    'exchange': ccxt.gemini(),
    'pair': 'ETH/BTC',
    'price': 0.0873
    },
    {
    'exchange': ccxt.gemini(),
    'pair': 'BTC/USD',
    'price': 10420.000
    },
    {
    'exchange': ccxt.gemini(),
    'pair': 'ETH/USD',
    'price': 924.99,
    'ts': 1518996767361
    }
]

pairs2 = [
    {
    'exchange': ccxt.gemini(),
    'pair': 'ETH/BTC',
    'price': .01
    },
    # {
    # 'exchange': ccxt.gemini(),
    # 'pair': 'BTC/USD',
    # 'price': 1.00
    # },
    {
    'exchange': ccxt.gemini(),
    'pair': 'ETH/USD',
    'price': 1.00,
    'ts': 1518996767361
    },
    {
    'exchange': ccxt.gemini(),
    'pair': 'LTC/USD',
    'price': 1.00
    },
    # {
    # 'exchange': ccxt.gemini(),
    # 'pair': 'LTC/BTC',
    # 'price': 1.00
    # },
    {
    'exchange': ccxt.gemini(),
    'pair': 'BTC/MON',
    'price': 1.00
    },
    {
    'exchange': ccxt.gemini(),
    'pair': 'MON/LTC',
    'price': 1.00
    }
]


class ArbitrageGraphTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # def test_basics(self):
    #     digraph = ArbitrageGraph()
    #     assert len(digraph) == 0
    #
    #     digraph = ArbitrageGraph(pairs=pairs)
    #     assert len(digraph) == 2*len(pairs)
    #
    #     digraph.remove_node('BTC_gemini')
    #     assert len(digraph) == 2
    #
    #     digraph.add_pair(pairs[1])
    #     assert digraph.has_edge('BTC_gemini', 'USD_gemini')
    #     assert digraph.has_edge('USD_gemini', 'BTC_gemini')
    #     digraph.add_pair(pairs[0])
    #     digraph.print_edges()
    #     digraph.print_nodes()
    #     assert len(digraph) == 2*len(pairs)
    #     print('BTC --> USD: {}'.format(digraph.get_edge_price('BTC_gemini', 'USD_gemini')))
    #     print('USD --> BTC: {}'.format(digraph.get_edge_price('USD_gemini', 'BTC_gemini')))
    #     print(1/digraph.get_edge_price('USD_gemini', 'ETH_gemini'), digraph.get_edge_price('ETH_gemini', 'USD_gemini'))
    #     assert len(digraph) == 6
    #
    #     digraph.add_pair(pairs[0])
    #     assert len(digraph) == 6


    def test_bellman_ford(self):

        digraph = ArbitrageGraph(pairs=pairs2, fees=np.zeros(shape=len(pairs2)))
        # assert len(digraph) == 2*len(pairs2)

        paths = []
        paths = find_opportunities(digraph)
        print(paths)

        for path in paths:
            if path == None:
                print('No opportunity found')
            else:
                print("\n")
                money = 1
                print("Starting with %(money)i in %(currency)s" % {"money":money,"currency":path[0]})
                for i, value in enumerate(path):
                    if i+1 < len(path):
                        start = path[i]
                        end = path[i+1]
                        rate = digraph.get_edge_price(start, end)
                        money = money*rate
                        print("%(start)s --> %(end)s @ %(rate)f = %(money)f" % {"start":start,"end":end,"rate":rate,"money":money})

        G = digraph.as_networkx(real=True)

        pos = nx.circular_layout(G)
        nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), node_size = 500)
        labels = nx.get_edge_attributes(G,'weight')
        nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos, arrows=True)
        # plt.show()


if __name__ == '__main__':
    unittest.main()
