import archive_config
import os.path
import datetime as dt
import numpy as np
import pandas as pd
from collections import OrderedDict

import python.datasets.util
from python.spatial_index import SpatialIndex
from python.station import WeatherStation
from python.vertical_profile import VerticalProfile

class ECMWFDataset:


    def __init__(self):

        self.dataset_dir = archive_config.ecmwf_dir

        if not os.path.isdir(self.dataset_dir):
            raise IOError("Cannot file ECMWF data folder %s" % archive_config.ecmwf_dir)

        # read levels to height mapping table:
        this_dir, this_filename = os.path.split(__file__)
        levels_file = os.path.join(this_dir, "ecmwf_levels.csv", )
        levels = pd.read_csv(levels_file, sep=" ", header=None)
        levels.columns = ["n", "a", "b", "ph", "pf", "gph", "hgt", "tk", "density"]
        altitudes = levels["hgt"]

        # pick a sample file
        sample_ds = None
        for subdir, dirs, files in os.walk(self.dataset_dir):
            for file in files:
                sample_ds = python.datasets.util.load_dataset(os.path.join(subdir, file))
            if sample_ds is not None:
                break

        z_profile = sample_ds.variables["lv_HYBL0"][:]


        self.all_hgts = np.zeros((len(z_profile)))
        for i, z in np.ndenumerate(z_profile):
            self.all_hgts[i] = altitudes[z]

        # create map of WRF points:
        lons = sample_ds.variables['lat_0'][:]
        lats = sample_ds.variables['lon_0'][:]

        self.indexer = SpatialIndex()

        for (i,lon) in np.ndenumerate( lons ):
            for (j, lat) in np.ndenumerate(lats):
                self.indexer.add( lat, lon, i, j )

    def get_profile(self, lat, lon, datetime, minh, maxh, params):
        path = self.create_filename( datetime )
        ds = python.datasets.util.load_dataset(path)

        (pi, pj, plat, plon) = self.indexer.get_closest_index(lat, lon)

        all_vals = {}

        for param in params:
            if param == "wvel_knt":
                ugrid = ds.variables["UGRD_P0_L105_GLL0"][:]
                vgrid = ds.variables["VGRD_P0_L105_GLL0"][:]
                uprofile = ugrid[0, :, pi, pj][0]
                vprofile = vgrid[0, :, pi, pj][0]
                all_vals[param] = (uprofile ** 2 + vprofile ** 2) ** 0.5 * 1.94384  # from m/s to knot
            elif param == "wdir_deg":
                ugrid = ds.variables["UGRD_P0_L105_GLL0"][:]
                vgrid = ds.variables["VGRD_P0_L105_GLL0"][:]
                uprofile = ugrid[0, :, pi, pj][0]
                vprofile = vgrid[0, :, pi, pj][0]

                # TODO : verify this conversion
                # ENTER CONDITION over wind speed
                # for i in range(len(vprofile)):
                # if np.sqrt(vprofile[i]**2+uprofile[i]**2) > 2 :
                # tmp[i] = 270-np.rad2deg(np.arctan(vprofile[i]/uprofile[i]))
                # else:
                # tmp[i] = np.NaN
                all_vals[param] = 270 - np.rad2deg(np.arctan(vprofile / uprofile))


            elif param == "u_knt":
                ugrid = ds.variables["UGRD_P0_L105_GLL0"][:]
                all_vals[param] = ugrid[0, :, pi, pj][0]
            elif param == "v_knt":
                vgrid = ds.variables["VGRD_P0_L105_GLL0"][:]
                all_vals[param] = vgrid[0, :, pi, pj][0]
            else:
                grid = ds.variables[param][:]
                all_vals[param] = grid[0, :, pi, pj][0]

        size = 0
        for hgt in self.all_hgts:
            if minh <= hgt <= maxh: size = size + 1
        # convert to numpy arrays:
        hgts = np.zeros((size), dtype=float)
        vals = {}
        for param in params:
            vals[param] = np.zeros((size), dtype=float)

        idx = 0
        for all_idx, hgt in enumerate(self.all_hgts):
            if minh <= hgt <= maxh:
                hgts[idx] = hgt
                for param in params:
                    vals[param][idx] = all_vals[param][all_idx]
                idx = idx + 1
        for param in params:
            vals[param] = np.flip(vals[param])

        hgts = np.flip(hgts)
        station = WeatherStation(-1, lat, lon, 0)

        return VerticalProfile(hgts, vals, station)

    def get_station_profile(self, station, datetime, minh, maxh, param):

        return self.get_profile( station.lat, station.lon, datetime, minh, maxh, param)


    def create_filename(self, datetime):
        return self.dataset_dir + "/" \
                + "/IS_" + datetime.strftime("%Y%m_%#d") + ".nc"




dataset = ECMWFDataset()

