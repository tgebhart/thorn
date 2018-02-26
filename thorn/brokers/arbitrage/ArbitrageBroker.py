import json
import datetime
import asyncio

import ccxt.async as ccxt

from thorn.brokers import UnifiedBroker

class ArbitrageBroker(UnifiedBroker):

    def __init__(self):
        print('arb broker')
