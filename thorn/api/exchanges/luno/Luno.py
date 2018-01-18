import time
import datetime
import os

import requests

from thorn.api.exchanges import PublicExchange
from thorn.api.exchanges.luno import config

class LunoPublic(PublicExchange):
    '''Public API class for Kraken. Extends `PublicExchange`'''

    def __init__(self):
        base = config.API_CONFIG['base']
        version = config.API_CONFIG['public_version']
        url = os.path.join(base,version)
        self.default_ticker = config.API_CONFIG['default_ticker']
        super(LunoPublic, self).__init__(base=url)

    def send_check(self,payload={}, endpoint=None):
        r, status = self.get(payload=self.filter_none_params(payload), endpoint=endpoint)
        if 'error' in r:
            print('Error in send_check: ', r['error'])
            return None
        return r

    def check_and_reformat_datetime(self, t):
        if isinstance(t, datetime.datetime):
            return int(time.mktime(t.timetuple()) * 100)
        return None

    def ticker(self, pair):
        payload = {'pair': pair}
        return self.send_check(payload=payload, endpoint='ticker')

    def tickers(self):
        return self.send_check(endpoint='tickers')

    def orderbook(self, pair):
        payload = {'pair': pair}
        return self.send_check(payload=payload, endpoint='orderbook')

    def trades(self, pair, since=None):
        since = self.check_and_reformat_datetime(since)
        payload = {'pair': pair,
                    'since': since}
        return self.send_check(payload=payload, endpoint='trades')












### end
