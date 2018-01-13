import unittest
from thorn.api.exchanges import CoinbasePublic

class CoinbasePublicTest(unittest.TestCase):

    self.cbpapi = CoinbasePublic()

    def test_return_ticker(self):
        self.assertIsNotNone(self.cbpapi.return_ticker())


if __name__ == '__main__':
    unittest.main()
