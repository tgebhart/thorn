import requests
from thorn.api.exchanges import PublicExchange


class CoinbasePublic(PublicExchange):
    '''Public REST API class for Coinbase. Extends `PublicExchange`'''

    def __init__(self):
        print('coinbase public init')
