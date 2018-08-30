import datasets.wrf_dataset as wrf
import datasets.ecmwf_dataset as ecmwf
import datasets.beitdagan_sonde_dataset as beitdagan_sonde
import datasets.wyoming_sonde_dataset as wyoming_sonde
import python.datasets.stations_list as stations_list
import numpy as np

import datetime as dt
 
class ProfileDatabase:

    def __init__(self):

        self.wrf_dataset = wrf.WRFDataset()
        self.ecmwf_dataset = ecmwf.ECMWFDataset()
        self.fine_sonde = beitdagan_sonde.BeitDaganSondeDataset()
        self.coarse_sonde = wyoming_sonde.WyomingSondeDataset()

    def get_heights(self, minh, maxh):
        size = 0
        for hgt in self.wrf_dataset.all_hgts:
            if minh <= hgt <= maxh: size = size +1
        # convert to numpy arrays:
        hgts = np.zeros((size),dtype=float)

        idx = 0
        for all_idx, hgt in enumerate(self.wrf_dataset.all_hgts):
            if minh <= hgt <= maxh:
                hgts[idx] = hgt
                idx = idx + 1

        return hgts

    def get_profile(self, dataset_label, station, datetime, minh, maxh, params ):

        try:
            #
            if "WRF" == dataset_label:
                return self.wrf_dataset.get_station_profile( station, datetime, minh, maxh, params )
            elif "ECMWF" == dataset_label:
                return self.ecmwf_dataset.get_station_profile( station, datetime, minh, maxh, params)
            elif "HIRES" == dataset_label:
                return self.fine_sonde.get_profile( datetime, minh, maxh, params)
            elif "LORES" == dataset_label:
                return self.coarse_sonde.get_station_profile(station.wmoid, datetime, minh, maxh, params)

        except (IOError, AttributeError, ValueError) as (strerror):
            print ("Failed to read %s data for %s" % (dataset_label, datetime))
            print ("%s" % strerror)
            return None

    def get_profiles(self, dataset_label, stations, datetime, minh, maxh, param):
        try:
            #
            if "WRF" == dataset_label:
                return self.wrf_dataset.get_profiles( stations, datetime, minh, maxh, param)
            elif "ECMWF" == dataset_label:
                return self.ecmwf_dataset.get_profiles( stations, datetime, minh, maxh, param)
            elif "HIRES" == dataset_label:
                return self.fine_sonde.get_profiles( datetime, minh, maxh, param)
            elif "LORES" == dataset_label:
                return self.coarse_sonde.get_profiles(stations.wmoid, datetime, minh, maxh, param)

        except (IOError, AttributeError, ValueError) as (errno, strerror):
            print ("Failed to read %s data for %s" % (dataset_label, datetime))
            print ("%s" % strerror)
            return None


    def get_dataset(self, dataset_label, minh, maxh, params):
        return ProfileDataset(self, dataset_label, minh, maxh, params)

    def iterator(self, ds1, ds2, height, station, min_date, max_date):
        return Iterator(ds1, ds2, height, station, min_date, max_date)

class ProfileDataset:

    def __init__(self, db, dataset_label, minh, maxh, params):
        self.db = db
        self.dataset_label = dataset_label

        self.minh = minh
        self.maxh = maxh
        self.params = params



    def get_profile(self, datetime, station ):
        return self.db.get_profile(self.dataset_label, station, datetime, self.minh, self.maxh, self.params)

    def get_profiles(self, datetime, stations):
        return self.db.get

class Iterator:
    def __init__(self, ds1, ds2, heights, station, min_date, max_date):

        self.ds1 = ds1
        self.ds2 = ds2
        self.heights = heights
        self.station = station
        self.min_date = min_date
        self.max_date = max_date
        self.curr_date = min_date



    def __iter__(self):
        return self

    def next(self):

            while self.curr_date <= self.max_date:
                prev_date = self.curr_date
                self.curr_date += dt.timedelta(1)

                p1 = self.ds1.get_profile(prev_date, self.station )
                p2 = self.ds2.get_profile(prev_date, self.station )

                if p1 is None or p2 is None:
                    continue

                # skipping invalid sonde:
                p1 = p1.interpolate(self.heights)
                p2 = p2.interpolate(self.heights)

                return self.heights, p1, p2, prev_date

            if self.curr_date > self.max_date:
                raise StopIteration


