import unittest
import time
import datetime
import threading
import json

from confluent_kafka import Consumer, KafkaError

from thorn.api import SocketManager
sm = SocketManager()

class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)


class SocketManagerTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_binance(self):
        # sm.manage_binance()
        def pass_test(m):
            if 'e' in m:
                return True
            return False

        t1 = threading.Thread(target=sm.manage_binance, args=())
        t1.daemon = True
        t1.start()
        consume('binance_socket', pass_test)

    def test_bitmex(self):

        def pass_test(m):
            if 'table' in m:
                return True
            return False

        t1 = threading.Thread(target=sm.manage_bitmex, args=())
        t1.daemon = True
        t1.start()
        consume('bitmex_socket', pass_test)

    def test_gemini(self):

        def pass_test(m):
            if 'type' in m:
                return True
            return False

        t1 = threading.Thread(target=sm.manage_gemini, args=())
        t1.daemon = True
        t1.start()
        consume('gemini_socket', pass_test)

def consume(topic, pass_test):
    c = Consumer({'bootstrap.servers': '0', 'group.id': 'mygroup',
                  'default.topic.config': {'auto.offset.reset': 'smallest'}})
    c.subscribe([topic])
    running = True
    while running:
        msg = c.poll()
        if not msg.error():
            print('Received message: %s' % msg.value().decode('utf-8'))
            m = json.loads(msg.value().decode('utf-8'))
            running = not pass_test(m)
            print('test passed')
        elif msg.error().code() != KafkaError._PARTITION_EOF:
            print(msg.error())
            running = False
    c.close()






if __name__ == '__main__':
    unittest.main()
