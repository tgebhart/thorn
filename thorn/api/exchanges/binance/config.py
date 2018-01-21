API_CONFIG = {
    'base': 'https://api.binance.com/api',
    'call_limit': 1200,
    'per': 'minute',
    'public_version': 'v1',
    'valid_limits': [5, 10, 20, 50, 100, 500, 1000],
    'default_pair': 'ETHBTC',
    'fee_structure': 'fixed',
}

WEBSOCKET_CONFIG = {
    'base': 'wss://stream.binance.com:9443/ws',
    'push_freq': 1,
    'push_per': 'second',
    'disconnect_after': 24,
    'disconnect_per': 'hours',
    'valid_streams': ['aggTrade', 'trade', 'kline', 'ticker', 'arr', 'depth']
}
