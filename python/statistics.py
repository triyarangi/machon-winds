import datetime as dt
import numpy as np

from python.profile_database import ProfileDatabase
from python.plot_profile import plot_profile

################################################
# TEST


# parameters:
wmoId = 40179
minh = 15000
maxh = 25000

# pick compared datasets:
#
# TODO: comparing sones won't work, since they have variable size
model_label = "WRF" # WRF; TODO: ECMWF doesn't work yet
sonde_label = "LORES" # LORES or HIRES

# TODO: only those params are currently available:
param = "wvel_knt"
#param = "wdir_deg"

# date ranges:
start_date = dt.datetime(2016,07,01,00,00)
end_date = dt.datetime(2016,07,30,00,00)

# fetch data handles:
db = ProfileDatabase()
ds1 = db.get_dataset(model_label, wmoId, minh, maxh, param)
ds2 = db.get_dataset(sonde_label, wmoId, minh, maxh, param)


# prepare arrays for statistics:
sample_model_profile = db.get_profile(model_label, wmoId, start_date, minh, maxh, param)
heights = sample_model_profile.heights

count = 0
bias = np.zeros((len(heights)))
mae = np.zeros((len(heights)))
rmse = np.zeros((len(heights)))

# iterate over the database and compute things:
for (heights, model, sonde, curr_date) in db.iterator(ds1, ds2, start_date, end_date):

    print("Processing %s" % curr_date)

    model_values = model.values
    sonde_values = sonde.values

    delta = sonde_values - model_values

    bias += delta

    mae += abs(delta)
    rmse += delta**2

    count = count + 1

# finalize computation:
mae = mae / count
rmse = (rmse / count)**0.5

# print results:
for idx in range(len(bias)):

    print("%6dm : bias:%3.3f mae:%3.3f rmse:%3.3f" % (heights[idx], bias[idx], mae[idx], rmse[idx]))

# draw test comparison chart:
plot_profile(
    { "WRF WD(knot)" : model,
#      "HIRES WD(knot)" : rescaled_hi_profile.samples,
      "LORES WD(knot)" : sonde
     })

