import unittest
from thorn.api.exchanges import PoloniexPublic

polpapi = PoloniexPublic()

class PoloniexPublicTest(unittest.TestCase):

    def test_return_ticker(self):
        t = polpapi.return_ticker()
        self.assertIn('USDT_BTC', t)


if __name__ == '__main__':
    unittest.main()
