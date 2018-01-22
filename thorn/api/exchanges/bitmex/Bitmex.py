import time
import datetime
import os
import json

import requests
import websocket

from thorn.api.exchanges import PublicExchange
from thorn.api.exchanges import Websocket
from thorn.api.exchanges.bitmex import config

class BitmexPublic(PublicExchange):
    '''Public API class for Bitmex. Extends `PublicExchange`'''

    def __init__(self):
        base = config.API_CONFIG['base']
        version = config.API_CONFIG['public_version']
        url = os.path.join(base,version)
        self.default_ticker = config.API_CONFIG['default_ticker']
        self.valid_bins = config.API_CONFIG['valid_bins']
        super(BitmexPublic, self).__init__(base=url)

    def send_check(self,payload={}, endpoint=None):
        r, status = self.get(payload=self.filter_none_params(payload), endpoint=endpoint)
        if 'error' in r:
            print('Error in send_check: ', r['error']['message'])
            return None
        return r

    def check_and_reformat_datetime(self, start, end):
        if isinstance(start, datetime.datetime) and isinstance(end, datetime.datetime):
            return start, end
        else:
            return None, None

    def instrument(self, ticker=None, filt=None, columns=None, count=100,
                    start=None, reverse=False, start_time=None, end_time=None):
        start_time, end_time = self.check_and_reformat_datetime(start_time, end_time)
        payload = {'symbol':ticker,
                    'filter': filt,
                    'columns': columns,
                    'count': count,
                    'start': start,
                    'reverse': reverse,
                    'start_time': start_time,
                    'end_time': end_time}

        return self.send_check(payload=payload, endpoint='instrument')

    def instrument_active(self, ticker=None, filt=None, columns=None, count=100,
                    start=None, reverse=False, start_time=None, end_time=None):
        start_time, end_time = self.check_and_reformat_datetime(start_time, end_time)
        payload = {'symbol':ticker,
                    'filter': filt,
                    'columns': columns,
                    'count': count,
                    'start': start,
                    'reverse': reverse,
                    'start_time': start_time,
                    'end_time': end_time}

        return self.send_check(payload=payload, endpoint='instrument/active')

    def instrument_active_and_indices(self, ticker=None, filt=None, columns=None, count=100,
                    start=None, reverse=False, start_time=None, end_time=None):
        start_time, end_time = self.check_and_reformat_datetime(start_time, end_time)
        payload = {'symbol':ticker,
                    'filter': filt,
                    'columns': columns,
                    'count': count,
                    'start': start,
                    'reverse': reverse,
                    'start_time': start_time,
                    'end_time': end_time}
        return self.send_check(payload=payload, endpoint='instrument/activeAndIndices')

    def instrument_active_intervals(self, ticker=None, filt=None, columns=None, count=100,
                    start=None, reverse=False, start_time=None, end_time=None):
        start_time, end_time = self.check_and_reformat_datetime(start_time, end_time)
        payload = {'symbol':ticker,
                    'filter': filt,
                    'columns': columns,
                    'count': count,
                    'start': start,
                    'reverse': reverse,
                    'start_time': start_time,
                    'end_time': end_time}

        return self.send_check(payload=payload, endpoint='instrument/activeIntervals')

    def instrument_composite_index(self, ticker, account=None, filt=None,
                                columns=None, count=100, start=None, reverse=False,
                                start_time=None, end_time=None):
        start_time, end_time = self.check_and_reformat_datetime(start_time, end_time)
        payload = {'symbol':ticker,
                    'account': account,
                    'filter': filt,
                    'columns': columns,
                    'count': count,
                    'start': start,
                    'reverse': reverse,
                    'start_time': start_time,
                    'end_time': end_time}

        return self.send_check(payload=payload, endpoint='instrument/compositeIndex')


    def instrument_indices(self, ticker=None, filt=None, columns=None, count=100,
                    start=None, reverse=False, start_time=None, end_time=None):
        start_time, end_time = self.check_and_reformat_datetime(start_time, end_time)
        payload = {'symbol':ticker,
                    'filter': filt,
                    'columns': columns,
                    'count': count,
                    'start': start,
                    'reverse': reverse,
                    'start_time': start_time,
                    'end_time': end_time}

        return self.send_check(payload=payload, endpoint='instrument/indices')


    def insurance(self, ticker=None, filt=None, columns=None, count=100,
                start=None, reverse=False, start_time=None, end_time=None):
        start_time, end_time = self.check_and_reformat_datetime(start_time, end_time)
        payload = {'symbol':ticker,
                    'filter': filt,
                    'columns': columns,
                    'count': count,
                    'start': start,
                    'reverse': reverse,
                    'start_time': start_time,
                    'end_time': end_time}

        return self.send_check(payload=payload, endpoint='insurance')

    def liquidation(self, ticker=None, filt=None, columns=None, count=100,
                start=None, reverse=False, start_time=None, end_time=None):
        start_time, end_time = self.check_and_reformat_datetime(start_time, end_time)
        payload = {'symbol':ticker,
                    'filter': filt,
                    'columns': columns,
                    'count': count,
                    'start': start,
                    'reverse': reverse,
                    'start_time': start_time,
                    'end_time': end_time}

        return self.send_check(payload=payload, endpoint='liquidation')


    def order_book(self, ticker, depth=25):
        payload = {'symbol': ticker,
                    'depth': depth}
        return self.send_check(payload=payload, endpoint='orderBook/L2')

    def quote(self, ticker=None, filt=None, columns=None, count=100,
                start=None, reverse=False, start_time=None, end_time=None):
        start_time, end_time = self.check_and_reformat_datetime(start_time, end_time)
        payload = {'symbol':ticker,
                    'filter': filt,
                    'columns': columns,
                    'count': count,
                    'start': start,
                    'reverse': reverse,
                    'start_time': start_time,
                    'end_time': end_time}

        return self.send_check(payload=payload, endpoint='quote')

    def quote_bucketed(self, bin_size='1m', partial=False, ticker=None, filt=None, columns=None, count=100,
                start=None, reverse=False, start_time=None, end_time=None):
        if bin_size not in self.valid_bins:
            raise AttributeError('bin_size {} is not an acceptable size'.format(bin_size))
        start_time, end_time = self.check_and_reformat_datetime(start_time, end_time)
        payload = {'binSize': bin_size,
                    'partial': partial,
                    'symbol':ticker,
                    'filter': filt,
                    'columns': columns,
                    'count': count,
                    'start': start,
                    'reverse': reverse,
                    'start_time': start_time,
                    'end_time': end_time}

        return self.send_check(payload=payload, endpoint='quote/bucketed')


    def settlement(self, ticker=None, filt=None, columns=None, count=100,
                start=None, reverse=False, start_time=None, end_time=None):
        start_time, end_time = self.check_and_reformat_datetime(start_time, end_time)
        payload = {'symbol':ticker,
                    'filter': filt,
                    'columns': columns,
                    'count': count,
                    'start': start,
                    'reverse': reverse,
                    'start_time': start_time,
                    'end_time': end_time}

        return self.send_check(payload=payload, endpoint='settlement')

    def stats(self):
        return self.send_check(endpoint='stats')

    def stats_history(self):
        return self.send_check(endpoint='stats/history')

    def stats_history_usd(self):
        return self.send_check(endpoint='stats/historyUSD')

    def trade(self, ticker=None, filt=None, columns=None, count=100,
                start=None, reverse=False, start_time=None, end_time=None):
        start_time, end_time = self.check_and_reformat_datetime(start_time, end_time)
        payload = {'symbol':ticker,
                    'filter': filt,
                    'columns': columns,
                    'count': count,
                    'start': start,
                    'reverse': reverse,
                    'start_time': start_time,
                    'end_time': end_time}

        return self.send_check(payload=payload, endpoint='trade')

    def trade_bucketed(self, bin_size='1m', partial=False, ticker=None, filt=None, columns=None, count=100,
                start=None, reverse=False, start_time=None, end_time=None):
        if bin_size not in self.valid_bins:
            raise AttributeError('bin_size {} is not an acceptable size'.format(bin_size))
        start_time, end_time = self.check_and_reformat_datetime(start_time, end_time)
        payload = {'binSize': bin_size,
                    'partial': partial,
                    'symbol':ticker,
                    'filter': filt,
                    'columns': columns,
                    'count': count,
                    'start': start,
                    'reverse': reverse,
                    'start_time': start_time,
                    'end_time': end_time}

        return self.send_check(payload=payload, endpoint='trade/bucketed')


