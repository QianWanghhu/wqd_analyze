import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def cq_line_plot(df, ylabel_str, xycols, logy=False, ax=None):
    """
    df : dataframe, dataframe to plot, contains the time as the first column
    ylabel : str, str to set as the y-axis label
    logy : Bool, optional. If True, the first y axis will be displayed in log scale
    """
    sns.set_style('white')
    ax1 = df.plot(x = xycols[0], y = xycols[2], kind = 'line', ylim = [0, 7],
        logy = logy, ax = ax) #
    ax.set_ylabel(ylabel_str)
    ax2 = ax1.twinx()
    df.plot(x = xycols[0], y = xycols[1], kind = 'scatter', ax = ax2, 
            color = 'orange', alpha = 0.5, s = 1)



def regression_plot(x, y, param_dict, flow_logic, r2_value, text_loc, x_lab, y_lab, x_range):
    """
    Helper for plotting curve fitting results.

    Parameters
    ----------
    param_dict : dictionary of parameters, e.g. {'a':2, 'b':4}
    flow_logic : boolean values, check whether the curve fitting is for flow and one water quality indicator
    r2_value : float, r2_score
    text_loc : list, location for text showing in the figure

    Return
    ------
    fig : figure
    """
    # x_range = np.linspace(0.0001, 1500, 1500)
    # x_range = np.linspace(-2,3,1500)
    x_range = 10 ** x_range
    y_range = param_dict['a'] * x_range ** param_dict['b'] + param_dict['c']
    fig = plt.figure(figsize=(10, 7))
    plt.plot(x,y,'bo')
    plt.plot(x_range, y_range, 'r--', 
             label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % (param_dict['a'],param_dict['b'], param_dict['c']))
    # plt.text(text_loc[0], text_loc[1], 'R2=%.4f' % (r2_value), fontsize=14)

    plt.yscale('log')
    plt.xscale('log')
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    if flow_logic:
        plt.xlabel('Flow (m^3/s)', fontsize=18)
        plt.ylabel('Total suspended solids (mg/L)', fontsize=18)
    else:
        plt.xlabel(x_lab, fontsize=14)
        plt.ylabel(y_lab, fontsize=14)
    plt.legend(fontsize=14)
    return fig