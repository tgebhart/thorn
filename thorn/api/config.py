SOCKET_MANAGER_CONFIG = {
    'brokers' : ['0'],
    'function_stream_suffixes': {
        'orderBookUpdate': '_order_book_update'
    },
    'binance_stream_name': 'binance_socket',
    'gemini_stream_name': 'gemini_socket',
    'bitmex_stream_name': 'bitmex_socket'
}

API_MANAGER_CONFIG = {
    'brokers': ['0'],
    'function_stream_suffixes': {
        'fetchOrderBook': '_order_book',
        'fetchTicker': '_ticker'
    }
}

KEY_CONFIG = {
    'api_key_location': '~',
    'api_key_name': 'api_keys.csv',
}
