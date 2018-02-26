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

def get_highest_trading_fee(exchange, maker=False, taker=False, tier=None):
    '''Computes the highest probable trading fee for an exchange. Optional
    arguments provide better accuracy.

    Args:
        exchange (ccxt.exchange): The exchange from which fees are to be computed.
        maker (bool, optional): If we know we will be making a new spot on the
            market, set to true.
        taker (bool, optional): If we know we will be taking a bid or ask already
            on the market, set to true.
        tier (int, optional): The tier that our quantity will fall under.

    Returns:
        float: The estimated fee.
    '''
    if 'fees' in exchange.has:
        all_fees = exchange['fees']
        if 'trading' in all_fees:
            fees = all_fees['trading']
            if maker:
                if tier is not None and isinstance(tier, int):
                    if 'tierBased' in fees and fees['tierBased']:
                        return fees['tiers']['maker'][tier]
            else:
                return fees['maker']

            if taker:
                if tier is not None and isinstance(tier, int):
                    if 'tierBased' in fees and fees['tierBased']:
                        return fees['tiers']['taker'][tier]
            else:
                return fees['taker']

            if 'taker' in fees:
                return fees['taker']

    return 0.001

def reformat_pair(pair):
    '''Reformats a pair of form "Curr1/Curr2" into a Kafka-acceptable form of
    "Curr1_Curr2" where Curr1 is the base and Curr2 is the quote currency.

    Args:
        pair (str): The pair to reformat (expected "Base/Quote").

    Returns:
        str: The reformatted pair
    '''
    return symbol.replace('/','_')
