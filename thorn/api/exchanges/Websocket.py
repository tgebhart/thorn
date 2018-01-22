import time
import datetime
import os
import ssl
import json

import requests
import websocket

class Websocket(object):
    '''Base class for Websocket exchange data.
    '''
    def __init__(self, url, on_message=None, on_error=None, on_open=None,
                on_close=None):
        self.url = url
        if on_message is None:
            on_message = self.on_message
        if on_error is None:
            on_error = self.on_error
        if on_open is None:
            on_open = self.on_open
        if on_close is None:
            on_close = self.on_close
        self.ws = websocket.WebSocketApp(self.url,
                                        on_open=on_open,
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close)

        self.ws.run_forever()




    def on_message(self, ws, message):
        return json.loads(message)

    def on_error(self, ws, error):
        print('BASE error: ', error)

    def on_open(self, ws):
        print('BASE: opened')

    def on_close(self, ws):
        print('BASE: closed')

    def generate_timestamp(self):
        return datetime.datetime.utcnow()
