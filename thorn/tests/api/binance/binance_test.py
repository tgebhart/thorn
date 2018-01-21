import unittest
import time
import datetime

from thorn.api.exchanges import BinancePublic
from thorn.api.exchanges import BinanceSocket

bapi = BinancePublic()
PAIR = 'ETHBTC'
CURRENCY = 'ETH'
SOCKET_PAIR = 'bnbbtc'
START = datetime.datetime(2018,1,1,12)
END = datetime.datetime(2018,1,1,13)

class BinancePublicTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        # sleep for 1/3 seconds as to not overwhelm API
        time.sleep(.33)

    def test_exchange_info(self):
        t = bapi.exchange_info()
        self.assertIn('serverTime', t)

    def test_depth(self):
        t = bapi.depth(PAIR)
        self.assertIn('bids', t)

    def test_trades(self):
        t = bapi.trades(PAIR)
        self.assertIsInstance(t, list)

    # requires API Key for some reason (not indicated in docs)
    # def test_historical_trades(self):
    #     t = bapi.historical_trades(PAIR)
    #     print(t)
    #     self.assertIsInstance(t, list)

    def test_agg_trades(self):
        t = bapi.agg_trades(PAIR, start_time=START, end_time=END)
        self.assertIsInstance(t, list)

    def test_klines(self):
        t = bapi.agg_trades(PAIR, start_time=START, end_time=END)
        self.assertIsInstance(t, list)

    def test_hr24(self):
        t = bapi.hr24(pair=PAIR)
        self.assertIn('symbol', t)

    def test_price(self):
        t = bapi.price(pair=PAIR)
        self.assertIn('symbol', t)

    def test_book_ticker(self):
        t = bapi.book_ticker(pair=PAIR)
        self.assertIn('symbol', t)


class BinanceWebsocketTest(unittest.TestCase):

    def wrap_on_message(self, ws, message):
        self.assertIn('exchange', message[0])
        ws.close()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        bws = BinanceSocket('depth', SOCKET_PAIR, on_message=self.wrap_on_message)




if __name__ == '__main__':
    unittest.main()
