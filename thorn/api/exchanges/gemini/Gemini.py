import time
import datetime
import os

import requests

from thorn.api.exchanges import PublicExchange
from thorn.api.exchanges import Websocket
from thorn.api.exchanges.gemini import config

class GeminiPublic(PublicExchange):
    '''Public API class for Bittrex. Extends `PublicExchange`'''

    def __init__(self):
        base = config.API_CONFIG['base']
        self.public_version = config.API_CONFIG['public_version']
        url = os.path.join(base, self.public_version)
        self.default_ticker = config.API_CONFIG['default_ticker']
        self.default_pair = config.API_CONFIG['default_pair']
        super(GeminiPublic, self).__init__(base=url)

    def send_check(self,payload={}, endpoint=None):
        r, status = self.get(payload=self.filter_none_params(payload), endpoint=endpoint)
        if 'result' in r:
            if r['result'] == 'error':
                print('error found in send_check: ', r['message'])
                return None
        return r

    def check_and_reformat_datetime(self, t):
        if isinstance(t, datetime.datetime):
            return int(time.mktime(t.timetuple()) * 1000)
        if len(str(t)) == 10:
            return t
        return None

    def symbols(self):
        return self.send_check(endpoint='symbols')

    def pubticker(self, pair):
        return self.send_check(endpoint=os.path.join('pubticker',str(pair)))

    def book(self, pair, limit_bids=50, limit_asks=50):
        payload = {'limit_bids': limit_bids,
                    'limit_asks': limit_asks}
        return self.send_check(payload=payload, endpoint=os.path.join('book', str(pair)))

    def trades(self, pair, since=None, limit_trades=50, include_breaks=False):
        since = self.check_and_reformat_datetime(since)
        if include_breaks:
            include_breaks = 'true'
        else:
            include_breaks = 'false'
        payload = {'timestamp': since,
                    'limit_trades': limit_trades,
                    'include_breaks': include_breaks}
        return self.send_check(payload=payload, endpoint=os.path.join('trades', str(pair)))

    def auction(self, pair):
        return self.send_check(endpoint=os.path.join('auction', str(pair)))

    def auction_history(self, pair, since=None, limit_auction_results=50, include_indicative=False):
        since = self.check_and_reformat_datetime(since)
        if include_indicative:
            include_indicative = 'true'
        else:
            include_indicative = 'false'
        payload = {'since': since,
                    'limit_auction_results': limit_auction_results,
                    'include_indicative': include_indicative}
        return self.send_check(payload=payload, endpoint=os.path.join('auction', str(pair), 'history'))


class GeminiSocket(Websocket):

    def __init__(self, symbol, on_message=None):
        self.base = config.WEBSOCKET_CONFIG['base']
        self.url = os.path.join(self.base, symbol)
        self.symbol = symbol
        self.wrap_on_message = on_message
        super(GeminiSocket, self).__init__(self.url, on_message = self.on_message_depth,
                                            on_error = self.on_error,
                                            on_open = self.on_open,
                                            on_close = self.on_close)

    def on_message_depth(self, ws, message):
        m = super(GeminiSocket, self).on_message(ws, message)
        if self.wrap_on_message is not None:
            self.wrap_on_message(ws, m)
        else:
            return self.translate_depth(m)

    def translate_depth(self, message):
        ret = []
        header = {}
        header['exchange'] = 'gemini'
        header['stream'] = 'depth_update'
        try:
            header['pair'] = self.symbol
            header['event_id'] = message['eventId']
            header['timestamp'] = self.generate_timestamp()
            data = message['data']
            events = message['events']
        except KeyError:
            print('Unexpected stream format in translate_order_book_l2:', message)
            return ret
        if action == 'update':
            for d in data:
                r = {}
                r['price_id'] = d['id']
                r['quantity'] = d['size']
                r['side'] = d['side'].lower()
                ret.append({**header, **r})
            return ret
        if action == 'insert':
            for d in data:
                r = {}
                r['price_id'] = d['id']
                r['price'] = d['price']
                r['quantity'] = d['size']
                r['side'] = d['side'].lower()
                ret.append({**header, **r})
            return ret
        if action == 'delete':
            for d in data:
                r = {}
                r['price_id'] = d['id']
                r['side'] = d['side'].lower()
                r['quantity'] = 0
                ret.append({**header, **r})
            return ret

    def on_error(self, ws, error):
        print('Error in GeminiSocket: ', error)

    def on_open(self, ws):
        print('GeminiSocket: opened')

    def on_close(self, ws):
        print('GeminiSocket: closed')







### end
