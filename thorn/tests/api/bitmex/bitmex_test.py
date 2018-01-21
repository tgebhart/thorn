import unittest
import time
import datetime

from thorn.api.exchanges import BitmexPublic
from thorn.api.exchanges import BitmexSocket

bapi = BitmexPublic()
PAIR = 'XBTUSD'
CURRENCY = 'XBT'
INDEX = '.XBT'
START = datetime.datetime(2018,1,1,12)
END = datetime.datetime(2018,1,1,13)

# class BitmexPublicTest(unittest.TestCase):
#
#     def setUp(self):
#         pass
#
#     def tearDown(self):
#         # sleep for 1/10 seconds as to not overwhelm API
#         time.sleep(.1)
#
#     def test_instrument(self):
#         t = bapi.instrument()
#         self.assertIsInstance(t, list)
#
#     def test_instrument_active(self):
#         t = bapi.instrument_active(start_time=START, end_time=END)
#         self.assertIsInstance(t, list)
#
#     def test_instrument_active_and_indices(self):
#         t = bapi.instrument_active_and_indices()
#         self.assertIsInstance(t, list)
#
#     def test_instrument_active_intervals(self):
#         t = bapi.instrument_active_intervals()
#         self.assertIn('intervals', t)
#
#     def test_instrument_composite_index(self):
#         t = bapi.instrument_composite_index(INDEX)
#         self.assertIsInstance(t, list)
#
#     def test_instrument_indices(self):
#         t = bapi.instrument_indices()
#         self.assertIsInstance(t, list)
#
#     def test_insurance(self):
#         t = bapi.insurance()
#         self.assertIsInstance(t, list)
#
#     def test_liquidation(self):
#         t = bapi.liquidation()
#         self.assertIsInstance(t, list)
#
#     def test_order_book(self):
#         t = bapi.order_book(CURRENCY)
#         self.assertIsInstance(t, list)
#
#     def test_quote(self):
#         t = bapi.quote()
#         self.assertIsInstance(t, list)
#
#     def test_quote_bucketed(self):
#         t = bapi.quote_bucketed()
#         self.assertIsInstance(t, list)
#
#     def test_settlement(self):
#         t = bapi.settlement()
#         self.assertIsInstance(t, list)
#
#     def test_stats(self):
#         t = bapi.stats()
#         self.assertIsInstance(t, list)
#
#     def test_stats_history(self):
#         t = bapi.stats_history()
#         self.assertIsInstance(t, list)
#
#     def test_stats_history_usd(self):
#         t = bapi.stats_history_usd()
#         self.assertIsInstance(t, list)
#
#     def test_trade(self):
#         t = bapi.trade()
#         self.assertIsInstance(t, list)
#
#     def test_trade_bucketed(self):
#         t = bapi.trade_bucketed()
#         self.assertIsInstance(t, list)

class BitmexSocketTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def wrap_onMessage(self, message, isBinary):
        print(message)
        if message is not None and len(message) > 0:
            self.assertIn('exchange', message[0])
            ws.close()

    def test_init(self):
        bms = BitmexSocket('orderBookL2', PAIR, onMessage=self.wrap_onMessage)





if __name__ == '__main__':
    unittest.main()
