import time
import datetime
import os

import requests

from thorn.api.exchanges import PublicExchange
from thorn.api.exchanges.kucoin import config

class KucoinPublic(PublicExchange):
    '''Public API class for Kucoin. Extends `PublicExchange`'''

    def __init__(self):
        base = config.API_CONFIG['base']
        version = config.API_CONFIG['public_version']
        url = os.path.join(base,version)
        self.default_ticker = config.API_CONFIG['default_ticker']
        self.valid_candle_units = config.API_CONFIG['valid_candle_units']
        self.valid_resolutions = config.API_CONFIG['valid_resolutions']
        super(KucoinPublic, self).__init__(base=url)

    def send_check(self,payload={}, endpoint=None):
        r, status = self.get(payload=self.filter_none_params(payload), endpoint=endpoint)
        if 'error' in r:
            print('Error in send_check: ', r['error'])
            return None
        if 'data' in r:
            return r['data']
        if 'success' in r:
            if r['success']:
                return r
        if 's' in r:
            if r['s'] == 'ok':
                return r

    def check_and_reformat_datetime(self, t):
        if isinstance(t, datetime.datetime):
            return int(time.mktime(t.timetuple()))
        if len(str(t)) == 10:
            return t
        return None

    def tick(self, ticker=None):
        payload = {'symbol': ticker}
        return self.send_check(payload=payload, endpoint='open/tick')

    def orders(self, pair, group=None, limit=None):
        payload = {'symbol': pair,
                    'group': group,
                    'limit': limit}
        return self.send_check(payload=payload, endpoint='open/orders')

    def orders_buy(self, pair, group=None, limit=None):
        payload = {'symbol': pair,
                    'group': group,
                    'limit': limit}
        return self.send_check(payload=payload, endpoint='open/orders-buy')

    def orders_sell(self, pair, group=None, limit=None):
        payload = {'symbol': pair,
                    'group': group,
                    'limit': limit}
        return self.send_check(payload=payload, endpoint='open/orders-sell')

    def deal_orders(self, pair, limit=None, since=None):
        since = self.check_and_reformat_datetime(since)
        payload = {'symbol': pair,
                    'limit': limit,
                    'since': since}
        return self.send_check(payload=payload, endpoint='open/deal-orders')

    def markets(self):
        return self.send_check(endpoint='open/markets')

    def symbols(self, market=None):
        payload = {'market': market}
        return self.send_check(payload=payload, endpoint='open/symbols')

    def coins_trending(self, market=None):
        payload = {'market': market}
        return self.send_check(payload=payload, endpoint='open/coins-trending')

    def kline(self, pair, frm, to, t='1day', limit=None):
        frm = self.check_and_reformat_datetime(frm)
        to = self.check_and_reformat_datetime(to)
        if t not in self.valid_candle_units:
            raise AttributeError('Type t is not a valid candle unit')
        payload = {'symbol': pair,
                    'type': t,
                    'from': frm,
                    'to': to,
                    'limi': limit}
        return self.send_check(payload=payload, endpoint='open/kline')

    def chart_history(self, pair, frm, to, resolution=5):
        frm = self.check_and_reformat_datetime(frm)
        to = self.check_and_reformat_datetime(to)
        if resolution not in self.valid_resolutions:
            raise AttributeError('Resolution is not in acceptable resolution choices: ', self.valid_resolutions)
        payload = {'symbol': pair,
                    'from': frm,
                    'to': to,
                    'resolution': resolution}
        return self.send_check(payload=payload, endpoint='open/chart/history')

    def market_coin_info(self, ticker):
        payload = {'coin': ticker}
        return self.send_check(payload=payload, endpoint='market/open/coin-info')

    def market_coins(self):
        return self.send_check(endpoint='market/open/coins')



### end
