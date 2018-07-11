import archive_config
import python.datasets.util
class ECMWFDataset:


    def __init__(self):

        self.index = {}

        #ds = python.datasets.util.load_dataset(archive_config.ecmwf_dir + "\\IS_201607_1.grb")

       #print ds


    def get_profile(self, lat, lon, datetime, param):

        return None

dataset = ECMWFDataset()

