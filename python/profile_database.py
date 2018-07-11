import datasets.wrf_dataset as wrf
import datasets.ecmwf_dataset as ecmwf
import datasets.beitdagan_sonde_dataset as beitdagan_sonde
import datasets.wyoming_sonde_dataset as wyoming_sonde
import python.datasets.stations_list as stations_list

class ProfileDatabase:

    def __init__(self):

        self.wrf_dataset = wrf.WRFDataset()
        self.ecmwf_dataset = ecmwf.ECMWFDataset()
        self.fine_sonde = beitdagan_sonde.BeitDaganSondeDataset()
        self.coarse_sonde = wyoming_sonde.WyomingSondeDataset()

    def get_profile(self, dataset_label, wmoid, datetime, minh, maxh, param):

        station = stations_list.stations[wmoid]

        if "WRF" == dataset_label:
            return self.wrf_dataset.get_station_profile( station, datetime, minh, maxh, param)
        elif "ECMWF" == dataset_label:
            return self.ecmwf_dataset.get_station_profile(station, datetime, minh, maxh, param)
        elif "HIRES" == dataset_label:
            return self.fine_sonde.get_profile( datetime, minh, maxh, param)
        elif "LORES" == dataset_label:
            return self.coarse_sonde.get_station_profile(station.wmoid, datetime, minh, maxh, param)



