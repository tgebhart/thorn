import unittest
import time
import datetime

from thorn.api.exchanges import KucoinPublic

kapi = KucoinPublic()
PAIR = 'ETH-BTC'
CURRENCY = 'BTC'
START = datetime.datetime(2018,1,15)
END = datetime.datetime(2018,1,16)

class KucoinPublicTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        # sleep for 1/10 seconds as to not overwhelm API
        time.sleep(.1)

    def test_tick(self):
        t = kapi.tick()
        self.assertIn('coinType', t[0])

    def test_orders(self):
        t = kapi.orders(PAIR)
        self.assertIn('SELL', t)

    def test_orders_buy(self):
        t = kapi.orders_buy(PAIR)
        self.assertIsInstance(t, list)

    def test_orders_sell(self):
        t = kapi.orders_sell(PAIR)
        self.assertIsInstance(t, list)

    def test_deal_orders(self):
        t = kapi.deal_orders(PAIR, since=START)
        self.assertIsInstance(t, list)
        t = kapi.deal_orders(PAIR)
        self.assertIsInstance(t, list)

    def test_markets(self):
        t = kapi.markets()
        self.assertIsInstance(t, list)

    def test_symbols(self):
        t = kapi.symbols()
        self.assertIsInstance(t, list)

    def test_coins_trending(self):
        t = kapi.coins_trending()
        self.assertIn('coinPair', t[0])

    def test_kline(self):
        t = kapi.kline(PAIR, START, END)
        self.assertIn('coinPair', t[0])

    def test_chart_history(self):
        t = kapi.chart_history(PAIR, START, END)
        self.assertIn('c', t)

    def test_market_coin_info(self):
        t = kapi.market_coin_info(CURRENCY)
        self.assertIn('coin', t)

    def test_market_coins(self):
        t = kapi.market_coins()
        self.assertIn('coin', t[0])






if __name__ == '__main__':
    unittest.main()
