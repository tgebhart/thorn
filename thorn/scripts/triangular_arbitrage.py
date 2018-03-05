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
from thorn.utils import instantiate_exchanges, get_highest_trading_fee, \
                        reformat_pair
from thorn.models import ArbitrageGraph, ArbitragePair, find_opportunities
from thorn.brokers import ArbitrageBroker

GROUP_SUFFIX = '_triangular'

def create_pair_object(pair, exchange, price):
    return ArbitragePair(exchange, pair, price[0], quantity=price[1])

def run(pair, exchange, graph, broker, stop_at=None):

    def on_message(m, seq=-1, **kwargs):
        '''Function passed to UnifiedOrderBook class that will be executed each
        time the UnifiedOrderBook reads an order book message from Kafka. If the
        message is about the exchange of the instantiated order book, this
        function will compute the diff on the order book from the previous
        second's complete book. This diff is then sent to the DB for storage.

        If the message is not from the exchange of `book`, do nothing.
        '''
        ex_name = m['exchange']
        ts = m['timestamp']

        book.update_full_book(m)
        price = book.asks.min()
        p = create_pair_object(book.pair, exchange, price)
        # first read in sequence, add pair
        if seq == 0:
            graph.add_pair(p, fee=0)
        else:
            graph.update_pair(p, fee=0)
        ops = find_opportunities(graph, exchange=exchange)
        graph.update_draw()
        print(ts,':', ops)
        if len(ops) > 0:
            broker.handle_ops(ops)

    print('RUNNING ', pair)
    book = UnifiedOrderBook(pair, exchange)

    group_name = pair + '_' + exchange.id + GROUP_SUFFIX
    book.monitor_full_book_stream(group_name, on_message=on_message, stop_at=stop_at)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Triangular Arbitrage model')

    parser.add_argument('-e', '--exchange', type=str, help='exchange to aggregate from (use exchange id name)', required=True)
    parser.add_argument('-a', '--all', action='store_true', help='whether to run all pairs', required=False)
    parser.add_argument('-p', '--pairs', nargs='+', help='list of pairs to monitor', required=False)
    parser.add_argument('-sa', '--stopAfter', help='Stop managing after this number of ms', type=int, required=False)

    cores = multiprocessing.cpu_count()
    print('Number of CPU Cores: {}'.format(cores))

    args = parser.parse_args()
    exchange = instantiate_exchanges([args.exchange])[args.exchange]
    if args.all:
        print('Using as many pairs as possible')
        # TODO: Add ability to query Cassandra for which UnifiedAPIManagers are
        # dumping to Kafka.
        pairs = exchange.markets
    else:
        pairs = args.pairs
    stop_at = args.stopAfter
    if stop_at is not None:
        stop_at = datetime.datetime.utcnow() + datetime.timedelta(milliseconds=stop_at)

    graph = ArbitrageGraph()
    graph.draw()
    broker = ArbitrageBroker()
    jobs = []
    multiprocessing.log_to_stderr(logging.DEBUG)
    for p in pairs:
        p = multiprocessing.Process(name=p, target=run, args=(p, exchange, graph, broker), kwargs={'stop_at':stop_at})
        jobs.append(p)
        p.start()
    for p in jobs:
        p.join()
        print(p.name, p.exitcode)
