import json
import datetime
import asyncio

import ccxt.async as ccxt

from thorn.brokers import UnifiedBroker
from thorn.models import ArbitrageOp

class ArbitrageBroker(UnifiedBroker):
    '''

    Args:
        expire_time (int, optional): The duration (ms) after which opportunities
            are purged from the opportunity queue.
    '''

    def __init__(self, expire_time=20000):
        self.op_queue = []
        self.expire_time = expire_time
        super(ArbitrageBroker, self).__init__()

    def add_op(self, op):
        op.timestamp = datetime.datetime.utcnow()
        self.op_queue.append(op)

    def handle_ops(self, ops):
        '''Expects ops in form:
        [
        {
            'path': [
                    {
                    'from':'xyz',
                    'to':'abc'
                    'price':123
                    },
                    ...
                    ]
            'exchange':ccxt.gemini()
        },
        ...
        ]
        '''
        for op in ops:
            if op in self.op_queue:
                # try a gain update
                try:
                    idx = self.op_queue.index(op)
                    op.timestamp = datetime.datetime.utcnow()
                    self.op_queue[idx] = op # update gain
                except ValueError:
                    pass
                    # opportunity not in list
            if op not in self.op_queue:
                self.add_op(op)

        self.sort_op_queue()


    def sort_op_queue(self):
        self.op_queue = sorted(self.op_queue, key=lambda x: (-x.gain, len(x)))

    def purge_ops(self):
        t = datetime.datetime.utcnow()
        td = datetime.timedelta(ms=self.expire_time)
        oq = list(self.op_queue)
        self.op_queue = [o for o in oq if (t > o.timestamp + td)]
