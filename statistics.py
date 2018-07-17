#!/usr/bin/env python
import datetime as dt
import numpy as np
import os as os
import os.path

from python.profile_database import ProfileDatabase
from python.vertical_profile import VerticalProfile
from python.plot_profile import plot_profile
import python.datasets.stations_list as stations_list

################################################
# TEST


# parameters:

# no of radiosonde:
wmoId = 40179
station = stations_list.stations[wmoId]
stations = [ station ]
minh = 9000
maxh = 25000

# pick compared datasets:
#
# TODO: comparing sondes won't work, since they have variable size
model_label = "WRF" # WRF; TODO: ECMWF doesn't work yet
sonde_label = "LORES" # LORES or HIRES

# TODO: only those params are currently available:
param = "wvel_knt"
# param = "wdir_deg"

# date ranges:
start_date = dt.datetime(2016,07,01,00,00)
end_date = dt.datetime(2016,07,4,00,00)

# output figs dir:
outdir='/home/sigalit/Loon/machon-winds-master/'+str(wmoId)+'_'+sonde_label+'_Apr_2016_statistics/'
if not os.path.exists(outdir):
    os.makedirs(outdir)


# fetch data handles:
db = ProfileDatabase()
model_wind_vel_ds = db.get_dataset(model_label, minh, maxh, "wvel_knt")
sonde_wind_vel_ds = db.get_dataset(sonde_label, minh, maxh, "wvel_knt")
model_wind_dir_ds = db.get_dataset(model_label, minh, maxh, "wdir_deg")
sonde_wind_dir_ds = db.get_dataset(sonde_label, minh, maxh, "wdir_deg")


# prepare arrays for statistics:
heights = db.get_heights( minh, maxh)

rad_dir="//home/sigalit/sigdata/Loon_radiosondes/"
# iterate over the database and compute things:

wind_vel_profiles = {}
wind_dir_profiles = {}
print("Extracting wind profiles...")
for (heights, model, sonde, curr_date) in db.iterator(model_wind_vel_ds, sonde_wind_vel_ds, heights, station, start_date, end_date):
    print("Extracting %s..." % curr_date)
    wind_vel_profiles[curr_date] = (heights, model, sonde, curr_date)
for (heights, model, sonde, curr_date) in db.iterator(model_wind_dir_ds, sonde_wind_dir_ds, heights, station, start_date, end_date):
    print("Extracting %s..." % curr_date)
    wind_dir_profiles[curr_date] = (heights, model, sonde, curr_date)



count = 0
wvel_bias = np.zeros((len(heights)))
wvel_mae = np.zeros((len(heights)))
wvel_rmse = np.zeros((len(heights)))
wvel_mean_model = np.zeros((len(heights)))
wvel_mean_sonde = np.zeros((len(heights)))

wvel_var_model = np.zeros((len(heights)))
wvel_var_sonde = np.zeros((len(heights)))

print("Calculating statistics...")
for (heights, model, sonde, curr_date) in wind_vel_profiles.values():
    model_values = model.values  # type: np array
    sonde_values = sonde.values  # type: np array

    delta = sonde_values - model_values

    wvel_bias += delta

    wvel_mean_model += model_values
    wvel_mean_sonde += sonde_values

    wvel_mae += abs(delta)
    wvel_rmse += delta**2

    count = count + 1

wvel_mean_model = wvel_mean_model/count
wvel_mean_sonde = wvel_mean_sonde/count


count=0
for (heights, model, sonde, curr_date) in wind_vel_profiles.values():

    model_values = model.values
    sonde_values = sonde.values

    wvel_var_model += (wvel_mean_model - model_values)**2
    wvel_var_sonde += (wvel_mean_sonde - sonde_values)**2
    count = count + 1



# finalize computation:
wvel_bias = wvel_bias / count
wvel_mae = wvel_mae / count
wvel_rmse = (wvel_rmse / count)**0.5

wvel_var_model = (wvel_var_model / count)**0.5
wvel_var_sonde = (wvel_var_sonde / count)**0.5


