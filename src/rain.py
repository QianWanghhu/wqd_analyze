
"""
This script is used to process the discharge-concentration data.
"""
# import packages
import numpy as np
import pandas as pd
import os
import datetime
# define the repository path
from common_settings import fpath
import matplotlib.pyplot as plt
import seaborn as sns

# Refer to rainfall data to split the data into different time periods: washoff, dilution and recession
# read rainfall data
filepath = '../../../model_ies/rainfall_sandy_creek/'; filename = 'rainfall_sandy_creek.csv'
rain =  pd.read_csv(filepath + filename)

time_period = [[2018, 5, 1], [2020, 8, 1]]
bool1 = (rain.Year == time_period[0][0]) & (rain.Month == time_period[0][1]) & (rain.Day == time_period[0][2])
bool2 = (rain.Year == time_period[1][0]) & (rain.Month == time_period[1][1]) & (rain.Day == time_period[1][2])
index_slice = [*rain[bool1].index.tolist(), *rain[bool2].index.tolist()]
rain = rain.iloc[index_slice[0]:index_slice[1]]
rain.reset_index(inplace=True)
for i in range(rain.shape[0]):
    rain.loc[i, 'Time'] = datetime.date(rain.Year[i], rain.Month[i], rain.Day[i]).strftime("%Y-%m-%d")
rain = rain.filter(items=['Time', 'Rainfall amount (millimetres)'])
rain.to_csv(filepath + 'rain_sliced.csv')
rain.plot(x = 'Time', y = 'Rainfall amount (millimetres)')
