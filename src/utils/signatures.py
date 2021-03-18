import pandas as pd
import numpy as np
import lmfit
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

# define objective function
# considering penalty while residual large
def residual(p, x, y):
    """
    Helper for defining objective function.

    Parameters
    ----------
    p : instance of parameter object, p = lmfit.Parameters()
    x : numpy arrary, input variable
    y : numpy array, variable for modelling

    Return
    ------
    obj_func : array or scalar value for miniming
    """
    y_mod = p['a'] * x ** p['b'] + p['c'] # +1.5
    bias = np.abs(np.average(y_mod - y))
    rel_bias = bias / np.average(y)
    resid = np.log(y_mod) - np.log(y)
    obj_func = (1 + 0.02 * rel_bias) * resid

    return obj_func

# do data regression
def nonlinear_fit(p, func, x, y, opti_method='differential_evolution'):
    """
    define objective function with the consideration penalty while residual large

    Parameters
    ----------
    p : instance of parameter object, p = lmfit.Parameters()
    func : objective function for minimization
    x : numpy arrary, input variable
    y : numpy array, variable for modelling
    opti_method : string,  global optimization method, default is differential_evolution

    Return
    ------
    out1 : instance of global minimization results object, method
    out2 : instance of  minimization results object
    ci : object of collections.OrderedDict, contains information of confidence interval
    trace : dict, The values are dictionaries with arrays of values for each variable, 
            and an array of corresponding probabilities for the corresponding cumulative variables

    """
    # create Minimizer
    mini = lmfit.Minimizer(func, p, nan_policy='omit', calc_covar=False, fcn_kws={'x': x, 'y': y})

    # first solve with differential_evolution
    out1 = mini.minimize(method=opti_method)
 
    # then solve with Levenberg-Marquardt using the
    # differential_evolution solution as a starting point
    out2 = mini.minimize(method='leastsq', params=out1.params)

    lmfit.report_fit(out2.params)

    ci, trace = lmfit.conf_interval(mini, out2, sigmas=[1, 2],
                                trace=True, verbose=False)
    lmfit.printfuncs.report_ci(ci)
    return out1, out2, ci, trace

# end