# print number of events :
print 'number of days = ',count
# print results:
for idx in range(len(wvel_bias)):

    print("%6dm : bias:%3.3f mae:%3.3f rmse:%3.3f" % (heights[idx], wvel_bias[idx], wvel_mae[idx], wvel_rmse[idx]))

# plot_profile(
#    { "WRF WD(knot)" : model,
#      "HIRES WD(knot)" : rescaled_hi_profile.samples,
#      "LORES WD(knot)" : sonde
#     })

title = "Errors for %s, station %s" % (curr_date, station.wmoid)
plot_profile({
      "wvel_mae": VerticalProfile(heights, wvel_mae, station),
      "wvel_rmse": VerticalProfile(heights, wvel_rmse, station)
    },
    { 
     "wvel_bias": VerticalProfile(heights, wvel_bias, station)
    }, outdir, title)
# save figure

title = "Means for %s to %s, station %s" % (start_date, end_date, station.wmoid)
plot_profile(    
    { "wvel_avg_model": VerticalProfile(heights, wvel_mean_model, station),
      "wvel_avg_sonde": VerticalProfile(heights, wvel_mean_sonde, station)
      }, None, outdir, title)

title = "Variance for %s to %s, station %s" % (start_date, end_date, station.wmoid)
plot_profile(    
    { "wvel_var_model": VerticalProfile(heights, wvel_var_model, station),
      "wvel_var_sonde": VerticalProfile(heights, wvel_var_sonde, station)
      }, None, outdir, title)



count = 0
wdir_bias = np.zeros((len(heights)))
wdir_mae = np.zeros((len(heights)))
wdir_rmse = np.zeros((len(heights)))
wdir_mean_model = np.zeros((len(heights)))
wdir_mean_sonde = np.zeros((len(heights)))

wdir_var_model = np.zeros((len(heights)))
wdir_var_sonde = np.zeros((len(heights)))

print("Calculating statistics...")
for (heights, model, sonde, curr_date) in wind_dir_profiles.values():
    model_values = model.values  # type: np array
    sonde_values = sonde.values  # type: np array

    delta = 180 - np.abs(np.abs(model_values - sonde_values) - 180)

    wdir_bias += delta

    wdir_mean_model += model_values
    wdir_mean_sonde += sonde_values

    wdir_mae += abs(delta)
    wdir_rmse += delta**2

    count = count + 1

wdir_mean_model = wdir_mean_model/count
wdir_mean_sonde = wdir_mean_sonde/count


count=0
for (heights, model, sonde, curr_date) in wind_dir_profiles.values():

    model_values = model.values
    sonde_values = sonde.values

    model_delta = 180 - np.abs(np.abs(wdir_mean_model - model_values) - 180)
    sonde_delta = 180 - np.abs(np.abs(wdir_mean_sonde - sonde_values) - 180)

    wdir_var_model += (wdir_mean_model - model_values)**2
    wdir_var_sonde += (wdir_mean_sonde - sonde_values)**2
    count = count + 1

    # finalize computation:
wdir_bias = wdir_bias / count
wdir_mae = wdir_mae / count
wdir_rmse = (wdir_rmse / count) ** 0.5

wdir_var_model = (wdir_var_model / count) ** 0.5
wdir_var_sonde = (wdir_var_sonde / count) ** 0.5

title = "Errors for %s, station %s" % (curr_date, station.wmoid)
plot_profile({
      "wdir_mae": VerticalProfile(heights, wdir_mae, station),
      "wdir_rmse": VerticalProfile(heights, wdir_rmse, station)
    },
    {
     "wdir_bias": VerticalProfile(heights, wdir_bias, station)
    }, outdir, title)
# save figure

title = "Means for %s to %s, station %s" % (start_date, end_date, station.wmoid)
plot_profile(
    { "wdir_avg_model": VerticalProfile(heights, wdir_mean_model, station),
      "wdir_avg_sonde": VerticalProfile(heights, wdir_mean_sonde, station)
      }, None, outdir, title)

title = "Variance for %s to %s, station %s" % (start_date, end_date, station.wmoid)
plot_profile(
    { "wdir_var_model": VerticalProfile(heights, wdir_var_model, station),
      "wdir_var_sonde": VerticalProfile(heights, wdir_var_sonde, station)
      }, None, outdir, title)
