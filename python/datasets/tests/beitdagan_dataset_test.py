import datetime as dt
from python.datasets.beitdagan_sonde_dataset import BeitDaganSondeDataset

################################################
# TEST

dataset = BeitDaganSondeDataset()

datetime = dt.datetime(2016,07,01,00,00)


sd = dataset.get_profile(datetime, 15000, 25000, "pres_hpa")

for idx,hgt in enumerate(sd.heights):
    print("%dm : %f"%(hgt, sd.values[idx]))


################################################
