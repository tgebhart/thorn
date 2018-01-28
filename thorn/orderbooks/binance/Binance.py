import json

from confluent_kafka import Consumer, KafkaError

from thorn.orderbooks import OrderBook
from thorn.api import BinancePublic
from thorn.api import config as socket_config
from thorn import config as global_config

class BinanceBook(OrderBook):

    def __init__(self, pair):
        self.pair = pair
        self.api = BinancePublic()
        self.bids = self
        self.ask = self
        self.last_update_id = 0
        self.latest_event_time = None
        super(BinanceBook, self).__init__()

    def get_full_book(self, pair, limit=1000):
        r = self.api.depth(pair, limit=limit)
        self.last_update_id = r['lastUpdateId']
        bids = r['bids']
        asks = r['asks']
        for bid in bids:
            self.bids.insert(bid[0], bid[1])
        for ask in asks:
            self.asks.insert(ask[0], ask[1])

    def monitor_updates(self):
        c = Consumer(global_config.KAFKA['consumer_config'])
        c.subscribe([socket_config.SOCKET_MANAGER_CONFIG['binance_stream_name']])
        running = True
        while running:
            msg = c.poll()
            if not msg.error():
                m = json.loads(msg.value().decode('utf-8'))
                if 'e' in m and m['e'] == 'depthUpdate':
                    self.update_book(m)
            elif msg.error().code() != KafkaError._PARTITION_EOF:
                print(msg.error())
                running = False
        c.close()

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
