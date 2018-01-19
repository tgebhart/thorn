import unittest
import time
import datetime

from thorn.api.exchanges import BittrexPublic

bapi = BittrexPublic()
PAIR = bapi.default_pair
CURRENCY = bapi.default_ticker
START = datetime.datetime(2018,1,15)
END = datetime.datetime(2018,1,16)

class BittrexPublicTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        # sleep for 1/10 seconds as to not overwhelm API
        time.sleep(.1)

    def test_get_markets(self):
        t = bapi.get_markets()
        self.assertIsInstance(t, list)

    def test_get_currencies(self):
        t = bapi.get_currencies()
        self.assertIsInstance(t, list)

    def test_get_ticker(self):
        t = bapi.get_ticker(PAIR)
        self.assertIn('Bid', t)

    def test_get_market_summaries(self):
        t = bapi.get_market_summaries()
        self.assertIsInstance(t, list)

    def test_get_market_summary(self):
        t = bapi.get_market_summary(PAIR)
        self.assertIn('MarketName', t[0])

    def test_get_orderbook(self):
        t = bapi.get_orderbook(PAIR)
        self.assertIn('buy', t)

    def test_get_market_history(self):
        t = bapi.get_market_history(PAIR)
        self.assertIsInstance(t, list)














if __name__ == '__main__':
    unittest.main()
