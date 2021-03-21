# RUN SOURCE to generate observation_ensemble.csv
import pandas as pd
import numpy as np
import veneer
from veneer.pest_runtime import *
from veneer.manage import start,kill_all_now
import time
import os
import spotpy as sp

first_port=15000
num_copies = 1
# define catchment_project and veneer_exe
project_path = 'src/DIN/pest_source/'
catchment_project= project_path + '/MW_BASE_RC10.rsproj'

# Setup Veneer
# define paths to veneer command and the catchment project
veneer_path = project_path + 'vcmd45/FlowMatters.Source.VeneerCmd.exe'
#Now, go ahead and start source
_, ports = start(catchment_project,
                     n_instances=num_copies,
                     ports=first_port,
                     debug=True,
                     veneer_exe=veneer_path,
                     remote=False,
                     overwrite_plugins=True)

vs = veneer.Veneer(port=first_port)
NODEs = 'gauge_126001A_SandyCkHomebush'
variables = ['Constituents@N_DIN@Downstream Flow Mass', 'Flow']
things_to_record = [{'NetworkElement':NODEs,
       'RecordingVariable':ele} for ele in variables]
vs.configure_recording(disable=[{}], enable=things_to_record)

time_start = time.time()
start_date = '01/07/2006'; end_date='30/06/2018'
variables = ['Constituents@N_DIN@Downstream Flow Mass', 'Downstream Flow Volume']
criteria = [{'NetworkElement':'gauge_126001A_SandyCkHomebush',
       'RecordingVariable': ele} for ele in variables]

# find links and upstream subcatchments
param = {'names':['DeliveryRatioSurface', 'DeliveryRatioSeepage', 'DWC', 'dissConst_DWC'],
              'new_values':[0, 0, 0, 0],
                     'funs' : [['Sugarcane'], ['Sugarcane'], ['Sugarcane'], 
                            ['Grazing Open', 'Grazing Forested', 'Conservation', 
                                   'Forestry', 'Horticulture', 'Urban', 'Water', 'Other', 'Irrigated Cropping']]}

# obtain param initial values
initial_values = {}
for p in param['names']:
       ind = param['names'].index(p)
       initial_values[p] = vs.model.catchment.generation.get_param_values(p, fus=param['funs'][ind])

# change param values and run the model to produce the loads contribution from each source
load = pd.DataFrame()
for p in param['names']:
       ind = param['names'].index(p)
       vs.model.catchment.generation.set_param_values(p, param['new_values'][ind], fus=param['funs'][ind])

       vs.drop_all_runs()
       vs.run_model(params={'NoHardCopyResults':True}, start = start_date, end = end_date) 

       # column_names = ['DIN_obs_load', 'flow']
       get_din = vs.retrieve_multiple_time_series(criteria=criteria[0])
       # get_flow = vs.retrieve_multiple_time_series(criteria=criteria[1])
       # get_din.columns = column_names[0]
       # get_flow.columns = column_names[1]
       din = get_din.loc[pd.Timestamp('2009-07-01'):pd.Timestamp('2018-06-30')]
       # flow = get_flow.loc[pd.Timestamp('2008-07-01'):pd.Timestamp('2018-06-30')]
       # store the daily results and the index of sampling
       din.rename(columns={din.columns[0]: p})
       load = pd.concat([load, din], axis=1)
       time_end = time.time()

# set the parameters to initial values
for p in param['names']:
       ind = param['names'].index(p)
       vs.model.catchment.generation.set_param_values(p, initial_values[p], fus=param['funs'][ind], fromList=True)

load.to_csv('data/observation_DRS_sources.csv')
print(f'{time_end - time_start} seconds')
print('----------Finished-----------')