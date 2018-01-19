import unittest
import time
import datetime

from thorn.api.exchanges import CryptopiaPublic

capi = CryptopiaPublic()
PAIR = capi.default_pair
PAIR2 = 'DOT_LTC'
CURRENCY = capi.default_ticker
START = datetime.datetime(2018,1,15)
END = datetime.datetime(2018,1,16)

class CryptopiaPublicTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        # sleep for 1/10 seconds as to not overwhelm API
        time.sleep(.1)

    def test_get_currencies(self):
        t = capi.get_currencies()
        self.assertIsInstance(t, list)

    def test_get_trade_pairs(self):
        t = capi.get_trade_pairs()
        self.assertIsInstance(t, list)

    def test_get_markets(self):
        t = capi.get_markets()
        self.assertIsInstance(t, list)
        t = capi.get_markets(ticker=CURRENCY, hours=12)
        self.assertIsInstance(t, list)

    def test_get_market(self):
        t = capi.get_market(PAIR)
        self.assertIn('Label', t)

    def test_get_market_history(self):
        t = capi.get_market_history(PAIR)
        self.assertIsInstance(t, list)

    def test_get_market_orders(self):
        t = capi.get_market_orders(PAIR)
        self.assertIn('Buy', t)

    def test_get_market_order_groups(self):
        t = capi.get_market_order_groups([PAIR, PAIR2])
        self.assertIsInstance(t, list)









if __name__ == '__main__':
    unittest.main()
