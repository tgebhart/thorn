API_CONFIG = {
    'base': 'https://poloniex.com/public',
    'call_limit': 6,
    'per': 'second',
    'fee_structure': 'maker_taker',
    'valid_periods': [300,900,1800,7200,14400,86400]
}


WEBSOCKET_CONFIG = {
    'base': 'wss://api.poloniex.com',
    'push_freq': 1,
    'push_per': 'second',
    'disconnect_after': 24,
    'disconnect_per': 'hours',
    'valid_streams': ['ticker', 'trollbox', 'depth']
}

FEE_CONFIG = {
    'fee_structure': 'maker_taker',
    'default': '<600BTC',
    'fee_table': {
        '<600BTC' : {'maker':0.0015, 'taker':0.0025},
        '>=600BTC': {'maker':0.0014, 'taker':0.0024},
        '>=1200BTC': {'maker':0.0012, 'taker':0.0022},
        '>=2400BTC': {'maker':0.0010, 'taker':0.0020},
        '>=6000BTC': {'maker':0.0008, 'taker':0.0016},
        '>=12000BTC': {'maker':0.0005, 'taker':0.0014},
        '>=18000BTC': {'maker':0.0002, 'taker':0.0012},
        '>=24000BTC': {'maker':0.0000, 'taker':0.0010},
        '>=60000BTC': {'maker':0.0000, 'taker':0.0008},
        '>=120000BTC': {'maker':0.0000, 'taker':0.0005}
    },
    'highest':'<600BTC',
    'lowest':'>=120000BTC'
}
