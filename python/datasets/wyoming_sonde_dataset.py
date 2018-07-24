import os
import datetime as dt
import numpy as np
from collections import OrderedDict
import math

import python.datasets.util
from python.station import WeatherStation
from python.vertical_profile import VerticalProfile
import python.station

import archive_config

################################################
# this class provides access to low resolution sonde dataset
#
class WyomingSondeDataset:

    ################################################
    # get profile for specified station wmoid
    def get_station_profile(self, wmoid, datetime, minh, maxh, params):

        # load sonde data:
        (samples, station) = self.load_sonde(wmoid, datetime)

        # convert to numpy arrays:
        # calculate size:
        size = 0
        for hgt in samples.iterkeys():
            if minh <= hgt <= maxh: size = size + 1

        # create arrays:
        hgts = np.zeros((size), dtype=float)
        vals = {}
        for param in params:
            vals[param] = np.zeros((size), dtype=float)
            vals[param][:] = np.nan

        # fill arrays:
        idx = 0
        for hgt in samples.iterkeys():
            if minh <= hgt <= maxh:
                hgts[idx] = hgt
                for param in params:
                    if param == 'u_knt':
                       
                        if  ( samples[hgt]["wdir_deg"] is None or samples[hgt]["wvel_knt"] is None ):
                            vals[param][idx] = None
                        else:
                            vals[param][idx] = samples[hgt]["wvel_knt"] * math.cos(math.radians(270-samples[hgt]["wdir_deg"]))
                            
                            
                            
                    elif param == 'v_knt':
                        if (  samples[hgt]["wdir_deg"]   is None or samples[hgt]["wvel_knt"] is None   ):
                            vals[param][idx] = None
                        else:
                            vals[param][idx] = samples[hgt]["wvel_knt"] * math.sin(math.radians(270-samples[hgt]["wdir_deg"]))
                            
                    elif param == 'wdir_deg': # remove wind dir values when wind speed is < 1 m/s
                        if (  samples[hgt]["wvel_knt"]  < 2 ):  
                            vals[param][idx] = None
                        else:
                            vals[param][idx] = samples[hgt][param]

                            
                    else:
                        vals[param][idx] = samples[hgt][param]


                idx = idx + 1
        # providing resulting profile:
        return VerticalProfile(hgts, vals, station)

    def get_profiles(self, stations, datetime, minh, maxh, param):

        profiles = {}
        for station in stations:
            station_profile = self.get_profile( station.wmoid, datetime, minh, maxh, param)
            profiles[station] = station_profile
        return profiles


    ################################################
    # initialize dataset
    def __init__(self):

        self.datasetDir = archive_config.wyoming_sonde_dir

        if not os.path.isdir(self.datasetDir):
            raise IOError("Cannot file sonde data folder %s" % self.datasetDir)

    ################################################
    # load sonde for specified date and station id
    def load_sonde(self, wmoid, datetime):
        filepath = self.datasetDir + "/" + datetime.strftime("%Y-%m") + "/" + datetime.strftime("%d") + "/" + datetime.strftime("%Y-%m-%d_%HZ") + "_" + str(wmoid) + "_sounding.txt"

        sonde_data = self.read_sonde( filepath )

        return sonde_data

    ################################################


    def read_sonde(self, sonde_filename):

        samples = OrderedDict()
        station = None

        with open( sonde_filename, 'r') as file:
            # skip header:
            file.readline(); file.readline(); file.readline(); file.readline()

            # read profile
            line = file.readline()
            while not line.startswith('==='):

                # a single point on vertical profile,
                # represented by variable map:
                sample = {
                    "pres_hpa"   : python.datasets.util.to_float(line[0:8]),
                    "hght_msl_m" : python.datasets.util.to_float(line[9:15]),
                    "temp_c"     : python.datasets.util.to_float(line[16:22]),
                    "dwpt_c"     : python.datasets.util.to_float(line[23:29]),
                    "relh"       : python.datasets.util.to_float(line[30:36]),
                    "mixr_gkg"   : python.datasets.util.to_float(line[37:43]),
                    "wdir_deg"   : python.datasets.util.to_float(line[44:50]),
                    "wvel_knt"   : python.datasets.util.to_float(line[51:58]),
                    "thta_k"     : python.datasets.util.to_float(line[58:64]),
                    "thte_k"     : python.datasets.util.to_float(line[65:71]),
                    "thtv_k"     : python.datasets.util.to_float(line[72:78])
                }

                samples[sample["hght_msl_m"]] = sample

                line = file.readline()

            # extract sonde station information:
            line = file.readline()
            if line.startswith("Station identifier:"):
                station_icao = line.split(":")[1]
                line = file.readline()
            station_number = int(line.split(":")[1])
            obs_time = file.readline().split(":")[1]
            station_lat = float(file.readline().split(":")[1])
            station_lon = float(file.readline().split(":")[1])
            station_hgt = float(file.readline().split(":")[1])

            station = WeatherStation(station_number, station_lat, station_lon, station_hgt)

        return samples, station
