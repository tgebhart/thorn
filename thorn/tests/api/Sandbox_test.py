import unittest
import time
import datetime
import threading
import json
import sys

import asyncio
import ccxt.async as ccxt

SYMBOL = 'ETH/BTC'

from thorn.api import UnifiedAPIManager
from thorn.api import config
from thorn.utils import read_private_api_info

keys = read_private_api_info(config.KEY_CONFIG['api_key_location'],
                            config.KEY_CONFIG['api_key_name'])

exchange_name = 'gemini'
exchange = ccxt.gemini({'apiKey':keys[exchange_name]['api_key'], 'secret': keys[exchange_name]['secret']})

asyncio.get_event_loop().run_until_complete(exchange.load_markets())

# try:
#     exchange.urls['api'] = exchange.urls['test']
#     print('API has sandbox')
# except KeyError:
#     print('Exchange does not contain sandbox url')
#     sys.exit()

class ManageThread(threading.Thread):
    def __init__(self, symbol, function, exchanges, delay, loop=None):
        uam = UnifiedAPIManager(symbol, function, exchanges, delay, loop=loop)
        self.uam = uam
        threading.Thread.__init__(self)

    def run(self):
        self.uam.manage()

class ConsumeThread(threading.Thread):
    def __init__(self, topic, pass_test):
        self.topic = topic
        self.pass_test = pass_test
        self.fun = consume
        threading.Thread.__init__(self)

    def run(self):
        self.fun(self.topic, self.pass_test)


class SandboxTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # def test_fetch_balance(self):
    #     bal = asyncio.get_event_loop().run_until_complete(exchange.fetch_balance())
    #     # print(bal)
    #     self.assertIn('info', bal)

    def test_fetch_trades(self):
        for symbol in exchange.markets:                    # ensure you have called loadMarkets() or load_markets() method.
            time.sleep (exchange.rateLimit / 1000)         # time.sleep wants seconds
            trades = asyncio.get_event_loop().run_until_complete(exchange.fetch_trades(symbol))
            print(symbol, trades)




if __name__ == '__main__':
    unittest.main()
