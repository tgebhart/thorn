import time
import datetime
import os
import json

import asyncio
import ccxt.async as ccxt

from confluent_kafka import Producer

from thorn.api import config

class UnifiedAPIManager(object):

    def __init__(self, symbol, function, exchanges, delay, brokers=[], loop=None):
        '''Initialization for UnifiedAPIManager class

        - symbol (str): symbol as string.
        - function (str): dictionary of function call properties.
        - exchanges (list[ccxt.exchange]): list of instantiated ccxt exchanges.
        - delay (int): the delay between API calls in ms.
        - brokers (list, optional): broker information for Producer. Defaults to
            config settings.

        Returns:
            UnifiedAPIManager instance.

        '''
        self.brokers = brokers
        if len(self.brokers) < 1:
            self.brokers = config.SOCKET_MANAGER_CONFIG['brokers']
        if len(self.brokers) > 1:
            self.broker_string = ",".join(self.brokers)
        else:
            self.broker_string = self.brokers[0]
        self.symbol = symbol
        self.function = function
        self.loop = asyncio.get_event_loop() if loop is None else loop
        # self.exchanges = self.loop.run_until_complete(self.filter_exchanges(exchanges, self.symbol, self.function))
        self.exchanges = self.filter_exchanges(exchanges, self.symbol, self.function)
        self.delay = delay
        self.p = Producer({'bootstrap.servers': self.broker_string})
        self.stream_suffixes = config.API_MANAGER_CONFIG['function_stream_suffixes']

    def filter_exchanges(self, exchanges, symbol, function):
        ret = []
        for exchange in exchanges:
            if exchange.has.get(function, False):
                markets = self.loop.run_until_complete(exchange.load_markets())
                if symbol in markets:
                    ret.append(exchange)
        if len(ret) == 0:
            raise AttributeError('filter_exchanges error: no exchanges found with function implemented')
        return ret

    async def fetch(self, function, symbol, params=None):
        if params is None:
            return await function(symbol)
        else:
            return await function(symbol, params)

    def manage(self, stop_at=None, params=None):
        if self.function == 'fetchOrderBook':
            if stop_at is not None:
                t = datetime.datetime.utcnow()
                while t < stop_at:
                    self.manage_fetch_order_book(self.symbol, self.exchanges, params=params)
                    t = datetime.datetime.utcnow()
                    time.sleep(self.delay / 1e3)
            else:
                while True:
                    self.manage_fetch_order_book(self.symbol, self.exchanges, params=params)
                    time.sleep(self.delay / 1e3)

        if self.function == 'fetchTicker':
            if stop_at is not None:
                t = datetime.datetime.utcnow()
                while t < stop_at:
                    self.manage_fetch_ticker(self.symbol, self.exchanges, params=params)
                    t = datetime.datetime.utcnow()
                    time.sleep(self.delay / 1e3)
            else:
                while True:
                    self.manage_fetch_ticker(self.symbol, self.exchanges, params=params)
                    time.sleep(self.delay / 1e3)

    def manage_fetch_order_book(self, symbol, exchanges, params=None):
        for exchange in exchanges:
            m = self.loop.run_until_complete(self.fetch(exchange.fetch_order_book, symbol, params=params))
            m['exchange'] = exchange.id
            self.p.produce(symbol.replace('/', '_')+self.stream_suffixes['fetchOrderBook'], json.dumps(m))

    def manage_fetch_ticker(self, symbol, exchanges, params=None):
        for exchange in exchanges:
            m = self.loop.run_until_complete(self.fetch(exchange.fetch_ticker, symbol, params=params))
            m['exchange'] = exchange.id
            self.p.produce(symbol.replace('/', '_')+self.stream_suffixes['fetchTicker'], json.dumps(m))
