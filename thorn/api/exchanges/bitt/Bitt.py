import time
import datetime
import os

import requests

from thorn.api.exchanges import PublicExchange
from thorn.api.exchanges.bitt import config

class BittPublic(PublicExchange):
    '''Public API class for Bitt. Extends `PublicExchange`'''

    def __init__(self):
        base = config.API_CONFIG['base']
        version = config.API_CONFIG['public_version']
        url = os.path.join(base,version)
        self.default_ticker = config.API_CONFIG['default_ticker']
        self.default_pair = config.API_CONFIG['default_pair']
        super(BittPublic, self).__init__(base=url)

    def send_check(self,payload={}, endpoint=None):
        r, status = self.get(payload=self.filter_none_params(payload), endpoint=endpoint)
        if 'error' in r:
            print('Error in send_check: ', r['error'])
            return None
        return r

    def check_and_reformat_datetime(self, t):
        if isinstance(t, datetime.datetime):
            return int(time.mktime(t.timetuple()))
        if len(str(t)) == 10:
            return t
        return None

    def get_ticker(self, pair):
        payload = {'productPair': pair}
        return self.send_check(payload=payload, endpoint='GetTicker')









### end
