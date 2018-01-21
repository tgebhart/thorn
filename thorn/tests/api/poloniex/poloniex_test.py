import unittest
import time
import datetime

from thorn.api.exchanges import PoloniexPublic
from thorn.api.exchanges import PoloniexSocket

polpapi = PoloniexPublic()
PAIR = 'BTC_NXT'
CURRENCY = 'BTC'
START = datetime.date(2018,1,1)
END = datetime.date(2018,1,2)

# class PoloniexPublicTest(unittest.TestCase):
#
#     def setUp(self):
#         pass
#
#     def tearDown(self):
#         # sleep for 1/3 seconds as to not overwhelm API
#         time.sleep(.33)
#
#     def test_return_ticker(self):
#         t = polpapi.return_ticker()
#         self.assertIn(PAIR, t)
#
#     def test_return_24_volume(self):
#         t = polpapi.return_24_volume()
#         self.assertIn(PAIR, t)
#
#     def test_return_order_vbook(self):
#         tall = polpapi.return_order_book(all_orders=True)
#         self.assertIn(PAIR, tall)
#         t = polpapi.return_order_book(pair=PAIR)
#         self.assertIn('asks', t)
#
#     def test_return_trade_history(self):
#         t = polpapi.return_trade_history(START,END,pair=PAIR)
#         self.assertIsInstance(t,list)
#
#     def test_return_chart_data(self):
#         t = polpapi.return_chart_data(START,END,pair=PAIR)
#         self.assertIsInstance(t,list)
#
#     def test_return_currencies(self):
#         t = polpapi.return_currencies()
#         self.assertIn(CURRENCY, t)
#
#     def test_return_loan_orders(self):
#         t = polpapi.return_loan_orders()
#         self.assertIn('offers', t)

class PoloniexSocketTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def wrap_on_message(self, ws, message):
        print(message)
        # if len(message) > 0:
        #     self.assertIn('exchange', message[0])
        #     ws.close()

    def test_init(self):
        bms = PoloniexSocket('depth', 'BTC_XMR', on_message=self.wrap_on_message)




if __name__ == '__main__':
    unittest.main()
