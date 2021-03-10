"""
This script is used to split the storm events downloaded from the website.
"""
# import packages
import numpy as np
import pandas as pd
import os
import datetime
# define the repository path
from common_settings import obspath
import matplotlib.pyplot as plt
import seaborn as sns

# separate the long time series into one-year data sets
file_name = '126001A_daily.csv'
df = pd.read_csv(obspath + file_name, index_col='Datetime')
# conver the index of df into datetime
time_format = "%H:%M:%S %d/%m/%Y"
df.index = pd.to_datetime(df.index, format=time_format)
# df.set_index(['Time'], inplace=True)


for year in range(2006, 2020):
    print(year)
    time_str = [f'00:00:00 01/07/{year}', f'00:00:00 30/06/{year+1}']
    time_period = [pd.datetime.strptime(time_str[0], time_format), 
        pd.datetime.strptime(time_str[1], time_format)]

    year1 = df.loc[time_period[0]:time_period[1], :] * 24 * 3600 / 1e6
    year1.rename(columns={year1.columns[0]: 'Flow (ML)'}, inplace=True)
    year1.to_csv(f'{obspath}{time_str[0][-4:]}_{time_str[1][-4:]}.csv')
