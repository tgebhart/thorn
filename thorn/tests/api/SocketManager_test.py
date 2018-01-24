import unittest
import time
import datetime
import threading
import json

from confluent_kafka import Consumer, KafkaError

from thorn.api import SocketManager
sm = SocketManager()

class sThread(threading.Thread):
   def __init__(self, threadID, name, counter, fun):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
      self.fun = fun

   def run(self):
      print("Starting " + self.name)
      self.fun()
      print("Exiting " + self.name)

def print_time(threadName, counter, delay):
   while counter:
      if 0:
         threadName.exit()
      time.sleep(delay)
      print("%s: %s" % (threadName, time.ctime(time.time())))
      counter -= 1


class SocketManagerTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_binance(self):
        # sm.manage_binance()
        thread1 = sThread(1, "Thread1", 1, sm.manage_binance)
        thread2 = sThread(2, "Thread2", 2, consume('binance_socket'))

def consume(topic):
    c = Consumer({'bootstrap.servers': '0', 'group.id': 'mygroup',
                  'default.topic.config': {'auto.offset.reset': 'smallest'}})
    c.subscribe([topic])
    running = True
    while running:
        msg = c.poll()
        if not msg.error():
            print('Received message: %s' % msg.value().decode('utf-8'))
            print('before mfj')
            mfj = json.loads(msg.value().decode('utf-8'))
            print(mfj)
            if 'e' in mfj:
                print('test passed')
                running = False
        elif msg.error().code() != KafkaError._PARTITION_EOF:
            print(msg.error())
            running = False
    c.close()






if __name__ == '__main__':
    unittest.main()
