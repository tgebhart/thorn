import unittest
import time
import datetime

from thorn.api.exchanges import BitfinexPublic

bapi = BitfinexPublic()
PAIR = 'BTCUSD'
CURRENCY = 'USD'
START = datetime.datetime(2018,1,1,12)
END = datetime.datetime(2018,1,1,13)

class BitfinexPublicTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        # sleep for 1/10 seconds as to not overwhelm API
        time.sleep(1)

    def test_pubticker(self):
        t = bapi.pubticker(PAIR)
        self.assertIn('bid', t)

    def test_stats(self):
        t = bapi.stats(PAIR)
        self.assertIn('period', t[0])

    def test_lendbook(self):
        t = bapi.lendbook(CURRENCY)
        self.assertIn('bids', t)

    def test_book(self):
        t = bapi.book(PAIR)
        self.assertIn('bids', t)

    def test_trades(self):
        t = bapi.trades(PAIR)
        self.assertIsInstance(t, list)
        t = bapi.trades(PAIR, timestamp=START)
        self.assertIsInstance(t, list)

    def test_lends(self):
        t = bapi.lends(CURRENCY)
        self.assertIn('rate', t[0])
        t = bapi.lends(CURRENCY, timestamp=END)
        self.assertIn('rate', t[0])

    def test_symbols(self):
        t = bapi.symbols()
        self.assertIsInstance(t, list)

    def test_symbols_details(self):
        t = bapi.symbols_details()
        self.assertIsInstance(t, list)








if __name__ == '__main__':
    unittest.main()
