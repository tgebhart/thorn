import unittest
import time
import datetime

from thorn.api.exchanges import LunoPublic

lapi = LunoPublic()
PAIR = 'XBTZAR'
CURRENCY = 'XBT'
START = datetime.datetime(2018,1,1,12)
END = datetime.datetime(2018,1,1,13)

class LunoPublicTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        # sleep for 1/10 seconds as to not overwhelm API
        time.sleep(1)

    def test_ticker(self):
        t = lapi.ticker(PAIR)
        self.assertIn('ask', t)

    def test_tickers(self):
        t = lapi.tickers()
        self.assertIn('tickers', t)

    def test_orderbook(self):
        t = lapi.orderbook(PAIR)
        self.assertIn('bids', t)

    def test_trades(self):
        t = lapi.trades(PAIR, since=START)
        self.assertIn('trades', t)










if __name__ == '__main__':
    unittest.main()
