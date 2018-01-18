import time
import datetime
import os

import requests

from thorn.api.exchanges import PublicExchange
from thorn.api.exchanges.bitfinex import config

class BitfinexPublic(PublicExchange):
    '''Public API class for Kraken. Extends `PublicExchange`'''

    def __init__(self):
        base = config.API_CONFIG['base']
        version = config.API_CONFIG['public_version']
        url = os.path.join(base,version)
        self.default_ticker = config.API_CONFIG['default_ticker']
        super(BitfinexPublic, self).__init__(base=url)

    def send_check(self,payload={}, endpoint=None):
        r, status = self.get(payload=self.filter_none_params(payload), endpoint=endpoint)
        if 'message' in r:
            print('Error in send_check: ', r['message'])
            return None
        return r

    def check_and_reformat_datetime(self, t):
        if isinstance(t, datetime.datetime):
            return time.mktime(t.timetuple())
        return None

    def pubticker(self, ticker):
        return self.send_check(endpoint='pubticker/'+str(ticker))

    def stats(self, ticker):
        return self.send_check(endpoint='stats/'+str(ticker))

    def lendbook(self, currency, limit_bids=50, limit_asks=50):
        payload = {'limit_bids': limit_bids,
                    'limit_asks': limit_asks}
        return self.send_check(payload=payload, endpoint='lendbook/'+str(currency))

    def book(self, ticker, limit_bids=50, limit_asks=50, group=1):
        if group not in [0,1]:
            raise AttributeError('Group may only be 0 or 1')
        payload = {'limit_bids': limit_bids,
                    'limit_asks': limit_asks,
                    'group': group}
        return self.send_check(payload=payload, endpoint='book/'+str(ticker))


    def trades(self, ticker, timestamp=None, limit_trades=50):
        timestamp = self.check_and_reformat_datetime(timestamp)
        payload = {'timestamp': timestamp,
                    'limit_trades': limit_trades}
        return self.send_check(payload=payload, endpoint='trades/'+str(ticker))


    def lends(self, currency, timestamp=None, limit_lends=50):
        timestamp = self.check_and_reformat_datetime(timestamp)
        payload = {'timestamp': timestamp,
                    'limit_trades': limit_lends}
        return self.send_check(payload=payload, endpoint='lends/'+str(currency))

    def symbols(self):
        return self.send_check(endpoint='symbols')

    def symbols_details(self):
        return self.send_check(endpoint='symbols_details')









### end
