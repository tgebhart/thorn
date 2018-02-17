import time
import datetime
import threading
import json
import argparse
import sys
from threading import Thread

import asyncio
import ccxt.async as ccxt

import cassandra
from cassandra.cluster import Cluster

from thorn.api import UnifiedAPIManager
from thorn.orderbooks import UnifiedOrderBook
from thorn import config
from thorn.utils import instantiate_exchanges, create_diff_object

FUNCTION = 'fetchOrderBook'
DELAY = 1000
FULL_DB_SUFFIX = '_order_book_snapshots'
UPDATE_DB_SUFFIX = '_second_updates'

class MonitorWorker(Thread):
    def __init__(self, book, on_message, stop_at):
        Thread.__init__(self)
        self.book = book
        self.on_message = on_message
        self.stop_at = stop_at

    def run(self):
        self.book.monitor_full_book_stream(on_message=self.on_message, stop_at=self.stop_at)

def run(symbol, exchanges={}, stop_at=None):
    print('RUNNING ', symbol)

    symbolstr = symbol.replace('/','_')
    update_db_name = symbolstr + UPDATE_DB_SUFFIX
    full_db_name = symbolstr + FULL_DB_SUFFIX
    cluster = Cluster(config.CASSANDRA['nodes'])

    if not exchanges:
        exchanges = instantiate_exchanges(ccxt.exchanges)

    print('Exchanges:', list(exchanges.keys()))

    manager = UnifiedAPIManager(symbol, FUNCTION, list(exchanges.values()), delay)
    asyncio.get_event_loop().run_until_complete(manager.filter_exchanges())

    print('Filtered Exchanges:', list(map(lambda x: x.id, manager.exchanges)))

    order_books = {}
    seqs = {}
    for e in manager.exchanges:
        order_books[e.id] = UnifiedOrderBook(symbol, e)
        seqs[e.id] = 0

    base_query = "INSERT INTO {} (ts, seq, is_trade, is_bid, price, quantity, exchange) \
                VALUES (%(ts)s, %(seq)s, %(is_trade)s, %(is_bid)s, %(price)s, \
                %(quantity)s, %(exchange)s)".format(update_db_name)
    full_base_query = "INSERT INTO {} (ts, bids, asks, exchange) \
                VALUES (%(ts)s, %(bids)s, %(asks)s, %(exchange)s) \
                ".format(full_db_name)

    session = cluster.connect()
    try:
        session.set_keyspace(config.CASSANDRA['second_update_keyspace']['name'])
    except Exception as e:
        if type(e) is cassandra.InvalidRequest:
            session.execute(config.CASSANDRA['second_update_keyspace']['query'])
            session.set_keyspace(config.CASSANDRA['second_update_keyspace']['name'])

    def on_message(m):
        print('Got message: ', m)
        exchange = m['exchange']
        book = order_books[exchange]
        seq = seqs[exchange]
        seqs[exchange] += 1

        ts = m['timestamp']
        # first update in sequence, save full order book snapshot in different table
        if seq == 0:
            u = {'ts': ts, 'bids':m['bids'], 'asks': m['asks'], 'exchange': exchange}
            session.execute(full_base_query, u)

        # don't run update because last_bids not yet available
        else:
            current_bids = set((x[0], x[1]) for x in m['bids'])
            current_asks = set((x[0], x[1]) for x in m['asks'])

            last_bids = set((x[0], x[1]) for x in book.bids.inorder())
            last_asks = set((x[0], x[1]) for x in book.asks.inorder())

            removed_bids = last_bids.difference(current_bids)
            removed_asks = last_asks.difference(current_asks)

            added_bids = current_bids.difference(last_bids)
            added_asks = current_asks.difference(last_asks)

            for bid in removed_bids:
                u = create_diff_object(ts, seq, True, bid[0], 0.0, exchange)
                session.execute(base_query, u)
            for bid in added_bids:
                u = create_diff_object(ts, seq, True, bid[0], bid[1], exchange)
                session.execute(base_query, u)

            for ask in removed_asks:
                u = create_diff_object(ts, seq, False, ask[0], 0.0, exchange)
                session.execute(base_query, u)
            for ask in added_asks:
                u = create_diff_object(ts, seq, False, ask[0], ask[1], exchange)
                session.execute(base_query, u)

        book.update_full_book(m)

    threads = []
    for _id in order_books:
        # worker = MonitorWorker(order_books[_id], on_message, stop_at)
        # worker.daemon = True
        # threads.append(worker)
        order_books[_id].monitor_full_book_stream(on_message=on_message, stop_at=stop_at)
    # for thread in threads:
    #     thread.start()
    # for thread in threads:
    #     thread.join()

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
        run(symbol, exchanges=exchanges, stop_at=stop_at)
