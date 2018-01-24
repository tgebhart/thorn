import time
import datetime
import os
import json

import requests
import websocket

from confluent_kafka import Producer

from thorn.api import config
from thorn.api.exchanges import BinanceSocket
from thorn.api.exchanges import GeminiSocket
from thorn.api.exchanges import BitmexSocket

class SocketManager(object):

    def __init__(self, brokers=[]):
        self.brokers = brokers
        if len(self.brokers) < 1:
            self.brokers = config.SOCKET_MANAGER_CONFIG['brokers']
        if len(self.brokers) > 1:
            self.broker_string = ",".join(self.brokers)
        else:
            self.broker_string = self.brokers[0]

    def manage_binance(self):

        p = Producer({'bootstrap.servers': ",".join(self.broker_string)})

        def on_message(ws, message):
            # print('on_message_def', message)
            p.produce('binance_socket', json.dumps(message).encode('utf-8'))

        s = BinanceSocket('depth','bnbbtc', on_message=on_message)
        s.run_forever()
        p.flush()

    def run(self):
        self.manage_binance()
