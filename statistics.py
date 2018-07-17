#!/usr/bin/env python
import datetime as dt
import numpy as np
import os as os
import os.path

from python.profile_database import ProfileDatabase
from python.vertical_profile import VerticalProfile
from python.plot_profile import plot_profile

################################################
# TEST


# parameters:

# no of radiosonde:
wmoId = 41217
minh = 9000
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
start_date = dt.datetime(2016,04,01,00,00)
end_date = dt.datetime(2016,04,30,00,00)

# output figs dir:
outdir='/home/sigalit/Loon/machon-winds-master/'+str(wmoId)+'_'+sonde_label+'_Apr_2016_statistics/'
if not os.path.exists(outdir):
    os.makedirs(outdir)


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
mean_model = np.zeros((len(heights)))
mean_sonde = np.zeros((len(heights)))

var_model = np.zeros((len(heights)))
var_sonde = np.zeros((len(heights)))

rad_dir="//home/sigalit/sigdata/Loon_radiosondes/"
# iterate over the database and compute things:

for (heights, model, sonde, curr_date) in db.iterator(ds1, ds2, start_date, end_date):
     
    datetime = curr_date
    rad_file=rad_dir+datetime.strftime("%Y-%m") + "/" + \
                   datetime.strftime("%d") + "/" + \
            datetime.strftime("%Y-%m-%d_%HZ") + "_" + str(wmoId) + "_sounding.txt"
    #print rad_file
    #print os.path.exists(rad_file)
    #if radiosonde file exist
    if os.path.isfile(rad_file): 
        skip=0
        print("Processing %s" % curr_date)

        model_values = model.values
        sonde_values = sonde.values
    
    
    # check sonde values != null
        for il in range(len(sonde_values)):
            if np.isnan(sonde_values[il]) :
                skip=skip+1
            
        if (skip < (len(sonde_values))*0.5  ):
            delta = sonde_values - model_values

            bias += delta
    
            mean_model += model_values
            mean_sonde += sonde_values

            mae += abs(delta)
            rmse += delta**2

            count = count + 1
     


mean_model = mean_model/count
mean_sonde = mean_sonde/count


count=0
for (heights, model, sonde, curr_date) in db.iterator(ds1, ds2, start_date, end_date):
    datetime = curr_date
    rad_file=rad_dir+datetime.strftime("%Y-%m") + "/" + \
                   datetime.strftime("%d") + "/" + \
            datetime.strftime("%Y-%m-%d_%HZ") + "_" + str(wmoId) + "_sounding.txt"
    #if radiosonde file exist
    if os.path.isfile(rad_file): 
        skip=0
        print("Processing %s" % curr_date)

        model_values = model.values
        sonde_values = sonde.values
    
    # check sonde values != null
        for il in range(len(sonde_values)):
            if np.isnan(sonde_values[il]):
                skip=skip+1
            
        if (skip < (len(sonde_values))*0.5 ):    
    
            var_model += (mean_model - model_values)**2
            var_sonde += (mean_sonde - sonde_values)**2
            count = count + 1

# finalize computation:
bias = bias / count
mae = mae / count
rmse = (rmse / count)**0.5



var_model = (var_model / count)**0.5
var_sonde = (var_sonde / count)**0.5


# print number of events :
print 'number of days = ',count
# print results:
for idx in range(len(bias)):

    print("%6dm : bias:%3.3f mae:%3.3f rmse:%3.3f" % (heights[idx], bias[idx], mae[idx], rmse[idx]))

#plot_profile(
#    { "WRF WD(knot)" : model,
#      "HIRES WD(knot)" : rescaled_hi_profile.samples,
#      "LORES WD(knot)" : sonde
#     })

# draw test comparison chart:
plot_profile({
      "mae" : VerticalProfile(heights, mae, wmoId),
      "rmse" : VerticalProfile(heights, rmse, wmoId)
    },
    { 
     "bias" : VerticalProfile(heights, bias, wmoId)
    },outdir)
# save figure

plot_profile(    
    { "avg_model" : VerticalProfile(heights, mean_model, wmoId),
      "avg_sonde" : VerticalProfile(heights, mean_sonde, wmoId)
      }, None,outdir)
plot_profile(    
    { "var_model" : VerticalProfile(heights, var_model, wmoId),
      "var_sonde" : VerticalProfile(heights, var_sonde, wmoId)
      }, None,outdir)



