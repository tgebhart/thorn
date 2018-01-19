import unittest
import time
import datetime

from thorn.api.exchanges import BittPublic

bapi = BittPublic()
PAIR = 'BTCUSD'
CURRENCY = 'BTC'
START = datetime.datetime(2018,1,15)
END = datetime.datetime(2018,1,16)

class BittPublicTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        # sleep for 1/10 seconds as to not overwhelm API
        time.sleep(.1)

    def test_get_ticker(self):
        t = bapi.get_ticker(PAIR)
        print(t)
        self.assertIn('hi', t)














if __name__ == '__main__':
    unittest.main()
