import time
import datetime

import requests

from thorn.api.exchanges import PublicExchange
from thorn.api.exchanges.poloniex import config

class PoloniexPublic(PublicExchange):
    '''Public API class for Poloniex. Extends `PublicExchange`'''

    def __init__(self):
        base = config.API_CONFIG['base']
        super(PoloniexPublic, self).__init__(base=base)

    def send_check(self,payload={}):
        r = self.get(payload=payload)
        if 'error' in r:
            print('Error in return_ticker: ', r)
            return None
        return r

    def return_ticker(self):
        payload = {'command': 'returnTicker'}
        return self.send_check(payload=payload)

    def return_24_volume(self):
        payload = {'command': 'return24hVolume'}
        return self.send_check(payload=payload)

    def return_order_book(self, pair='BTC_NXT', all_orders=False, depth=10):
        if all_orders:
            payload = {'command': 'returnOrderBook',
                        'currencyPair':'all',
                        'depth': depth}
            return self.send_check(payload=payload)
        elif pair is not None:
            payload = {'command': 'returnOrderBook',
                        'currencyPair':pair,
                        'depth': depth}
            return self.send_check(payload=payload)
        else:
            print('Invalid parameters in return_order_book')

    def return_trade_history(self, start, end, pair='BTC_NXT'):
        start, end = self.check_and_reformat_datetime(start, end)
        if isinstance(start, float) and isinstance(end, float):
            payload = {'command': 'returnTradeHistory',
                        'start': start,
                        'end': end,
                        'currencyPair': pair}
            return self.send_check(payload=payload)
        else:
            raise TypeError('Invalid date structure in return_trade_history')
            return None

    def return_chart_data(self, start, end, period=14400, pair='BTC_NXT'):
        start, end = self.check_and_reformat_datetime(start, end)
        if period not in config.API_CONFIG['valid_periods']:
            raise Exception('Invalid period choice for API')
            return None
        else:
            if isinstance(start, float) and isinstance(end, float):
                payload = {'command': 'returnTradeHistory',
                            'start': start,
                            'end': end,
                            'period': period,
                            'currencyPair': pair}
                return self.send_check(payload=payload)
            else:
                raise TypeError('Invalid date structure in return_trade_history')
                return None

    def return_currencies(self):
        payload={'command': 'returnCurrencies'}
        return self.send_check(payload=payload)

    def return_loan_orders(self, currency='BTC'):
        payload = {'command': 'returnLoanOrders',
                    'currency': currency}
        return self.send_check(payload=payload)
