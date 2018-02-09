import os
import pandas as pd

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
