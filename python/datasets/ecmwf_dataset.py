import archive_config
import os.path
import python.datasets.util
class ECMWFDataset:


    def __init__(self):

        if not os.path.isdir(archive_config.ecmwf_dir):
            raise IOError("Cannot file ECMWF data folder %s" % archive_config.ecmwf_dir)
        self.index = {}

        #ds = python.datasets.util.load_dataset(archive_config.ecmwf_dir + "//IS_201607_1.grb")

       #print ds


    def get_profile(self, lat, lon, datetime, param):

        return None

dataset = ECMWFDataset()

