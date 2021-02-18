import pandas as pd
import numpy as np
from .concentration import cumulative_lq

def update_cumul_df(df, loads, flow):
    cumulative_ratio = cumulative_lq(loads, flow)
    df.loc[:, 'cumul_flow_ratio'] = cumulative_ratio['flow_ratio']
    df.loc[:, 'cumul_load_ratio'] = cumulative_ratio['loads_ratio']
    return df

def load_flow_loc(start_end, load_flow, timestep='d'):
    start, end = start_end
    if timestep=='h':
        start = pd.to_datetime(start + ' 00:00:00')
        end = pd.to_datetime(end + ' 23:00:00')
        
    df = load_flow.loc[start:end, :]
    return df