import time
import datetime
import os
import json

import requests
import websocket

from confluent_kafka import Producer

from thorn.api.exchanges import PublicExchange
from thorn.api.exchanges import Websocket
from thorn.api.exchanges.binance import config

class BinancePublic(PublicExchange):
    '''Public API class for Kraken. Extends `PublicExchange`'''

    def __init__(self):
        base = config.API_CONFIG['base']
        version = config.API_CONFIG['public_version']
        url = os.path.join(base,version)
        self.default_pair = config.API_CONFIG['default_pair']
        self.valid_limits = config.API_CONFIG['valid_limits']
        super(BinancePublic, self).__init__(base=url)

    def send_check(self,payload={}, endpoint=None):
        r, status = self.get(payload=payload, endpoint=endpoint)
        if status is not None:
            if 'code' in r and 'msg' in r:
                print(r)
                print('Bad parameters: ', r['msg'])
                return None
            if r.status_code >= 400 and r.status_code < 500:
                print('Bad GET parameters. No data returned.')
                return None
        return r

    def check_and_reformat_datetime(self, start, end, lim=1):
        if isinstance(start, datetime.datetime) and isinstance(end, datetime.datetime):
            dif = end - start
            if dif.days <= lim:
                start = time.mktime(start.timetuple()) * 1000
                end = time.mktime(end.timetuple()) * 1000
                return int(start), int(end)
            else:
                print('start time and end time must be no less than {} days apart'.format(lim))
        return None, None

    def exchange_info(self):
        '''Return rate limits and list of symbols

        :returns: list - List of product dictionaries

        .. code-block:: python
            {
                "timezone": "UTC",
                "serverTime": 1508631584636,
                "rateLimits": [
                    {
                        "rateLimitType": "REQUESTS",
                        "interval": "MINUTE",
                        "limit": 1200
                    },
                    {
                        "rateLimitType": "ORDERS",
                        "interval": "SECOND",
                        "limit": 10
                    },
                    {
                        "rateLimitType": "ORDERS",
                        "interval": "DAY",
                        "limit": 100000
                    }
                ],
                "exchangeFilters": [],
                "symbols": [
                    {
                        "symbol": "ETHBTC",
                        "status": "TRADING",
                        "baseAsset": "ETH",
                        "baseAssetPrecision": 8,
                        "quoteAsset": "BTC",
                        "quotePrecision": 8,
                        "orderTypes": ["LIMIT", "MARKET"],
                        "icebergAllowed": false,
                        "filters": [
                            {
                                "filterType": "PRICE_FILTER",
                                "minPrice": "0.00000100",
                                "maxPrice": "100000.00000000",
                                "tickSize": "0.00000100"
                            }, {
                                "filterType": "LOT_SIZE",
                                "minQty": "0.00100000",
                                "maxQty": "100000.00000000",
                                "stepSize": "0.00100000"
                            }, {
                                "filterType": "MIN_NOTIONAL",
                                "minNotional": "0.00100000"
                            }
                        ]
                    }
                ]
            }

        '''

        return self.send_check(endpoint='exchangeInfo')

    def depth(self, pair, limit=100):
        '''Get the Order Book for the market
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#order-book

        :param symbol: required
        :type symbol: str
        :param limit:  Default 100; max 100
        :type limit: int
        :returns: API response

        .. code-block:: python
            {
                "lastUpdateId": 1027024,
                "bids": [
                    [
                        "4.00000000",     # PRICE
                        "431.00000000",   # QTY
                        []                # Can be ignored
                    ]
                ],
                "asks": [
                    [
                        "4.00000200",
                        "12.00000000",
                        []
                    ]
                ]
            }

        '''
        if limit not in self.valid_limits:
            raise Exception('Limit is not in valid limits')
        payload = {'symbol': pair,
                    'limit': limit}
        return self.send_check(payload=payload, endpoint='depth')

    def trades(self, pair, limit=500):
        '''Get recent trades (up to last 500).
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#recent-trades-list

        :param symbol: required
        :type symbol: str
        :param limit:  Default 500; max 500.
        :type limit: int
        :returns: API response

        .. code-block:: python
            [
                {
                    "id": 28457,
                    "price": "4.00000100",
                    "qty": "12.00000000",
                    "time": 1499865549590,
                    "isBuyerMaker": true,
                    "isBestMatch": true
                }
            ]

        '''
        if limit is None or limit > 500:
            raise AttributeError('Limit of {} is above allowable limit'.format(limit))
        payload = {'symbol': pair,
                    'limit': limit}
        return self.send_check(payload=payload, endpoint='trades')

    def historical_trades(self, pair, limit=500, from_id=None):
        '''Get older trades.
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#recent-trades-list

        :param symbol: required
        :type symbol: str
        :param limit:  Default 500; max 500.
        :type limit: int
        :param fromId:  TradeId to fetch from. Default gets most recent trades.
        :type fromId: str
        :returns: API response

        .. code-block:: python
            [
                {
                    "id": 28457,
                    "price": "4.00000100",
                    "qty": "12.00000000",
                    "time": 1499865549590,
                    "isBuyerMaker": true,
                    "isBestMatch": true
                }
            ]

        '''
        if limit is None or limit > 500:
            raise AttributeError('Limit of {} is above allowable limit'.format(limit))
        if from_id is not None:
            payload = {'symbol' :pair,
                        'limit': limit,
                        'fromId': from_id}
        else:
            payload = {'symbol': pair,
                        'limit': limit}
        return self.send_check(payload=payload, endpoint='historicalTrades')

    def agg_trades(self, pair, start_time=None, end_time=None, from_id=None, limit=500):
        '''Get compressed, aggregate trades. Trades that fill at the time,
        from the same order, with the same price will have the quantity aggregated.
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#compressedaggregate-trades-list

        :param symbol: required
        :type symbol: str
        :param fromId:  ID to get aggregate trades from INCLUSIVE.
        :type fromId: str
        :param startTime: Timestamp in ms to get aggregate trades from INCLUSIVE.
        :type startTime: int
        :param endTime: Timestamp in ms to get aggregate trades until INCLUSIVE.
        :type endTime: int
        :param limit:  Default 500; max 500.
        :type limit: int
        :returns: API response

        .. code-block:: python
            [
                {
                    "a": 26129,         # Aggregate tradeId
                    "p": "0.01633102",  # Price
                    "q": "4.70443515",  # Quantity
                    "f": 27781,         # First tradeId
                    "l": 27781,         # Last tradeId
                    "T": 1498793709153, # Timestamp
                    "m": true,          # Was the buyer the maker?
                    "M": true           # Was the trade the best price match?
                }
            ]

        '''
        start, end = self.check_and_reformat_datetime(start_time, end_time, lim=1)
        if limit is None or limit > 500:
            raise AttributeError('Limit of {} is above allowable limit'.format(limit))
        if start_time is not None and end_time is not None:
            payload = {'symbol': pair,
                        'startTime': start,
                        'endTime': end}
            return self.send_check(payload=payload, endpoint='aggTrades')
        else:
            if from_id is not None:
                payload = {'symbol': pair,
                            'fromId': from_id,
                            'limit': limit}
            return self.send_check(payload=payload, endpoint='aggTrades')

    def kline(self, pair, start_time=None, end_time=None, from_id=None, limit=500):
        '''Kline/candlestick bars for a symbol. Klines are uniquely identified by their open time.
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#klinecandlestick-data

        :param symbol: required
        :type symbol: str
        :param interval: -
        :type interval: enum
        :param limit: - Default 500; max 500.
        :type limit: int
        :param startTime:
        :type startTime: int
        :param endTime:
        :type endTime: int
        :returns: API response

        .. code-block:: python
            [
                [
                    1499040000000,      # Open time
                    "0.01634790",       # Open
                    "0.80000000",       # High
                    "0.01575800",       # Low
                    "0.01577100",       # Close
                    "148976.11427815",  # Volume
                    1499644799999,      # Close time
                    "2434.19055334",    # Quote asset volume
                    308,                # Number of trades
                    "1756.87402397",    # Taker buy base asset volume
                    "28.46694368",      # Taker buy quote asset volume
                    "17928899.62484339" # Can be ignored
                ]
            ]

        '''
        start, end = self.check_and_reformat_datetime(start_time, end_time, lim=1)
        if limit is None or limit > 500:
            raise AttributeError('Limit of {} is above allowable limit'.format(limit))
        if start_time is not None and end_time is not None:
            payload = {'symbol': pair,
                        'startTime': start,
                        'endTime': end}
            return self.send_check(payload=payload, endpoint='klines')
        else:
            if from_id is not None:
                payload = {'symbol': pair,
                            'fromId': from_id,
                            'limit': limit}
            return self.send_check(payload=payload, endpoint='klines')

    def hr24(self, pair=None):
        '''24 hour price change statistics.
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#24hr-ticker-price-change-statistics

        :param symbol:
        :type symbol: str
        :returns: API response

        .. code-block:: python
            {
                "priceChange": "-94.99999800",
                "priceChangePercent": "-95.960",
                "weightedAvgPrice": "0.29628482",
                "prevClosePrice": "0.10002000",
                "lastPrice": "4.00000200",
                "bidPrice": "4.00000000",
                "askPrice": "4.00000200",
                "openPrice": "99.00000000",
                "highPrice": "100.00000000",
                "lowPrice": "0.10000000",
                "volume": "8913.30000000",
                "openTime": 1499783499040,
                "closeTime": 1499869899040,
                "fristId": 28385,   # First tradeId
                "lastId": 28460,    # Last tradeId
                "count": 76         # Trade count
            }
        OR
        .. code-block:: python
            [
                {
                    "priceChange": "-94.99999800",
                    "priceChangePercent": "-95.960",
                    "weightedAvgPrice": "0.29628482",
                    "prevClosePrice": "0.10002000",
                    "lastPrice": "4.00000200",
                    "bidPrice": "4.00000000",
                    "askPrice": "4.00000200",
                    "openPrice": "99.00000000",
                    "highPrice": "100.00000000",
                    "lowPrice": "0.10000000",
                    "volume": "8913.30000000",
                    "openTime": 1499783499040,
                    "closeTime": 1499869899040,
                    "fristId": 28385,   # First tradeId
                    "lastId": 28460,    # Last tradeId
                    "count": 76         # Trade count
                }
            ]

        '''
        if pair is not None:
            payload = {'symbol': pair}
            return self.send_check(payload=payload, endpoint='ticker/24hr')
        return self.send_check(endpoint='ticker/24hr')

    def price(self, pair=None):
        '''Latest price for a symbol or symbols.
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#24hr-ticker-price-change-statistics

        :param symbol:
        :type symbol: str
        :returns: API response

        .. code-block:: python
            {
                "symbol": "LTCBTC",
                "price": "4.00000200"
            }
        OR
        .. code-block:: python
            [
                {
                    "symbol": "LTCBTC",
                    "price": "4.00000200"
                },
                {
                    "symbol": "ETHBTC",
                    "price": "0.07946600"
                }
            ]

        '''
        if pair is not None:
            payload = {'symbol': pair}
            return self.send_check(payload=payload, endpoint='ticker/price')
        return self.send_check(endpoint='ticker/price')

    def book_ticker(self, pair=None):
        '''Latest price for a symbol or symbols.
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#symbol-order-book-ticker

        :param symbol:
        :type symbol: str
        :returns: API response

        .. code-block:: python
            {
                "symbol": "LTCBTC",
                "bidPrice": "4.00000000",
                "bidQty": "431.00000000",
                "askPrice": "4.00000200",
                "askQty": "9.00000000"
            }
        OR
        .. code-block:: python
            [
                {
                    "symbol": "LTCBTC",
                    "bidPrice": "4.00000000",
                    "bidQty": "431.00000000",
                    "askPrice": "4.00000200",
                    "askQty": "9.00000000"
                },
                {
                    "symbol": "ETHBTC",
                    "bidPrice": "0.07946700",
                    "bidQty": "9.00000000",
                    "askPrice": "100000.00000000",
                    "askQty": "1000.00000000"
                }
            ]

        '''
        if pair is not None:
            payload = {'symbol': pair}
            return self.send_check(payload=payload, endpoint='ticker/bookTicker')
        return self.send_check(endpoint='ticker/bookTicker')


