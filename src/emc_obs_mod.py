import pandas as pd
import numpy as np
from utils.concentration import rainfall_events, emc_cal, conc_interpolate, event_emc
from common_settings import obspath, outpath, events_name, \
    obs_events, day_load_flow, hour_load_flow, conct_name
"""
This script is used to caclulate the Event Mean Concentration (EMC).
The inputs are .csv files containing concentration and flow after linear interpolation.
"""
# read the discrete storm events
# Read daily loads and flow
# Read hourly loads and flow
cols = [col for col in day_load_flow.columns if ('Load' in col) or ('Flow(ML)' in col)]
index_range = [1, 60]
obs_events = event_emc(obs_events, day_load_flow, index_range, cols[0], cols[1], 
    time_scale='d', multiplier=1e3)

# Calculate EMC for high-frequency data
cols = [col for col in hour_load_flow.columns if ('Load' in col) or ('ML' in col)]
index_range = [60, obs_events.shape[0]+1]
loads_col = cols[1]; flow_col = cols[0]
obs_events = event_emc(obs_events, hour_load_flow, index_range, loads_col, flow_col, 
    time_scale='h', multiplier=1)
obs_events.to_csv(outpath + events_name, index='ID')

# read the discrete storm events
modpath = '../data/mod/'
filename = 'storm_event.csv'
events = rainfall_events(f'{modpath}{filename}')

# Calculate EMC for modeling data
mod_fl_fn = 'DIN_flow.csv'
load_flow = pd.read_csv(modpath + mod_fl_fn, index_col='Date')
load_flow.index = pd.to_datetime(load_flow.index)
cols = [col for col in load_flow.columns if ('Load' in col) or ('ML' in col)]
index_range = [1, events.shape[0]]
loads_col = cols[0]; flow_col = cols[1]

events = event_emc(events, load_flow, index_range, loads_col, flow_col, 
    time_scale='d', multiplier=1)
events.dropna(axis=0, inplace=True)
events.to_csv(f'{outpath}DIN_{filename}', index='ID')