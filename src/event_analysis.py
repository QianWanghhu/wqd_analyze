#usr/bin/env python=3

import pandas as pd
import numpy as np
from utils.concentration import rainfall_events, emc_cal, conc_interpolate, event_emc
import datetime

# read the discrete storm events
# Read daily loads and flow
# Read hourly loads and flow
from common_settings import obspath, outpath, events_name, \
    obs_events, day_load_flow, hour_load_flow, conct_name, modpath, mod_load_flow

from utils.concentration import cumulative_lq, excel_save
from utils.signatures import update_cumul_df, load_flow_loc

# Read files of events, daily load and flow, hourly flow, conc.
dir_out = '../output/'
dir_data = '../data/obs/'
fn = ['obs_storm_event_common3.csv', 'low_interp_flow.csv',  '126001A_hourly.csv', 'gbr_WhiSun.xlsx']
events = pd.read_csv(f'{dir_out}{fn[0]}', index_col='ID')
daily_obs = pd.read_csv(f'{dir_data}{fn[1]}')
hour_flow = pd.read_csv(f'{dir_data}{fn[2]}')
conc = pd.read_excel(f'{dir_data}{fn[3]}', sheet_name='126001A')
daily_obs['Date'] = pd.to_datetime(daily_obs['Date'], yearfirst=True)
hour_flow['Time'] = pd.to_datetime(hour_flow['Time'])
conc['DateTime'] = pd.to_datetime(conc['DateTime'])
events['start'] = pd.to_datetime(events['start'] , yearfirst=True)
events['end'] = pd.to_datetime(events['end'] , yearfirst=True)

# Loop over events
for ii in range(1, events.shape[0]+1):
    t_start, t_end = events.loc[ii, 'start':'end']
    idx_temp = daily_obs[daily_obs['Date'] >= t_start][daily_obs['Date'] <= t_end]['Loads (kg)'].idxmax();
    events.loc[ii, ['peaktime_load', 'peak_load(kg)']] = daily_obs.loc[idx_temp, ['Date', 'Loads (kg)']].values

    idx_temp_d = daily_obs[daily_obs['Date'] >= t_start][daily_obs['Date'] <= t_end]['Flow (ML)'].idxmax();
    events.loc[ii, ['peaktime_flow_d', 'peak_flow_d(ML)']] = daily_obs.loc[idx_temp_d, ['Date', 'Flow (ML)']].values

    idx_temp = daily_obs[daily_obs['Date'] >= t_start][daily_obs['Date'] <= t_end]['Concentration (mg/L)'].idxmax();
    events.loc[ii, ['peaktime_conc', 'peak_conc(mg/L)']] = daily_obs.loc[idx_temp, ['Date', 'Concentration (mg/L)']].values

    idx_temp_h = hour_flow[hour_flow['Time'] >= t_start][hour_flow['Time'] < t_end + datetime.timedelta(days=1)]['Flow(ML)'].idxmax();
    events.loc[ii, ['peaktime_flow_h', 'peak_flow_h(ML)']] = hour_flow.loc[idx_temp_h, ['Time', 'Flow(ML)']].values

    # Summarize water quality samples that were taken during each event.
    
    wq_samples = conc[conc['DateTime'] >= t_start][conc['DateTime'] < t_end + datetime.timedelta(days=1)]
    events.loc[ii, 'num_obs_sample'] = wq_samples.shape[0]
    events.loc[ii, 'sample_bef_peak'] = wq_samples[wq_samples['DateTime'] < events.loc[ii, 'peaktime_flow_h']].shape[0]
    events.loc[ii, 'sample_aft_peak'] = wq_samples[wq_samples['DateTime'] > events.loc[ii, 'peaktime_flow_h']].shape[0]
    events.loc[ii, 'sample_on_peakday'] = wq_samples[wq_samples['DateTime'] >= events.loc[ii, 'peaktime_flow_d']][wq_samples['DateTime'] < events.loc[ii, 'peaktime_flow_d'] + datetime.timedelta(days=1)].shape[0]

events.to_csv(dir_out+'event_obs_info_new.csv')
    
