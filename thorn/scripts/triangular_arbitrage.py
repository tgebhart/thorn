import time
import datetime
import json
import argparse
import sys
import multiprocessing
import logging

import asyncio
import ccxt.async as ccxt

from thorn.api import UnifiedAPIManager
from thorn.orderbooks import UnifiedOrderBook
from thorn import config
from thorn.utils import instantiate_exchanges, get_highest_trading_fee, reformat_pair
from thorn.models import ArbitrageGraph

GROUP_SUFFIX = '_triangular'

def create_pair_object(pair, exchange, price):
    return {'exchange':exchange, 'pair':pair, 'price':price}

def run(pair, exchange, graph, broker, stop_at=None):
    print('RUNNING ', pair)

    book = UnifiedOrderBook(pair, exchange)

    def on_message(m, **kwargs):
        '''Function passed to UnifiedOrderBook class that will be executed each
        time the UnifiedOrderBook reads an order book message from Kafka. If the
        message is about the exchange of the instantiated order book, this
        function will compute the diff on the order book from the previous
        second's complete book. This diff is then sent to the DB for storage.

        If the message is not from the exchange of `book`, do nothing.
        '''
        print('Got message: ', m)
        ex_name = m['exchange']

        ts = m['timestamp']

        book.update_full_book(m)
        price = book.asks.min()
        p = create_pair_object(book.pair, exchange, price)
        # first read in sequence, add pair
        if seq == 0:
            graph.add_pair(p)
        else:
            graph.update_pair(p)
        ops = graph.find_opportunities()
        if len(ops) > 0:
            broker.handle_ops(ops)

    group_name = pair + '_' + exchange.id + GROUP_SUFFIX
    book.monitor_full_book_stream(group_name, on_message=on_message, stop_at=stop_at)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Triangular Arbitrage model')

    parser.add_argument('-e', '--exchange', nargs='+', help='exchange to aggregate from (use exchange id name)', required=True)
    parser.add_argument('-a', '--all', action='store_true', help='whether to run all pairs', required=False)
    parser.add_argument('-e', '--pairs', nargs='+', help='list of pairs to monitor', required=False)
    parser.add_argument('-sa', '--stopAfter', help='Stop managing after this number of ms', type=int, required=False)

    cores = multiprocessing.cpu_count()
    print('Number of CPU Cores: {}'.format(cores))

    args = parser.parse_args()
    exchange = instantiate_exchanges([args.exchange])
    asyncio.get_event_loop().run_until_complete(exchange.load_markets())
    if args.all:
        print('Using as many pairs as possible')
        # TODO: Add ability to query Cassandra for which UnifiedAPIManagers are
        # dumping to Kafka.
        pairs = exchange.markets
    else:
        symbols = args.pairs
    else:
        print('List of exchanges not specified, using as many ccxt-unified exchanges as possible')
    stop_at = args.stopAfter
    if stop_at is not None:
        stop_at = datetime.datetime.utcnow() + datetime.timedelta(milliseconds=stop_at)

    graph = ArbitrageGraph()
    jobs = []
    multiprocessing.log_to_stderr(logging.DEBUG)
    for p in pairs:
        p = multiprocessing.Process(name=p, target=run, args=(p, exchange, graph), kwargs={'stop_at':stop_at})
        jobs.append(p)
        p.start()
    for p in jobs:
        p.join()
        print(p.name, p.exitcode)
