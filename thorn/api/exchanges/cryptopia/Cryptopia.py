import time
import datetime
import os

import requests

from thorn.api.exchanges import PublicExchange
from thorn.api.exchanges.cryptopia import config

class CryptopiaPublic(PublicExchange):
    '''Public API class for Cryptopia. Extends `PublicExchange`'''

    def __init__(self):
        base = config.API_CONFIG['base']
        url = base
        self.default_ticker = config.API_CONFIG['default_ticker']
        self.default_pair = config.API_CONFIG['default_pair']
        super(CryptopiaPublic, self).__init__(base=url)

    def send_check(self,payload={}, endpoint=None):
        r, status = self.get(payload=self.filter_none_params(payload), endpoint=endpoint)
        if r is not None:
            if not r['Success']:
                    print('error found in send_check: ', r['Message'])
                    return None
            return r['Data']
        return None

    def check_and_reformat_datetime(self, t):
        if isinstance(t, datetime.datetime):
            return int(time.mktime(t.timetuple()) * 1000)
        if len(str(t)) == 10:
            return t
        return None

    def get_currencies(self):
        return self.send_check(endpoint='GetCurrencies')

    def get_trade_pairs(self):
        return self.send_check(endpoint='GetTradePairs')

    def get_markets(self, ticker=None, hours=24):
        if ticker is not None:
            endpoint = os.path.join('GetMarkets', str(ticker), str(hours))
        else:
            endpoint = os.path.join('GetMarkets', str(hours))
        return self.send_check(endpoint=endpoint)

    def get_market(self, pair, hours=24):
        endpoint = os.path.join('GetMarket', str(pair), str(hours))
        return self.send_check(endpoint=endpoint)

    def get_market_history(self, pair, hours=24):
        endpoint = os.path.join('GetMarketHistory', str(pair), str(hours))
        return self.send_check(endpoint=endpoint)

    def get_market_orders(self, pair, hours=24):
        endpoint = os.path.join('GetMarketOrders', str(pair), str(hours))
        return self.send_check(endpoint=endpoint)

    def get_market_order_groups(self, pairs, order_count=100):
        pairs = '-'.join(pairs)
        endpoint = os.path.join('GetMarketOrderGroups', pairs, str(order_count))
        return self.send_check(endpoint=endpoint)






### end
