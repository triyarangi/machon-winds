import matplotlib.pyplot as plt
from python.datasets.wrf_dataset import WRFDataset
from collections import OrderedDict
import datetime as dt

def plot_profile( profiles ):
    for label in profiles.iterkeys():
        profile = profiles.get(label)

        keys = []
        values = []

        for key, value in profile.iteritems():
            keys.append(key)
            values.append(value)

        plt.plot( values, keys,label=label)

    plt.legend(loc='best')
    plt.show()