class BitmexSocket(Websocket):

    def __init__(self, stream, symbol, on_message=None):
        self.valid_streams = config.WEBSOCKET_CONFIG['valid_streams']
        if stream not in self.valid_streams:
            raise AttributeError('stream {} not a valid stream'.format(stream))
        self.base = config.WEBSOCKET_CONFIG['base']
        self.symbol = symbol
        self.args = str(stream) + ':' + str(symbol)
        # self.url = self.base + '?subscribe=' + args
        self.url = self.base
        self.wrap_on_message = on_message
        om = self.choose_stream_function(stream)
        super(BitmexSocket, self).__init__(self.url, on_message = om,
                                            on_error = self.on_error,
                                            on_open = self.on_open,
                                            on_close = self.on_close)

    def on_message_order_book_l2(self, ws, message):
        m = super(BitmexSocket, self).on_message(ws, message)
        if self.wrap_on_message is not None:
            self.wrap_on_message(ws, self.translate_order_book_l2(m))
        else:
            return self.translate_order_book_l2(m)

    def choose_stream_function(self, stream):
        if stream == 'orderBookL2':
            return self.on_message_order_book_l2

    def translate_order_book_l2(self, message):
        ret = []
        header = {}
        header['exchange'] = 'bitmex'
        header['stream'] = 'depth_update'
        try:
            header['pair'] = self.symbol
            header['timestamp'] = self.generate_timestamp()
            data = message['data']
            action = message['action']
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
        print('Error in BitmexSocket: ', error)

    def on_open(self, ws):
        payload = {'op': 'subscribe', 'args': [self.args]}
        ws.send(json.dumps(payload))
        print('BitmexSocket: opened')

    def on_close(self, ws):
        print('BitmexSocket: closed')






































### end
