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
        self.exchanges = exchanges
        # self.exchanges = self.filter_exchanges(exchanges, self.symbol, self.function)
        self.delay = delay
        self.p = Producer(**{'bootstrap.servers': self.broker_string, 'group.id': 'mygroup'})
        print(self.p)
        self.stream_suffixes = config.API_MANAGER_CONFIG['function_stream_suffixes']

    async def filter_exchanges(self):
        ret = []
        for exchange in self.exchanges:
            if exchange.has.get(self.function, False):
                markets = await exchange.load_markets()
                if self.symbol in markets:
                    ret.append(exchange)
        if len(ret) == 0:
            raise AttributeError('filter_exchanges error: no exchanges found with function implemented')
        self.exchanges = ret

    async def manage(self, stop_at=None, params={}):
        if self.function == 'fetchOrderBook':
            if stop_at is not None:
                t = datetime.datetime.utcnow()
                while t < stop_at:
                    await self.manage_fetch_order_book(self.symbol, self.exchanges, params=params)
                    t = datetime.datetime.utcnow()
                    time.sleep(self.delay / 1e3)
            else:
                while True:
                    await self.manage_fetch_order_book(self.symbol, self.exchanges, params=params)
                    time.sleep(self.delay / 1e3)

        if self.function == 'fetchTicker':
            if stop_at is not None:
                t = datetime.datetime.utcnow()
                while t < stop_at:
                    await self.manage_fetch_ticker(self.symbol, self.exchanges, params=params)
                    t = datetime.datetime.utcnow()
                    time.sleep(self.delay / 1e3)
            else:
                while True:
                    await self.manage_fetch_ticker(self.symbol, self.exchanges, params=params)
                    time.sleep(self.delay / 1e3)

    async def manage_fetch_order_book(self, symbol, exchanges, params={}):
        for exchange in exchanges:
            m = await exchange.fetch_order_book(symbol)
            m['exchange'] = exchange.id
            self.p.produce(symbol.replace('/', '_')+self.stream_suffixes['fetchOrderBook'], json.dumps(m))

    async def manage_fetch_ticker(self, symbol, exchanges, params={}):
        for exchange in exchanges:
            m = await exchange.fetch_ticker(symbol)
            m['exchange'] = exchange.id
            self.p.produce(symbol.replace('/', '_')+self.stream_suffixes['fetchTicker'], json.dumps(m))
