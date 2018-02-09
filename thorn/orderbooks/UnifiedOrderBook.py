import json
import datetime
import asyncio

from confluent_kafka import Consumer, KafkaError

from thorn.api import config as api_config
from thorn import config as global_config
from thorn.utils import Printer
from thorn.utils import BinaryTree

class UnifiedOrderBook(BinaryTree):

    def __init__(self, symbol, exchange, loop=None):
        '''Initialization method for the `UnifiedOrderBook` class. The class
        tracks a symbol, exchange, bids, asks, update id, event times, an asyncio
        loop, a Kafka consumer class, and a few other helper attributes. The bids
        and asks are stored in their own binary trees. The class implements only
        the ccxt unified API functions related to order book tracking. This allows
        the class to be instantiated for any exchange that is able to call the
        unified API exchange methods.

        Args:
            - symbol (str): The symbol that the order book tracks.
            - exchange (ccxt.exchange): The instantiated exchange tied to the order book.
            - loop (asyncio.event_loop): An Asyncio event loop to be used for the Order Book.

        Returns: None.
        '''
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
        '''Method that calls for the full order book at the time using the
        unified API `fetch_order_book` method. This updates the class's order
        book.

        ASYNC

        Args:
            - params (dict, optional): Additional paramters to be sent with the fetch.

        Returns: None.
        '''
        r = await self.exchange.fetch_order_book(self.symbol, params=params)
        self.update_full_book(r)

    def update_full_book(self, m):
        '''Updates the bid and ask trees along with the most recent event time
        given an API order book message.

        Args:
            - m (dict): A json message returned from `fetch_order_book` or similar
                unified API return structure.

        Returns: None.
        '''
        bids = m['bids']
        asks = m['asks']
        self.latest_event_time = m['datetime']
        for bid in bids:
            self.bids.insert(bid[0], bid[1], replace=True)
        for ask in asks:
            self.asks.insert(ask[0], ask[1], replace=True)

    def monitor_updates(self):
        '''Deprecated method for monitoring socket streams.
        '''
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
        '''Function that monitors Kafka streams containing full order book
        information. That is, responses of the unified API method `fetch_order_book`.
        This function uses the class consumer to read a stream dictated by
        `self.api_stream_suffixes['fetchOrderBook']` and update its internal
        bid/ask structure accordingly. This method will run indefinitely unless
        `stop_at` is set.

        Args:
            - stop_at (datetime.datetime): The time at which to stop monitoring
                the full order book.

        Returns: None.
        '''
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
        '''Deprecated method for updating order books according to socket stream
        information.
        '''
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
        '''Helper method for updating a binary tree.

        Args:
            - price (float): The price to update.
            - quantity (float): The quantity at which the price will be set.
            - tree (BinaryTree): A binary tree.

        Returns: None.
        '''
        if quantity == 0:
            tree.remove(price)
        tree.insert(price, quantity)

    def format_time(self, t):
        '''Helper method to format a millisecond timestamp into a datetime object.

        Args:
            - t (int): An integer ms timestamp.

        Returns: datetime.datetime.
        '''
        return datetime.datetime.fromtimestamp(t / 1e3)

    def output_terminal(self):
        '''Outputs the order book to the terminal in an easily-readable format
        for debugging purposes. Uses the `Printer` class.
        '''
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
