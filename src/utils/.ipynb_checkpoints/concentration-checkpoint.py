import pandas as pd
import numpy as np
import datetime
import os
from scipy import array
from scipy.interpolate import interp1d

def subst(x, str_re, loc):
    """
    Parameters:
    -----------
    x :  str, the string to be updated
    str_re :  str, the new string to replace
    loc : int or numpy.array, the index of where to replace x with y

    Returns:
    --------
    x_new : updated new string
    """
    if isinstance(loc, int):
        if loc == -1:
            x_new = x[:loc] + str_re
        else:
            x_new = x[:loc] + str_re + x[loc+1:]
    elif loc[-1] == -1:
        x_new = x[:loc[0]] + str_re
    else:
        x_new = x[:loc[0]] + str_re + x[loc[1]+1:]

    return x_new
# End subst()

def prep_cq(concentration, cons_name, discharge):
    """
    Parameters:
    ------------
    fnames : list, list of file names
    index_file : int, the index of file to read
    loc : np.array, location where the string to be replaced
    savefile : Bool, optional, save files if True

    Returns:
    ------------
    files saved to the given directory.
    """
    concentration.rename(columns={concentration.columns[0]: 'Time',
                            concentration.columns[1]: '126001A-' + cons_name + '(mg/l)'}, inplace=True)
    concentration.drop(index=[0, 1], inplace=True)
    concentration.dropna(how='all', inplace=True, axis=1)
    # Match C-Q data according to time
    # Convert the string in "Time" to datetime
    concentration = conc_time_shift(concentration, time_format="%Y/%m/%d %H:%M")
    concentration = duplicate_average(concentration).set_index('Time')
    # concentration.drop_duplicates(keep='first', inplace=True)
    cq = combine_cq(concentration, discharge)
    return cq
# End prep_cq()

def combine_cq(concentration, discharge):
    cq = pd.concat([concentration, discharge], axis=1, join='inner')
    cq.reset_index(inplace=True)
    cols = cq.columns
    cq.loc[:, cols[1:]] = cq.loc[:, cols[1:]].astype(float)
    cq.rename(columns = {cols[-1] : 'Flow(m3)'}, inplace=True)
    return cq
    # End combine_cq()

def conc_time_convert(concentration, loc, time_format="%Y/%m/%d %H:%M"):
    """ Assumptions: 1) If there are more than one obs C in an hour, the average of the C is used
    2) the mean of flow
    """
    monitor_minute = concentration['Time'][2][-2:]
    if monitor_minute == '00':
        concentration['Time'] = concentration['Time'].apply(subst, args=('00', loc[1]))
    else:
        concentration['Time'] = concentration['Time'].apply(subst, args=('00', loc[0]))

    concentration['Time'] = pd.to_datetime(concentration['Time'], format=time_format)
    concentration.set_index(['Time'], inplace=True)
    return concentration
    # End conc_time_convert()

def conc_time_shift(concentration, time_format="%Y/%m/%d %H:%M"):
    """
    Shift the time for linear interpolation.
    """
    concentration['Time'] = pd.to_datetime(concentration['Time'], format=time_format)
    index_start = concentration.index[0]
    for ii in range(index_start, len(concentration['Time'])+index_start):
        minute_ii = concentration['Time'][ii].minute
        if minute_ii > 30:
            concentration['Time'][ii] = concentration['Time'][ii] + datetime.timedelta(minutes=(60 - minute_ii))
        else:
            concentration['Time'][ii] = concentration['Time'][ii] - datetime.timedelta(minutes=minute_ii)
    return concentration     
    # End conc_time_shift()
    

def conc_interpolate(concentration, flow):
    """
    Interpolate constituent concentration linearly and return the hourly loads. 
    Follow the assumptions for linear interpolation.
    The index of the two dataframes follows the same format. 
    Instead of adding tie down, the first and the last values are treated as the added points.
    """
    conc_time = concentration.index
    flow = flow.loc[conc_time[0]:conc_time[-1], :]
    cols_flow = flow.columns
    cols_conct = concentration.columns[0]
    
    # 插值
    flow.loc[conc_time[0], cols_conct] = concentration.loc[conc_time[0], :].values
    for ii in range(0, len(conc_time)-1):
        delta_time = (conc_time[ii+1] - conc_time[ii]).total_seconds() / 3600
        if delta_time > 24:
            print(delta_time, conc_time[ii+1])
        if delta_time == 1:
            flow.loc[conc_time[ii], cols_conct] = concentration.loc[conc_time[ii], :].values
        elif delta_time > 1:
            x_temp = flow.loc[conc_time[ii]:conc_time[ii+1], cols_flow[0]].values
            x = [x_temp[0], x_temp[-1]]
            y = [concentration.loc[conc_time[ii], :].values[0], concentration.loc[conc_time[ii+1], :].values[0]]
            f = interp1d(x, y)
            f_x = extrap1d(f)
            x_new = x_temp[1:-1]
            y_new = f_x(x_new)
            # import pdb; pdb.set_trace()
            flow.loc[conc_time[ii]:conc_time[ii+1], cols_conct] = \
                [concentration.loc[conc_time[ii], :].values[0], *y_new, concentration.loc[conc_time[ii+1], :].values[0]]
        else:
            raise AssertionError("The time interval is not hourly.")

    flow.loc[conc_time[-1], cols_conct] = concentration.loc[conc_time[-1], :].values
    flow['Loads'] = flow[cols_flow] * \
        flow[cols_conct].values.reshape(flow[cols_conct].values.shape[0], 1)
    return flow
    # End conc_interpolate()

