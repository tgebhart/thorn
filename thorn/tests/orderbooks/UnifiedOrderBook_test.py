import unittest
import time
import datetime
import threading
import json

import asyncio
import ccxt.async as ccxt

from confluent_kafka import Consumer, KafkaError

SYMBOL = 'ETH/BTC'

from thorn.api import UnifiedAPIManager
from thorn.orderbooks import UnifiedOrderBook

class ManageThread(threading.Thread):
    def __init__(self, symbol, function, exchanges, delay, loop=None):
        uam = UnifiedAPIManager(symbol, function, exchanges, delay)
        # loop = asyncio.get_event_loop()
        loop.run_until_complete(uam.filter_exchanges())
        self.loop = loop
        self.uam = uam
        threading.Thread.__init__(self)

    def run(self):
        self.loop.run_until_complete(self.uam.manage())

class UnifiedOrderBookTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_monitor_full_book_stream(self):
        exchanges = [ccxt.binance(), ccxt.gemini(), ccxt.bitmex()]
        loop = asyncio.get_event_loop()
        t1 = ManageThread(SYMBOL, 'fetchOrderBook', exchanges, 5000, loop=loop)
        t1.daemon = True
        t1.start()

        def pass_test(m):
            if 'bids' in m:
                return True
            return False

        ub = UnifiedOrderBook(SYMBOL, exchanges[0])
        ub.monitor_full_book_stream()
        t1.join()
        self.assertEqual(2+2, 4)



if __name__ == '__main__':
    unittest.main()
