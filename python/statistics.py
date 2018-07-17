import datetime as dt
import numpy as np

from python.datasets import stations_list
from python.profile_database import ProfileDatabase
from python.plot_profile import plot_profile
from python.vertical_profile import VerticalProfile

################################################
# TEST


# parameters:
station = stations_list.stations[40179]
stations = [ station ]

minh = 15000
maxh = 25000

# pick compared datasets:
#
# TODO: comparing sondes won't work, since they have variable size
model_label = "WRF" # WRF; TODO: ECMWF doesn't work yet
sonde_label = "LORES" # LORES or HIRES

# TODO: only those params are currently available:
param = "wvel_knt"
#param = "wdir_deg"

# date ranges:
start_date = dt.datetime(2016,07,01,00,00)
end_date = dt.datetime(2016,07,3,00,00)

# fetch data handles:
db = ProfileDatabase()
ds1 = db.get_dataset(model_label, minh, maxh, param)
ds2 = db.get_dataset(sonde_label, minh, maxh, param)

# prepare arrays for statistics:
sample_model_profile = db.get_profile(model_label, station, start_date, minh, maxh, param)
heights = sample_model_profile.heights

count = 0
bias = np.zeros((len(heights)))
mae = np.zeros((len(heights)))
rmse = np.zeros((len(heights)))
model_avg = np.zeros((len(heights)))
sonde_avg = np.zeros((len(heights)))

# iterate over the database and compute things:
for (heights, model, sonde, curr_date) in db.iterator(ds1, ds2, station, start_date, end_date):

    print("Processing %s" % curr_date)

    model_values = model.values
    sonde_values = sonde.values

    delta = sonde_values - model_values

    bias += delta

    mae += abs(delta)
    rmse += delta**2

    model_avg += model_values
    sonde_avg += sonde_values

    count = count + 1

# finalize computation:
bias = bias / count
mae = mae / count
rmse = (rmse / count)**0.5

model_avg /= count
sonde_avg /= count

model_var = np.zeros((len(heights)))
sonde_var = np.zeros((len(heights)))

for (heights, model, sonde, curr_date) in db.iterator(ds1, ds2, station,start_date, end_date):
    model_var += (model_avg - model.values)**2
    sonde_var += (sonde_avg - sonde.values) ** 2

model_var = (model_var / count)**0.5
sonde_var = (sonde_var / count)**0.5
# print results:
#for idx in range(len(bias)):
    #print("%6dm : bias:%3.3f mae:%3.3f rmse:%3.3f" % (heights[idx], bias[idx], mae[idx], rmse[idx]))

# draw test comparison chart:
title = "%s comparison for %s, station %s" %( param, curr_date, station.wmoid)
plot_profile(
    { "WRF WD(knot)" : model,
#      "HIRES WD(knot)" : rescaled_hi_profile.samples,
      "LORES WD(knot)" : sonde
     },
    title=title
)

title = "Errors for %s to %s, station %s" % (start_date, end_date, station.wmoid)
plot_profile(
    {
        "RMSE" : VerticalProfile(heights, rmse, station),
        "MAE" : VerticalProfile(heights, mae, station)
    },
    {
        "Bias" : VerticalProfile(heights, bias, station)
    },
    title
)

title = "Variance for %s to %s, station %s" % (start_date, end_date, station.wmoid)
plot_profile(
    {
        "Model" : VerticalProfile(heights, model_var, station),
        "Sonde" : VerticalProfile(heights, sonde_var, station)
    },
    title=title
)