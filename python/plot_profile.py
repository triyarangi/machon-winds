import matplotlib.pyplot as plt
from python.datasets.wrf_dataset import WRFDataset
from collections import OrderedDict
import datetime as dt

def plot_profile( profiles ):
    for label in profiles.iterkeys():
        profile = profiles.get(label)

        print(label)
        plt.plot( profile.values, profile.heights, label=label)

    plt.legend(loc='best')
    plt.show()

