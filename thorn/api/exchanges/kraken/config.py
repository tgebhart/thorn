API_CONFIG = {
    'base': 'https://api.kraken.com/0/public/',
    'call_limit': 1,
    'per': 'second',
    'default_pair': 'XXBTZUSD',
    'valid_intervals' : [1, 5, 15, 30, 60, 240, 1440, 10080, 21600],
    'fee_structure': 'maker_taker',
}

FEE_CONFIG = {
    'fee_structure': 'maker_taker',
    'default': '<50000',
    'fee_table': {
    },
    'highest':'<50000',
    'lowest':'>10000000'
}
