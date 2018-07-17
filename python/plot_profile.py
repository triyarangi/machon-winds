import matplotlib.pyplot as plt
from python.datasets.wrf_dataset import WRFDataset
from collections import OrderedDict
import datetime as dt

def plot_profile( lineProfiles, scatterProfiles=None, title="" ):
    if lineProfiles is not None:
        for label in lineProfiles.iterkeys():
            profile = lineProfiles.get(label)
            plt.plot( profile.values, profile.heights, label=label)
    if scatterProfiles is not None:
        for label in scatterProfiles.iterkeys():
            profile = scatterProfiles.get(label)
            plt.scatter(profile.values, profile.heights, label=label)

    plt.title(title)

    plt.legend(loc='best')
    plt.show()

