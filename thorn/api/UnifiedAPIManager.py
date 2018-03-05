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

        Returns: UnifiedAPIManager instance.

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
        self.delay = delay
        self.p = Producer(**{'bootstrap.servers': self.broker_string, 'group.id': 'mygroup'})
        self.stream_suffixes = config.API_MANAGER_CONFIG['function_stream_suffixes']

    async def filter_exchanges(self):
        '''Given an instantiated list of exchanges, a ccxt universal function,
        and a symbol, filter the exchanges that are have a market w.r.t. the
        symbol and ccxt provides functionality for the instantiated function.

        ASYNC

        Returns: None.

        Raises: AttributeError.
        '''
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
        '''Wrapper function that manages the publication of market data to
        designated streams. Depending on the instantiated function, fetch
        data related to that function and then sleep according to `self.delay`.

        ASYNC

        Args:
            - stop_at (datetime.datetime, optional): Stop managing at this time.
                If None (default), function will continue running indefinitely.
            - params (dict, optional): An optional list of parameters to be sent
                in the API fetch.

        Returns: None.
        '''
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
        '''Primary method for managing function `fetchOrderBook`. Awaits for a
        get request from each exchange's API using the unified `fetch_order_book`
        method. Upon response, add the exchange id to the json and then dump into
        the Kafka stream determined by `self.stream_suffixes['fetchOrderBook']`.

        ASYNC

        Args:
            - symbol (str): The symbol from which to fetch data.
            - exchanges (list[ccxt.exchange]): The list of exchanges whose
                `fetch_order_book` equivalent method will be called to obtain
                data on `symbol`. This list should be filtered via `filter_exchanges`
                prior to use as an argument.
            - params (dict, optional): The optional API request paramters to be sent.

        Returns: None.
        '''

        async def wait_append_produce(symbol, exchange):
            m = await exchange.fetch_order_book(symbol)
            m['exchange'] = exchange.id
            print(exchange.id, symbol)
            self.p.produce(symbol.replace('/', '_')+self.stream_suffixes['fetchOrderBook'], json.dumps(m))

        await asyncio.wait([wait_append_produce(symbol, exchange) for exchange in exchanges])

    async def manage_fetch_ticker(self, symbol, exchanges, params={}):
        '''Primary method for managing function `fetchTicker`. Awaits for a
        get request from each exchange's API using the unified `fetch_ticker`
        method. Upon response, add the exchange id to the json and then dump into
        the Kafka stream determined by `self.stream_suffixes['fetchTicker']`.

        ASYNC

        Args:
            - symbol (str): The symbol from which to fetch data.
            - exchanges (list[ccxt.exchange]): The list of exchanges whose
                `fetch_order_book` equivalent method will be called to obtain
                data on `symbol`. This list should be filtered via `filter_exchanges`
                prior to use as an argument.
            - params (dict, optional): The optional API request paramters to be sent.

        Returns: None.
        '''

        async def wait_append_produce(symbol, exchange):
            m = await exchange.fetch_ticker(symbol)
            m['exchange'] = exchange.id
            self.p.produce(symbol.replace('/', '_')+self.stream_suffixes['fetchTicker'], json.dumps(m))

        await asyncio.wait([wait_append_produce(symbol, exchange) for exchange in exchanges])
