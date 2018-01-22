API_CONFIG = {
    'base': 'https://api.gemini.com',
    'call_limit': 1,
    'per': 'second',
    'public_version': 'v1',
    'default_pair': 'BTCUSD',
    'default_ticker': 'BTC',
    'fee_structure': 'maker_taker',
}


WEBSOCKET_CONFIG = {
    'base': 'wss://api.gemini.com/v1/marketdata',
    'push_freq': 1,
    'push_per': 'second',
    'disconnect_after': 24,
    'disconnect_per': 'hours',
}
