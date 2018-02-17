import os
import asyncio
import pandas as pd
import ccxt.async as ccxt

def read_private_api_info(loc, name, index_col_name='exchange'):
    '''Helper method for reading API Keys and Secret Keys. Returns a dictionary
    of form {'exchange': {'api_key': '<>'}, {'secret key':'<>'}} as expected
    when calling `df.to_dict('index')` in Pandas given an appropriate index of
    exchange names.

    Args:
        - loc (str): The location (absolute) of the csv file to read.
        - name (str): The name of the csv file. `Ex: api_keys.csv`.
        - index_col_name (str, optional): The column name used to create an index.

    Returns: dict of form {'exchange': {'api_key': '<>'}, {'secret key':'<>'}}.
    '''
    df = pd.read_csv(os.path.join(loc,name))
    df = df.set_index(index_col_name)
    return df.to_dict('index')

def instantiate_exchanges(exchanges):
    '''Instantiates the exchanges listed in `exchanges` parameter. The parameter
    must be an iterable containing the name of the property returned by
    `exchange.id`. This function returns a dict mapping the id of the exchange
    to the instantiated exchange object.

    Args:
        - exchanges (list[str]): An iterable object whose first iterable object
            is a string representing the id of the exchange as per `exchange.id`.

    Returns: dict mapping exchange id to instantiated exchange object.
    '''
    ret = {}
    for _id in exchanges:
        exchange = getattr(ccxt, _id)
        ex = exchange()
        try:
            asyncio.get_event_loop().run_until_complete(ex.load_markets())
            ret[_id] = ex
        except Exception as e:
            print('EXCEPTION RAISED FOR {}:'.format(_id), e)
    return ret

def create_diff_object(ts, seq, is_bid, price, quantity, exchange, is_trade=False):
    '''Returns a dict-formatted update object for order book tracking.

    Args:
        - ts (int): Timestamp in ms.
        - seq (int): Sequence number of the update.
        - is_bid (bool): Whether or not the update is a bid (false if ask).
        - price (float): The price to be updated.
        - quantity (float): The updated quantity.
        - exchange (str): The exchange id from which the update originated.
        - is_trade (bool, optional): Whether or not this update represents a trade.

    Returns: dict
    '''
    return {
    'ts': ts,
    'seq': seq,
    'is_trade': is_trade,
    'is_bid': is_bid,
    'price': price,
    'quantity': quantity,
    'exchange': exchange
    }
