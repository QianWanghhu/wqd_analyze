import matplotlib.pyplot as plt
import seaborn as sns

def cq_line_plot(df, ylabel_str, xycols, logy=False, ax=None):
    """
    df : dataframe, dataframe to plot, contains the time as the first column
    ylabel : str, str to set as the y-axis label
    logy : Bool, optional. If True, the first y axis will be displayed in log scale
    """
    sns.set_style('white')
    ax1 = df.plot(x = xycols[0], y = xycols[2], kind = 'line', ylim = [0, 7],
        ylabel = ylabel_str, logy = logy, ax = ax) #
    ax2 = ax1.twinx()
    df.plot(x = xycols[0], y = xycols[1], kind = 'scatter', ax = ax2, 
            color = 'orange', alpha = 0.5, s = 1)