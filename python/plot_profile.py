import matplotlib.pyplot as plt
from python.datasets.wrf_dataset import WRFDataset
from collections import OrderedDict
import datetime as dt

def plot_profile( line_profiles, scatter_profiles ,outdir,title=""):
    if line_profiles is not None:
        for label in line_profiles.iterkeys():
            profile = line_profiles.get(label)
            plt.plot( profile.values, profile.heights, label=label)
    if scatter_profiles is not None:
        for label in scatter_profiles.iterkeys():
            profile = scatter_profiles.get(label)
            plt.scatter( profile.values, profile.heights, label=label)

    plt.title(title)
    plt.legend(loc='best')
    plt.savefig(outdir+label+'.png')
    plt.show()
