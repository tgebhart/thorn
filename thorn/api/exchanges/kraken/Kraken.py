import time
import datetime

import requests

from thorn.api.exchanges import PublicExchange
from thorn.api.exchanges.kraken import config

class KrakenPublic(PublicExchange):
    '''Public API class for Kraken. Extends `PublicExchange`'''

    def __init__(self):
        base = config.API_CONFIG['base']
        self.default_pair = config.API_CONFIG['default_pair']
        self.valid_intervals = config.API_CONFIG['valid_intervals']
        super(KrakenPublic, self).__init__(base=base)

    def send_check(self,payload={}, endpoint=None):
        r = self.get(payload=payload, endpoint=endpoint)
        if len(r['error']) > 0:
            print('Error in send_check: ', r)
            return None
        return r['result']

    def assets(self):
        return self.send_check(endpoint='Assets')

    def asset_pairs(self, info='info', pair=None):
        if pair is not None:
            payload = {'info': info,
                        'pair': pair}
        else:
            payload = {'info': info}
        return self.send_check(payload=payload, endpoint='AssetPairs')

    def ticker(self, pairs):
        if pairs is None:
            pairs = [self.default_pair]
        payload = {'pair': pairs}
        return self.send_check(payload=payload, endpoint='Ticker')

    def ohlc(self, pair, interval=1):
        if interval not in self.valid_intervals:
            raise Exception('Interval {} is not a valid interval for ohlc'.format(interval))
        payload = {'pair': pair,
                    'interval': interval}
        return self.send_check(payload=payload, endpoint='OHLC')

    def depth(self, pair, count=None):
        if count is not None:
            payload = {'pair': pair,
                        'count': count}
        else:
            payload = {'pair': pair}
        return self.send_check(payload=payload, endpoint='Depth')

    def trades(self, pair, since=None):
        if since is not None:
            payload = {'pair': pair,
                        'since': since}
        else:
            payload = {'pair': pair}
        return self.send_check(payload=payload, endpoint='Trades')

    def spread(self, pair, since=None):
        if since is not None:
            payload = {'pair': pair,
                        'since': since}
        else:
            payload = {'pair': pair}
        return self.send_check(payload=payload, endpoint='Spread')








### end
