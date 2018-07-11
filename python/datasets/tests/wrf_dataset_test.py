import datetime as dt
from python.datasets.wrf_dataset import WRFDataset


################################################
# TEST

wrf_dataset = WRFDataset()

datetime = dt.datetime(2016,07,01,00,00)

profile = wrf_dataset.get_profile(32,32,datetime, 20000,30000, "P")

print( profile )