import time
import datetime
import os

import requests

from thorn.api.exchanges import PublicExchange
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









### end
