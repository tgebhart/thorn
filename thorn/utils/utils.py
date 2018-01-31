import os
import pandas as pd

def read_private_api_info(loc, name, index_col_name='exchange'):
    df = pd.read_csv(os.path.join(loc,name))
    df = df.set_index(index_col_name)
    return df.to_dict('index')
