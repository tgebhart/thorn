import time
import datetime
import os

import requests

from thorn.api.exchanges import PublicExchange
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
        return self.send_check(endpoint='exchangeInfo')

    def depth(self, pair, limit=100):
        if limit not in self.valid_limits:
            raise Exception('Limit is not in valid limits')
        payload = {'symbol': pair,
                    'limit': limit}
        return self.send_check(payload=payload, endpoint='depth')

    def trades(self, pair, limit=500):
        if limit is None or limit > 500:
            raise AttributeError('Limit of {} is above allowable limit'.format(limit))
        payload = {'symbol': pair,
                    'limit': limit}
        return self.send_check(payload=payload, endpoint='trades')

    def historical_trades(self, pair, limit=500, from_id=None):
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
        if pair is not None:
            payload = {'symbol': pair}
            return self.send_check(payload=payload, endpoint='ticker/24hr')
        return self.send_check(endpoint='ticker/24hr')

    def price(self, pair=None):
        if pair is not None:
            payload = {'symbol': pair}
            return self.send_check(payload=payload, endpoint='ticker/price')
        return self.send_check(endpoint='ticker/price')

    def book_ticker(self, pair=None):
        if pair is not None:
            payload = {'symbol': pair}
            return self.send_check(payload=payload, endpoint='ticker/bookTicker')
        return self.send_check(endpoint='ticker/bookTicker')






### end
