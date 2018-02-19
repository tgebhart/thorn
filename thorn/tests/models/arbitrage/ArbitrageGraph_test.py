import unittest
import time

import ccxt.async as ccxt
from thorn.models import ArbitrageGraph

pairs = [
    {
    'exchange': ccxt.gemini(),
    'pair': 'ETH/BTC',
    'price': .0873
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


class ArbitrageGraphTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_basics(self):
        digraph = ArbitrageGraph()
        assert len(digraph) == 0

        digraph = ArbitrageGraph(pairs=pairs)
        assert len(digraph) == 2*len(pairs)

        digraph.remove_node('BTC_gemini')
        assert len(digraph) == 4
        #
        # digraph.add_arc(8, 7, 20.0)
        # assert digraph.has_arc(8, 7)
        # assert 20.0 == digraph.get_arc_weight(8, 7)
        # assert digraph.number_of_arcs() == 1
        #
        # digraph.add_arc(9, 8, 10.0)
        # assert digraph.number_of_arcs() == 2
        # assert digraph.get_arc_weight(9, 8) == 10.0
        # assert digraph.has_arc(9, 8)
        # assert not digraph.has_arc(8, 9)
        # digraph.remove_node(8)
        # assert not digraph.has_arc(9, 8)
        # assert digraph.number_of_arcs() == 0
        #
        # digraph.remove_node(5)
        # assert len(digraph) == 8
        #
        # digraph.add_arc(0, 3, 1.0)
        # digraph.add_arc(1, 3, 2.0)
        # digraph.add_arc(3, 6, 3.0)
        # digraph.add_arc(3, 7, 4.0)
        #
        # assert digraph.number_of_arcs() == 4
        #
        # assert 0 in digraph.get_parents_of(3)
        # assert 1 in digraph.get_parents_of(3)
        # assert 6 in digraph.get_children_of(3)
        # assert 7 in digraph.get_children_of(3)
        #
        # try:
        #     digraph.get_arc_weight(3, 100)
        #     assert False
        # except Exception:
        #     pass
        #
        # try:
        #     digraph.get_arc_weight(100, 3)
        #     assert False
        # except Exception:
        #     pass
        #
        # try:
        #     digraph.get_arc_weight(2, 3)
        #     assert False
        # except Exception:
        #     pass



if __name__ == '__main__':
    unittest.main()
