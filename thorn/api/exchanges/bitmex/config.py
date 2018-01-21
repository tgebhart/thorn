API_CONFIG = {
    'base': 'https://www.bitmex.com/api/',
    'call_limit': 5,
    'per': 'second',
    'public_version': 'v1',
    'default_ticker': '.XBT',
    'valid_bins': ['1m','5m','1h','1d'],
    'fee_structure': 'fixed',
}


WEBSOCKET_CONFIG = {
    'base': 'wss://www.bitmex.com/realtime',
    'push_freq': 1,
    'push_per': 'second',
    'disconnect_after': 24,
    'disconnect_per': 'hours',
    'valid_streams': ["announcement", # Site announcements
                    "chat",        # Trollbox chat
                    "connected",   # Statistics of connected users/bots
                    "instrument",  # Instrument updates including turnover and bid/ask
                    "insurance",   # Daily Insurance Fund updates
                    "liquidation", # Liquidation orders as they're entered into the book
                    "orderBookL2", # Full level 2 orderBook
                    "orderBook10", # Top 10 levels using traditional full book push
                    "publicNotifications", # System-wide notifications (used for short-lived messages)
                    "quote",       # Top level of the book
                    "quoteBin1m",  # 1-minute quote bins
                    "settlement",  # Settlements
                    "trade",       # Live trades
                    "tradeBin1m"  # 1-minute ticker bins
                    "affiliate",   # Affiliate status, such as total referred users & payout %
                    "execution",   # Individual executions; can be multiple per order
                    "order",       # Live updates on your orders
                    "margin",      # Updates on your current account balance and margin requirements
                    "position",    # Updates on your positions
                    "privateNotifications", # Individual notifications - currently not used
                    "transact",     # Deposit/Withdrawal updates
                    "wallet"       # Bitcoin address balance data, including total deposits & withdrawals
                    ],
}