class BinanceSocket(Websocket):

    def __init__(self, stream, symbol, on_message=None):
        self.valid_streams = config.WEBSOCKET_CONFIG['valid_streams']
        if stream not in self.valid_streams:
            raise AttributeError('stream {} not a valid stream'.format(stream))
        self.base = config.WEBSOCKET_CONFIG['base']
        endpoint = str(symbol) + '@' + str(stream)
        self.url = os.path.join(self.base, endpoint)
        self.wrap_on_message = on_message
        om = self.choose_stream_function(stream)
        super(BinanceSocket, self).__init__(self.url, on_message = om,
                                            on_error = self.on_error,
                                            on_open = self.on_open,
                                            on_close = self.on_close)


    def choose_stream_function(self, stream):
        if stream == 'depth':
            return self.on_message_depth

    def on_message_depth(self, ws, message):
        m = json.loads(message)
        if self.wrap_on_message is not None:
            self.wrap_on_message(ws, m)
        else:
            return self.translate_depth(m)

    def validate_time(self, t):
        if isinstance(t, int):
            s = str(t)
            return datetime.datetime.utcfromtimestamp((t * 10**(13 - len(s)))/1000)
        else:
            raise AttributeError('Time t must be an integer')


    def translate_depth(self, message):
        ret = []
        header = {}
        header['exchange'] = 'binance'
        header['stream'] = 'depth_update'
        try:
            header['pair'] = message['s']
            header['timestamp'] = self.generate_timestamp()
            header['stream_start'] = message['U']
            header['stream_end'] = message['u']
            bids = message['b']
            asks = message['a']
        except KeyError:
            return ret
        for bid in bids:
            b = {}
            b['side'] = 'bid'
            b['price'] = bid[0]
            b['quantity'] = bid[1]
            ret.append({**header, **b})
        for ask in asks:
            a = {}
            a['side'] = 'ask'
            a['price'] = ask[0]
            a['quantity'] = ask[1]
            ret.append({**header, **a})
        return ret

    def on_error(self, ws, error):
        print('Error in BinanceSocket: ', error)

    def on_open(self, ws):
        print('BinanceSocket: opened')

    def on_close(self, ws):
        print('BinanceSocket: closed')















































































### end
