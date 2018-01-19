import time
import datetime
import os

import requests

from thorn.api.exchanges import PublicExchange
from thorn.api.exchanges.bittrex import config

class BittrexPublic(PublicExchange):
    '''Public API class for Bittrex. Extends `PublicExchange`'''

    def __init__(self):
        base = config.API_CONFIG['base']
        self.public_version = config.API_CONFIG['public_version']
        url = os.path.join(base, self.public_version, 'public')
        self.valid_orderbook_types = config.API_CONFIG['valid_orderbook_types']
        self.default_ticker = config.API_CONFIG['default_ticker']
        self.default_pair = config.API_CONFIG['default_pair']
        super(BittrexPublic, self).__init__(base=url)

    def send_check(self,payload={}, endpoint=None):
        r, status = self.get(payload=self.filter_none_params(payload), endpoint=endpoint)
        if not r['success']:
            print('Error in send_check: ', r['message'])
            return None
        return r['result']

    def check_and_reformat_datetime(self, t):
        if isinstance(t, datetime.datetime):
            return int(time.mktime(t.timetuple()))
        if len(str(t)) == 10:
            return t
        return None

    def get_markets(self):
        return self.send_check(endpoint='getmarkets')

    def get_currencies(self):
        return self.send_check(endpoint='getcurrencies')

    def get_ticker(self, pair):
        payload = {'market': pair}
        return self.send_check(payload=payload, endpoint='getticker')

    def get_market_summaries(self):
        return self.send_check(endpoint='getmarketsummaries')

    def get_market_summary(self, pair):
        payload = {'market': pair}
        return self.send_check(payload=payload, endpoint='getmarketsummary')

    def get_orderbook(self, pair, t='both'):
        if t not in self.valid_orderbook_types:
            raise AssertionError('Type t is not a valid orderbook type')
        payload = {'market': pair,
                    'type': t}
        return self.send_check(payload=payload, endpoint='getorderbook')

    def get_market_history(self, pair):
        payload = {'market': pair}
        return self.send_check(payload=payload, endpoint='getmarkethistory')










### end