def emc_cal(load, discharge):
    """
    Calculate EMC with \sum{l_t}/ \sum{discharge_t}
    load: numpy.ndarry, load time series
    discharge: numpy.ndarry, discharge time series
    """
    return load.sum() / discharge.sum()
    # End emc_cal()

def extrap1d(interpolator):
    xs = interpolator.x
    ys = interpolator.y

    def pointwise(x):
        
        if xs[0] == xs[1]:
            return xs.mean()
        
        elif x < xs[0]:
            y_return = ys[0]+(x-xs[0])*(ys[1]-ys[0])/(xs[1]-xs[0])
            if y_return > 0:
                return y_return
            else:
                return ys.min()
            
        elif x > xs[-1]:
            return ys[-1]+(x-xs[-1])*(ys[-1]-ys[-2])/(xs[-1]-xs[-2])
        else:
            return interpolator(x)

    def ufunclike(xs):
        return list(map(pointwise, array(xs)))

    return ufunclike
    # End extrap1d()

# define time period
def rainfall_events(filename):
    events = pd.read_csv(filename, index_col='ID')
    return events
    # End rainfall_events()

def load_flow_index_consistent(load_flow):
    # subset the conc_flow data
    index_list = list(load_flow.index)
    start_index = index_list.index('1/7/2017')
    for ii in range(start_index, len(index_list)):
        st_split = index_list[ii].split('/')
        index_list[ii] = f'{st_split[-1]}/{st_split[1]}/{st_split[0]}'
    load_flow.index = index_list
    # load_flow.to_csv('../data/low_interp_flow.csv')
    return load_flow
# End load_flow_index_consistent()

def duplicate_average(concentration):
    """
    This is used to average the duplicates of concentration.
    """
    duplicateCheck = concentration.duplicated(subset=['Time'], keep=False)
    # import pdb; pdb.set_trace()
    if concentration[duplicateCheck].shape[0] > 0:
        duplicate_time = set(concentration[duplicateCheck]['Time'])
        for tmp in duplicate_time:
            ind = concentration[concentration.Time == tmp].index
            concentration.loc[ind, concentration.columns[-1]] = \
                concentration.loc[ind, concentration.columns[-1]].mean(axis=0)    
        concentration.drop_duplicates(keep = 'first')
    return concentration
    # End duplicate_average()
    
def hourly_cq(flow_name, childpath, outpath):
    discharge = pd.read_csv(flow_name)
    discharge['Time'] = pd.to_datetime(discharge['Time'], format="%H:%M:%S %d/%m/%Y")
    discharge.set_index(['Time'], inplace=True)
    discharge.to_csv(flow_name, index_label='Time')

    # set the index for 
    fnames = os.listdir(childpath)
    cons_names = [fname.split('-')[-1][:-4] for fname in fnames[1:]]
    for i in range(1, len(fnames)):
        concentration = pd.read_csv(childpath + fnames[i])
        cq = prep_cq(concentration, cons_names[i-1], discharge)
        cq.to_csv(outpath + 'cq-' + cons_names[i-1] + '.csv', index=False)
    # End hourly_cq()

def high_cq_linear(conc_file, flow_file):
    conct = pd.read_csv(conc_file, index_col='Time').filter(like='mg')
    conct.index = pd.to_datetime(conct.index)
    flow = pd.read_csv(flow_file, index_col='Time').filter(like='low')
    flow.rename(columns={flow.columns[0]:'Flow (ML)'}, inplace=True)
    flow.index = pd.to_datetime(flow.index)
    load_flow = conc_interpolate(conct, flow).rename(columns={'Loads': 'Loads (kg)'})

    return load_flow
    # End high_cq_linear()

def event_emc(events, load_flow, index_range, loads_col, flow_col, 
    time_scale='d', multiplier=1):
    """
    Calcualte the event mean concentration.
    events: pandas.DataFrame, containing discrete events. 
        Columns at least contain: ['start, 'end', 'end']
    load_flow: pandas.DataFrame, containing concentration and flow after linear interpolation.
    """
    for i in range(index_range[0], index_range[1]):
        start, end = events.loc[i, ['start', 'end']]
        loads = load_flow.loc[start:end, loads_col]
        flow = load_flow.loc[start:end, flow_col]
        if 'h' in time_scale:
            start = pd.to_datetime(start + ' 00:00:00')
            end = pd.to_datetime(end + ' 23:00:00')

        events.loc[i, 'emc(mg/l)'] = emc_cal(loads, flow) * multiplier
        events.loc[i, 'Load(kg)'] = loads.sum() * multiplier
    return events
    # End event_emc()

def cumulative_lq(loads, flow):
    """
    Calculate the cumulative flow and constituent loads.
    loads: numpy.ndarray, loads at each time step (i.e., daily or hourly)
    flow: numpy.ndarray, flow at each time step (i.e., daily or hourly)
    """
    loads_ratio = np.cumsum(loads) / loads.sum()
    flow_ratio = np.cumsum(flow) / flow.sum()

    return {'loads_ratio': loads_ratio, 'flow_ratio': flow_ratio}
    # End cumulative_lq()
    
def excel_save(data, fn, index=True):
    writer = pd.ExcelWriter(fn)
    for key, val in data.items():
           val.to_excel(excel_writer=writer,sheet_name=key,index=index)
    writer.save()
    writer.close()
    
    # End excel_save()