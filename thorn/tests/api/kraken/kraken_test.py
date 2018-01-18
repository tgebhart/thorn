import unittest
import time
import datetime

from thorn.api.exchanges import KrakenPublic

kapi = KrakenPublic()
PAIR = 'XXBTZUSD'
CURRENCY = 'XXBT'
START = datetime.date(2018,1,1)
END = datetime.date(2018,1,2)

class KrakenPublicTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        # sleep for 1/3 seconds as to not overwhelm API
        time.sleep(.33)

    def test_assets(self):
        t = kapi.assets()
        self.assertIn(CURRENCY, t)

    def test_asset_pairs(self):
        default = kapi.asset_pairs()
        self.assertIn(PAIR, default)
        lev = kapi.asset_pairs(info='leverage')
        self.assertIn(PAIR, lev)
        paired = kapi.asset_pairs(pair=[PAIR, 'XXBTEUR'])
        self.assertIn(PAIR, paired)

    def test_ticker(self):
        t = kapi.ticker([PAIR, 'XXBTEUR'])
        self.assertIn(PAIR, t)

    def test_ohlc(self):
        t = kapi.ohlc(PAIR)
        self.assertIn(PAIR, t)

    def test_depth(self):
        t = kapi.depth(PAIR)
        self.assertIn(PAIR, t)

    def test_trades(self):
        t = kapi.trades(PAIR)
        self.assertIn(PAIR, t)

    def test_spread(self):
        t = kapi.spread(PAIR)
        self.assertIn(PAIR, t)


if __name__ == '__main__':
    unittest.main()
