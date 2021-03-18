""" This script stores the shared settings for other .py files in the same repository."""
import pandas as pd 
from utils.concentration import rainfall_events

# read the discrete storm events
obspath = '../data/obs/'
modpath = '../data/mod/'
outpath = '../output/'
events_name = 'obs_storm_event_common.csv'
obs_events = rainfall_events(outpath + events_name)

# Read daily loads and flow
day_load_flow = pd.read_csv(obspath+'low_interp_flow.csv', index_col='Date')
day_load_flow.index = pd.to_datetime(day_load_flow.index)

# Read hourly loads and flow
fn_conct = 'cq-NO3'
conct_name = fn_conct.split('-')[1]
hour_load_flow = pd.read_csv(f'{obspath}high_{conct_name}_flow.csv', index_col = 'Time')
hour_load_flow.index = pd.to_datetime(hour_load_flow.index)

# Read modeling loads and flow
mod_fl_fn = 'DIN_flow.csv'
mod_load_flow = pd.read_csv(modpath + mod_fl_fn, index_col='Date')
mod_load_flow.index = pd.to_datetime(mod_load_flow.index, dayfirst=False)