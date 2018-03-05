import time
import datetime
import multiprocessing
import logging
import json
import argparse

import asyncio
import ccxt.async as ccxt

from thorn.api import UnifiedAPIManager
from thorn.orderbooks import UnifiedOrderBook
from thorn.utils import instantiate_exchanges

FUNCTION = 'fetchOrderBook'
DELAY = 1000

def run(symbol, exchanges, delay=DELAY, stop_at=None):
    print('RUNNING ', symbol)
    print('Exchanges:', exchanges)

    loop = asyncio.get_event_loop()
    exchanges = instantiate_exchanges(exchanges)
    manager = UnifiedAPIManager(symbol, FUNCTION, list(exchanges.values()), delay)
    loop.run_until_complete(manager.filter_exchanges())

    print('Filtered Exchanges:', list(map(lambda x: x.id, manager.exchanges)))

    loop.run_until_complete(manager.manage(stop_at=stop_at))
    loop.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Second-level order book change \
                                    real-time scraper.')

    parser.add_argument('-e', '--exchanges', nargs='+', help='list of exchanges to aggregate from (use exchange id name)', required=False)
    parser.add_argument('-ap', '--allPairs', action='store_true', help='whether to use all pairs from each exchange', required=False)
    parser.add_argument('-ae', '--allExchanges', action='store_true', help='whether to run all exchanges', required=False)
    parser.add_argument('-p', '--pairs', help='the pairs/tickers to monitor', nargs='+', required=False)
    parser.add_argument('-d', '--delay', help='the delay (ms) between calls', type=int, required=False, default=DELAY)
    parser.add_argument('-sa', '--stopAfter', help='Stop managing after this number of ms', type=int, required=False)

    args = parser.parse_args()

    delay = args.delay

    if args.allExchanges:
        print('Using as many ccxt-unified exchanges as possible')
        exchanges = ccxt.exchanges
    elif args.exchanges is not None:
        exchanges = args.exchanges
    else:
        raise ValueError('Please either list an exchange or set the -allExchanges flag.')

    stop_at = args.stopAfter
    if stop_at is not None:
        stop_at = datetime.datetime.utcnow() + datetime.timedelta(milliseconds=stop_at)

    pairs = []
    if args.allPairs:
        print('Using as many pairs as possible given exchanges')
        for exchange in exchanges:
            ex = instantiate_exchanges([exchange])[exchange]
            pairs.append(ex.markets)
    elif args.pairs is not None:
        pairs = args.pairs
    else:
        raise ValueError('Please either list pairs or set the -allPairs flag.')

    multiprocessing.log_to_stderr(logging.DEBUG)
    jobs = []
    for p in pairs:
        p = multiprocessing.Process(name=p, target=run, args=(p, exchanges), kwargs={'delay':delay,'stop_at':stop_at})
        jobs.append(p)
        p.start()
    for p in jobs:
        p.join()
        print(p.name, p.exitcode)
