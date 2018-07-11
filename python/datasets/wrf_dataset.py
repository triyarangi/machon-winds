import datetime as dt
import numpy as np
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

        sample_path = self.create_filename( dt.datetime(2016,07,01,00,00) )

        sample_ds = python.datasets.util.load_dataset(sample_path)

        lons = sample_ds.variables['XLONG'][:]
        lats = sample_ds.variables['XLAT'][:]

        self.indexer = SpatialIndex()

        for ((n,i,j),val) in np.ndenumerate( lons ):
            self.indexer.add( lats[n,i,j], lons[n,i,j], i, j )

    def get_station_profile(self, station, datetime, minh, maxh, param):

        return self.get_profile( station.lat, station.lon, datetime, minh, maxh, param)

    def get_profile(self, lat, lon, datetime, minh, maxh, param):

        path = self.create_filename( datetime )

        ds = python.datasets.util.load_dataset(path)

        (pi,pj,plat,plon) = self.indexer.get_closest_index( lat, lon )

        elevation_grid = (ds.variables["PH"][:] + ds.variables["PHB"][:])/9.81

        elevation_profile = elevation_grid[0,:,pi,pj]

        if param == "wvel_knt":
            ugrid = ds.variables["U"][:]
            vgrid = ds.variables["V"][:]
            uprofile = ugrid[0, :, pi, pj]
            vprofile = vgrid[0, :, pi, pj]
            param_profile = (uprofile**2+vprofile**2)**0.5 * 1.94384
        elif param == "wdir_deg":
            ugrid = ds.variables["U"][:]
            vgrid = ds.variables["V"][:]
            uprofile = ugrid[0, :, pi, pj]
            vprofile = vgrid[0, :, pi, pj]
            # TODO : verify this conversion
            param_profile = 270-np.rad2deg(np.arctan(vprofile/uprofile))
        else:
            grid = ds.variables[param][:]
            param_profile = grid[0,:,pi,pj]

        profile = OrderedDict()
        for i in range(0, len(param_profile)):

            h = elevation_profile[i]
            if minh <= h <= maxh:
                profile[round(elevation_profile[i])] = param_profile[i]

        #for key,var in ds.variables.items():
        #    desc = "<no desc>"
        #    if hasattr(var, 'description') :
        #        desc = var.description
        #    print("%s - %s" % (var.name, desc))

        #print "%d %d" % (plat, plon)

        station = WeatherStation(-1, lat, lon, 0)

        return VerticalProfile(profile, station)

    def create_filename(self, datetime):
        return self.dataset_dir + "/" + datetime.strftime("%Y%m%d%H") \
                + "/wrfout_d01_" + datetime.strftime("%Y-%m-%d") + "_00_00_00"
