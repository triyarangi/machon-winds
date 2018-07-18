import os.path

import python.datasets.util
from python.station import WeatherStation
from collections import OrderedDict
from python.vertical_profile import VerticalProfile
import archive_config
import math

import numpy as np

import datetime as dt

################################################
# this class provides access to Beit Dagan
# high resolution sonde dataset
#
class BeitDaganSondeDataset:


    def __init__(self):

        self.files = []
        if not os.path.isdir(archive_config.highres_sonde_dir):
            raise IOError("Cannot file sonde data folder %s" % archive_config.highres_sonde_dir)

    def get_profiles(self, stations, datetime, minh, maxh, param):

        profiles = {}
        for station in stations:
            if station.wmoid == 40179:
                station_profile = self.get_profile(station.wmoid, datetime, minh, maxh, param)
                profiles[station] = station_profile
        return profiles

    ################################################
    # Retrieve a sonde from specified date
    #
    def get_profile(self, date, minh, maxh, params):

        # create filename:
        filename = archive_config.highres_sonde_dir + "/" + \
                   date.strftime("%Y%m%d%H") + "_physical"

        (samples, station) = self.read_sonde( filename )

        size = 0
        for hgt in samples.iterkeys():
            if minh <= hgt <= maxh: size = size +1
        # convert to numpy arrays:
        hgts = np.zeros((size),dtype=float)
        vals = {}
        for param in params:
            vals[param] = np.zeros((size), dtype=float)

        idx = 0
        for hgt in samples.iterkeys():
            if minh <= hgt <= maxh:
                hgts[idx] = hgt
                for param in params:
                    if param == 'u_knt':
                        vals[param][idx] = samples[hgt]["wvel_knt"] * math.cos(math.radians(270-samples[hgt]["wdir_deg"]))
                    elif param == 'v_knt':
                        vals[param][idx] = samples[hgt]["wvel_knt"] * math.sin(math.radians(270-samples[hgt]["wdir_deg"]))
                    else:
                        vals[param][idx] = samples[hgt][param]
                idx = idx+1


        return VerticalProfile(hgts, vals, station)


    ################################################
    # read sonde from a file into VerticalDataset
    #
    def read_sonde(self, sonde_filename):

        sonde_data = None
        samples = OrderedDict()
        station = None

        with open( sonde_filename, 'r') as file:
            # skip header:
            line = file.readline()
            while not line.startswith('LOCATION'):
                line = file.readline()

            parts = line.split()
            station_lat = float(parts[4])
            station_lon = float(parts[6])
            # roll forward to surface obs description
            while not line.startswith('PRESSURE'):
                line = file.readline()

            surface_pressure_mb = float(line.split(":")[1].split()[0])
            station_hgt = float(file.readline().split(":")[1].split()[0])
            surface_temp_c = float(file.readline().split(":")[1].split()[0])
            surface_relh = float(file.readline().split(":")[1].split()[0])
            surface_wdir_deg = float(file.readline().split(":")[1].split()[0])
            surface_wvel_knt = float(file.readline().split(":")[1].split()[0])
            try:
                cloud_code = float(file.readline().split(":")[1].split()[0])
            except ValueError:
                cloud_code = -1
            station_number = int(file.readline().split(":")[1].split()[0])
            station_icao = file.readline().split(":")[1].split()[0]

            self.station = WeatherStation(station_number, station_lat, station_lon, station_hgt)

            while len(line) != 0:

                while not line.startswith('------------------------------------------------'):
                    line = file.readline()

                while not line.startswith('PHYSICAL VALUES') and len(line) != 0:
                    # a single point on vertical profile,
                    # represented by variable map:
                    sample = {
                        "temp_c":     python.datasets.util.to_float(line[9:16]),
                        "relh":       python.datasets.util.to_float(line[16:22]),
                        "pres_hpa":   python.datasets.util.to_float(line[22:29]),
                        "hght_sur_m": python.datasets.util.to_float(line[29:37]),
                        "hght_msl_m": python.datasets.util.to_float(line[37:45]),
                        "wdir_deg":   python.datasets.util.to_float(line[62:68]),
                        "wvel_knt":   python.datasets.util.to_float(line[68:75]),

                    }

                    samples[sample["hght_msl_m"]] = sample

                    line = file.readline()

            sonde_data = samples

        return (sonde_data, station)
