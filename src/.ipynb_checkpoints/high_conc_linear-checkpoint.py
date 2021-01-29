"""
This script is used to process the discharge-concentration data.
"""
# import packages
import numpy as np
import pandas as pd
import os
import datetime
# define the repository path
import matplotlib.pyplot as plt
import seaborn as sns

from common_settings import obspath, outpath
from utils.concentration import prep_cq, conc_interpolate, \
    hourly_cq, high_cq_linear, rainfall_events, emc_cal, event_emc

# Read discharge (Q) and the concentration (C) data
# Read discharge data
flow_name = obspath + '126001A_hourly.csv'
childpath = obspath+'high-freq/'
hourly_cq(flow_name, childpath, outpath)

# Conduct linear interpolation to high-frequency data
fn_conct = 'cq-NO3'
conct_name = fn_conct.split('-')[1]
conc_file = outpath + fn_conct +'.csv'
flow_file = obspath+'126001A_hourly.csv'

load_flow = high_cq_linear(conc_file, flow_file)
load_flow.to_csv(f'{outpath}high_{conct_name}_flow.csv')

