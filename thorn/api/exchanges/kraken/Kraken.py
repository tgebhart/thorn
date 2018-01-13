import requests
from thorn.api.exchanges import PublicExchange


class KrakenPublic(PublicExchange):
    '''Public API class for Kraken. Extends `PublicExchange`'''

    def __init__(self):
        print('kraken public init')
