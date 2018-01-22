import unittest
import time
import datetime

from thorn.api.exchanges import GeminiPublic
from thorn.api.exchanges import GeminiSocket

gpi = GeminiPublic()
PAIR = gpi.default_pair
CURRENCY = gpi.default_ticker
START = datetime.datetime(2018,1,15)
END = datetime.datetime(2018,1,16)
# 
# class GeminiPublicTest(unittest.TestCase):
#
#     def setUp(self):
#         pass
#
#     def tearDown(self):
#         # sleep for 1/10 seconds as to not overwhelm API
#         time.sleep(.1)
#
#     def test_symbols(self):
#         t = gpi.symbols()
#         self.assertIsInstance(t, list)
#
#     def test_pubticker(self):
#         t = gpi.pubticker(PAIR)
#         self.assertIn('bid', t)
#
#     def test_book(self):
#         t = gpi.book(PAIR)
#         self.assertIn('bids', t)
#
#     def test_trades(self):
#         t = gpi.trades(PAIR, since=END)
#         self.assertIsInstance(t, list)
#
#     def test_auction(self):
#         t = gpi.auction(PAIR)
#         self.assertIsInstance(t, dict)
#
#     def test_auction_history(self):
#         t = gpi.auction_history(PAIR, since=END)
#         self.assertIsInstance(t, list)

class GeminiSocketTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def wrap_on_message(self, ws, message):
        print(message)
        if message is not None and len(message) > 0:
            self.assertIn('exchange', message[0])
            ws.close()

    def test_init(self):
        bms = GeminiSocket(PAIR, on_message=self.wrap_on_message)







if __name__ == '__main__':
    unittest.main()
