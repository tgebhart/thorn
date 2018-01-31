import json
import datetime
import asyncio

from confluent_kafka import Consumer, KafkaError

from thorn.api import config as api_config
from thorn import config as global_config
from thorn.utils import Printer
from thorn.utils import BinaryTree

class UnifiedOrderBook(BinaryTree):

    def __init__(self, symbol, exchange, params={}, loop=None):
        self.symbol = symbol
        self.exchange = exchange
        self.bids = BinaryTree()
        self.asks = BinaryTree()
        self.last_update_id = 0
        self.latest_event_time = None
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.c = Consumer(global_config.KAFKA['consumer_config'])
        self.api_stream_suffixes = api_config.API_MANAGER_CONFIG['function_stream_suffixes']
        self.socket_stream_suffixes = api_config.SOCKET_MANAGER_CONFIG['function_stream_suffixes']
        super(UnifiedOrderBook, self).__init__()

    async def get_full_book(self, params={}):
        r = await self.exchange.fetch_order_book(self.symbol, params=params)
        self.update_full_book(r)

    def update_full_book(self, m):
        bids = m['bids']
        asks = m['asks']
        self.latest_event_time = m['datetime']
        for bid in bids:
            self.bids.insert(bid[0], bid[1], replace=True)
        for ask in asks:
            self.asks.insert(ask[0], ask[1], replace=True)

    def monitor_updates(self):
        topicstr = self.symbol.replace('/', '_') + self.socket_stream_suffixes['orderBookUpdate']
        self.c.subscribe([topicstr])
        running = True
        while running:
            msg = self.c.poll()
            if not msg.error():
                m = json.loads(msg.value().decode('utf-8'))
                if 'e' in m and m['e'] == 'depthUpdate' and m['exchange'] == self.exchange.id:
                    self.update_book(m)
            elif msg.error().code() != KafkaError._PARTITION_EOF:
                print(msg.error())
                running = False
        self.c.close()

    def monitor_full_book_stream(self, stop_at=None):
        if stop_at is None:
            stop_at = datetime.datetime.utcnow() + datetime.timedelta(days=73000)
        topicstr = self.symbol.replace('/','_') + self.api_stream_suffixes['fetchOrderBook']
        self.c.subscribe([topicstr])
        running = True
        while running:
            msg = self.c.poll()
            if not msg.error():
                m = json.loads(msg.value().decode('utf-8'))
                if 'exchange' in m and m['exchange'] == self.exchange.id:
                    self.update_full_book(m)
                    self.output_terminal()
            elif msg.error().code() != KafkaError._PARTITION_EOF:
                print(msg.error())
                running = False
            if datetime.datetime.utcnow() > stop_at:
                running = False
        self.c.close()

    def update_book(self, m):
        if m['u'] <= self.last_update_id:
            return None
        bids = m['bids']
        for bid in bids:
            self.update_tree(bid[0], bid[1], self.bids)
        asks = m['asks']
        for ask in asks:
            self.update_tree(bid[0], bid[1], self.asks)
        self.last_update_id = m['u']
        self.latest_event_time = self.format_time(m['E'])

    def update_tree(self, price, quantity, tree):
        if quantity == 0:
            tree.remove(price)
        tree.insert(price, quantity)

    def format_time(self, t):
        return datetime.datetime.fromtimestamp(t / 1e3)

    def output_terminal(self):
        bo = self.bids.inorder()
        ao = self.asks.inorder()
        spacing = " "*10
        output = "Bids" + 2*spacing + "Asks" "\n" + "-"*4*len(spacing) + "\n"
        end = "\n"
        if len(bo) >= len(ao):
            lb = len(bo)
            la = len(ao)
            for i in range(lb):
                if i < la:
                    output += "[{:0.6f}, {:0.5f}]".format(bo[i][0], bo[i][1])  + spacing + "[{:0.6f}, {:0.5f}]".format(ao[i][0], ao[i][1]) + end
                else:
                    output += "[{:0.6f}, {:0.5f}]".format(bo[i][0], bo[i][1])  + spacing + " "*len(str(ao[la-1])) + end
        else:
            lb = len(bo)
            la = len(ao)
            for i in range(la):
                if i < lb:
                    output += "[{:0.6f}, {:0.5f}]".format(bo[i][0], bo[i][1]) + spacing + "[{:0.6f}, {:0.5f}]".format(ao[i][0], ao[i][1])  + end
                else:
                    output += " "*len(str(bo[lb-1])) + spacing + "[{:0.6f}, {:0.5f}]".format(ao[i][0], ao[i][1])  + end
        Printer(output)
