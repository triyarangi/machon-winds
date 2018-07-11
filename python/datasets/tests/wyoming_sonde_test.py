import datetime as dt

from python.datasets.wyoming_sonde_dataset import WyomingSondeDataset

################################################
# TEST

sondeDataset = WyomingSondeDataset()

sonde_date = dt.datetime(2016,07,01,00,00)

profile = sondeDataset.get_station_profile("40179", sonde_date, 15000, 25000, "pres_hpa")

print( profile.samples )