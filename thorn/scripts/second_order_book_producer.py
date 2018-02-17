import time
import datetime
import threading
import json
import argparse

import asyncio
import ccxt.async as ccxt

from thorn.api import UnifiedAPIManager
from thorn.orderbooks import UnifiedOrderBook
from thorn.utils import instantiate_exchanges

FUNCTION = 'fetchOrderBook'
DELAY = 1000

def run(symbol, exchanges={}, delay=DELAY, stop_at=None):
    print('RUNNING ', symbol)

    if not exchanges:
        exchanges = instantiate_exchanges(ccxt.exchanges)

    print('Exchanges:', list(exchanges.keys()))

    manager = UnifiedAPIManager(symbol, FUNCTION, list(exchanges.values()), delay)
    asyncio.get_event_loop().run_until_complete(manager.filter_exchanges())

    print('Filtered Exchanges:', list(map(lambda x: x.id, manager.exchanges)))

    asyncio.get_event_loop().run_until_complete(manager.manage(stop_at=stop_at))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Second-level order book change \
                                    real-time scraper.')

    parser.add_argument('-e', '--exchanges', nargs='+', help='list of exchanges to aggregate from (use exchange id name)', required=False)
    parser.add_argument('-a', '--all', action='store_true', help='whether to run all exchanges', required=False)
    parser.add_argument('-s', '--symbol', help='the symbol/ticker to monitor', required=True, type=str)
    parser.add_argument('-d', '--delay', help='the delay (ms) between calls', type=int, required=False, default=DELAY)
    parser.add_argument('-sa', '--stopAfter', help='Stop managing after this number of ms', type=int, required=False)

    args = parser.parse_args()

    exchanges = {}
    delay = DELAY

    if args.all:
        print('Using as many ccxt-unified exchanges as possible')
        exchanges = instantiate_exchanges(ccxt.exchanges)
    elif args.exchanges is not None:
        exchanges = instantiate_exchanges(args.exchanges)
    else:
        print('List of exchanges not specified, using as many ccxt-unified exchanges as possible')
    stop_at = args.stopAfter
    if stop_at is not None:
        stop_at = datetime.datetime.utcnow() + datetime.timedelta(milliseconds=stop_at)
    symbol = args.symbol
    if '/' in symbol:
        run(symbol, exchanges=exchanges, delay=args.delay, stop_at=stop_at)
