import time
import datetime

import requests

class PublicExchange(object):
    '''Base class for Public Exchanges.
    '''
    def __init__(self, base=None):
        self.base = base

    def get(self, payload={}):
        r = requests.get(self.base, params=payload)
        if r.status_code == 200:
            return r.json()
        else:
            print("Unexpected Status Code in request ", r.url)
            return None

    def check_and_reformat_datetime(self, start, end):
        if isinstance(start, datetime.date) and isinstance(end, datetime.date):
            start = time.mktime(start.timetuple())
            end = time.mktime(end.timetuple())
            return start, end
        return None, None
