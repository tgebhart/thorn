import time
import datetime
import threading
import json
import argparse

import asyncio
import ccxt.async as ccxt

from thorn.api import UnifiedAPIManager
from thorn.orderbooks import UnifiedOrderBook



def run(symbol):
    print('RUNNING ', symbol)

    exchanges = {}  # a placeholder for your instances

    for _id in ccxt.exchanges:
        exchange = getattr(ccxt, _id)
        ex = exchange()
        try:
            asyncio.get_event_loop().run_until_complete(ex.load_markets())
            exchanges[_id] = ex
        except Exception:
            print('EXCEPTION RAISED FOR {}'.format(_id))

    






if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Second-level order book change \
                                    real-time scraper.')

    parser.add_argument('-e', '--exchanges', nargs='+', help='list of exchanges to aggregate from (use exchange id name)', required=False)
    parser.add_argument('-a', '--all', action='store_true', help='whether to run all exchanges', required=False)
    parser.add_argument('-s', '--symbol', help='the symbol/ticker to monitor', required=True, type=str)

    args = parser.parse_args()

    if args.all:
        print('Using as many ccxt-unified exchanges as possible')
    elif args.exchanges is not None:
        print('EXCHANGES: ', args.exchanges)
    else:
        print('List of exchanges not specified, using as many ccxt-unified exchanges as possible')

    symbol = args.symbol
    if '/' in symbol:
        run(symbol)
