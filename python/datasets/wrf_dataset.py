import datetime as dt
import numpy as np
import os.path
import math
from collections import OrderedDict

import python.datasets.util
from python.spatial_index import SpatialIndex
from python.station import WeatherStation
from python.vertical_profile import VerticalProfile
import archive_config

class WRFDataset:

    dataset_dir = archive_config.wrf_dir


    def __init__(self):

        if not os.path.isdir(self.dataset_dir):
            raise IOError("Cannot file WRF data folder %s" % self.dataset_dir)

        # pick a sample file
        sample_ds = None
        for subdir, dirs, files in os.walk(self.dataset_dir):
            for file in files:
                sample_ds = python.datasets.util.load_dataset(os.path.join(subdir, file))
            if sample_ds is not None:
                break

        elevation_grid = (sample_ds.variables["PH"][:] + sample_ds.variables["PHB"][:]) / 9.81
        self.all_hgts = elevation_grid[0,:,0,0]

        # create map of WRF points:
        lons = sample_ds.variables['XLONG'][:]
        lats = sample_ds.variables['XLAT'][:]

        self.indexer = SpatialIndex()

        for ((n,i,j),val) in np.ndenumerate( lons ):
            self.indexer.add( lats[n,i,j], lons[n,i,j], i, j )

    def get_station_profile(self, station, datetime, minh, maxh, param):

        return self.get_profile( station.lat, station.lon, datetime, minh, maxh, param)

    def get_profiles(self, stations, datetime, minh, maxh, param):

        profiles = {}
        for station in stations:
            station_profile = self.get_profile( station.lat, station.lon, datetime, minh, maxh, param)
            profiles[station] = station_profile
        return profiles

    def get_profile(self, lat, lon, datetime, minh, maxh, params):

        path = self.create_filename( datetime )

        ds = python.datasets.util.load_dataset(path)

        (pi,pj,plat,plon) = self.indexer.get_closest_index( lat, lon )

        elevation_grid = (ds.variables["PH"][:] + ds.variables["PHB"][:])/9.81

        all_hgts = elevation_grid[0,:,pi,pj]

        all_vals = {}

        for param in params:
            if param == "wvel_knt":
                ugrid = ds.variables["U"][:]
                vgrid = ds.variables["V"][:]
                uprofile = ugrid[0, :, pi, pj]
                vprofile = vgrid[0, :, pi, pj]
                all_vals[param] = (uprofile**2+vprofile**2)**0.5 * 1.94384
            elif param == "wdir_deg":
                ugrid = ds.variables["U"][:]
                vgrid = ds.variables["V"][:]
                uprofile = ugrid[0, :, pi, pj]
                vprofile = vgrid[0, :, pi, pj]
                # TODO : verify this conversion
                all_vals[param] = 270-np.rad2deg(np.arctan(vprofile/uprofile))
            elif param == "u_knt":
                ugrid = ds.variables["U"][:]
                all_vals[param] = ugrid[0, :, pi, pj]
            elif param == "v_knt":
                ugrid = ds.variables["V"][:]
                all_vals[param] = ugrid[0, :, pi, pj]
            elif param == "pres_hpa":
                ugrid = ds.variables["P"][:]
                all_vals[param] = ugrid[0, :, pi, pj]/100.0

            else:
                grid = ds.variables[param][:]
                all_vals[param] = grid[0,:,pi,pj]

        size = 0
        for hgt in all_hgts:
            if minh <= hgt <= maxh: size = size +1
        # convert to numpy arrays:
        hgts = np.zeros((size),dtype=float)
        vals = {}
        for param in params:
            vals[param] = np.zeros((size), dtype=float)

        idx = 0
        for all_idx, hgt in enumerate(all_hgts):
            if minh <= hgt <= maxh:
                hgts[idx] = hgt
                for param in params:
                    vals[param][idx] = all_vals[param][all_idx]
                idx = idx + 1

        station = WeatherStation(-1, lat, lon, 0)

        return VerticalProfile(hgts, vals, station)

    def create_filename(self, datetime):
        return self.dataset_dir + "/" + datetime.strftime("%Y%m%d%H") \
                + "/wrfout_d01_" + datetime.strftime("%Y-%m-%d") + "_00_00_00"

