import time
import datetime
import os

import requests

class PublicExchange(object):
    '''Base class for Public Exchanges.
    '''
    def __init__(self, base=None):
        self.base = base

    def get(self, payload={}, endpoint=None):
        if endpoint is not None:
            path = os.path.join(self.base, endpoint)
        else:
            path = self.base
        r = requests.get(path, params=payload)
        if r.status_code == 200:
            return r.json(), None
        else:
            print("Unexpected Status Code in request ", r.url, ':', r.status_code)
            try:
                return r.json(), r.status_code
            except Exception:
                return r, r.status_code

    def check_and_reformat_datetime(self, start, end):
        if isinstance(start, datetime.date) and isinstance(end, datetime.date):
            start = time.mktime(start.timetuple())
            end = time.mktime(end.timetuple())
            return start, end
        return None, None

    def filter_none_params(self, d):
        return {k:v for k,v in d.items() if v is not None}
