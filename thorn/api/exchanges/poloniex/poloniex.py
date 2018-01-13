import requests
from thorn.api.exchanges import PublicExchange
from thorn.api.exchanges.poloniex import config


class PoloniexPublic(PublicExchange):
    '''Public API class for Poloniex. Extends `PublicExchange`'''

    def __init__(self):
        self.base = config.API_CONFIG['base']

    def return_ticker(self):
        payload = {'command': 'returnTicker'}
        r = requests.get(self.base, params=payload)
        return r.json()
