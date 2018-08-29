#!/usr/bin/env python
import datetime as dt
import numpy as np
import os.path

from python.profile_database import ProfileDatabase
from python.vertical_profile import VerticalProfile
from python.plot_profile import plot_profile
import python.datasets.stations_list as stations_list
import python.datasets.util as util

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
model_label = "ECMWF" # WRF; TODO: ECMWF doesn't work yet
sonde_label = "HIRES" # LORES or HIRES

# TODO: only those params are currently available:
params = ["wvel_knt", "wdir_deg", "u_knt", "v_knt"]
# param = "wdir_deg"

# date ranges:
start_date = dt.datetime(2016, 07, 20,00,00)
end_date   = dt.datetime(2016, 07, 22,00,00)

# output figs dir:
outdir='/home/sigalit/Loon/v23_7_2018/machon-winds-master/'+str(wmoId)+'_'+sonde_label+start_date.strftime("%Y-%m-%d")+end_date.strftime("-%d")+'_statistics/'
 
if not os.path.exists(outdir):
    os.makedirs(outdir)


# fetch data handles:
db = ProfileDatabase()
model_ds = db.get_dataset(model_label, minh, maxh, params)
sonde_ds = db.get_dataset(sonde_label, minh, maxh, params)


# prepare arrays for statistics:
heights = db.get_heights( minh, maxh)

rad_dir="//home/sigalit/sigdata/Loon_radiosondes/"


####################################################
# caching all relevant data:

profiles = {}
print("Caching profiles...")
for (heights, model, sonde, curr_date) in db.iterator(model_ds, sonde_ds, heights, station, start_date, end_date):
    print("Extracting %s..." % curr_date)
    profiles[curr_date] = (heights, model, sonde, curr_date)


####################################################
# preparing arrays for statistics:


 
bias = {}
mae = {}
rmse = {}

model_mean = {}
sonde_mean = {}

model_var = {}
sonde_var = {}
model_var2 = {}
sonde_var2 = {}
count = {}  # at each z level number of events  when model and measurement exist
 


for param in params:
    
    bias[param] = np.zeros((len(heights)))
    mae[param] = np.zeros((len(heights)))
    rmse[param] = np.zeros((len(heights)))
    model_mean[param] = np.zeros((len(heights)))
    sonde_mean[param] = np.zeros((len(heights)))

    model_var[param] = np.zeros((len(heights)))
    sonde_var[param] = np.zeros((len(heights)))
    model_var2[param] = np.zeros((len(heights)))
    sonde_var2[param] = np.zeros((len(heights)))
    
    count[param] = np.zeros((len(heights)))
     
####################################################
#  params = ["wvel_knt", "wdir_deg", "u_knt", "v_knt", "pres_hpa"]  
#   1 kt = 0.51444444444 mps
    
print("Calculating statistics...")
for (heights, model, sonde, curr_date) in profiles.values():
    for param in params:
        model_values = model.values[param]  # type: np array
        sonde_values = sonde.values[param]  # type: np array
        #print param
        #print model_values
        #print sonde_values
        if model_values is None or sonde_values is None:
            continue

        if param == "wdir_deg":
            delta = util.to_degrees(sonde.values["u_knt"], sonde.values["v_knt"])\
                    - \
                    util.to_degrees(model.values["u_knt"], model.values["v_knt"])
            for ix in range(len(heights)):
                delta[ix] = util.wrap_degrees(delta[ix])
        else:
            delta = sonde_values - model_values

        for ix in range(len(heights)):
            if (not np.isnan(delta[ix])): count[param][ix] += 1
            if (np.isnan(delta[ix])): delta[ix] = 0  # delta = 0 , do not increase number of events
        print count[param]

        bias[param] += delta

        model_mean[param] += model_values
        sonde_mean[param] += sonde_values

        mae[param] += abs(delta)
        rmse[param] += delta**2

        

for param in params:
    if param != "wdir_deg":
        model_mean[param] /= count[param]
        sonde_mean[param] /= count[param]
    bias[param] /= count[param]
    mae[param] /= count[param]
    rmse[param] = (rmse[param] / count[param])**0.5
    
    
# completed mean bias ame rmse calculations
    
 
    
model_mean["wdir_deg"] = util.to_degrees(model_mean["u_knt"],model_mean["v_knt"])
    
sonde_mean["wdir_deg"] = util.to_degrees(sonde_mean["u_knt"],sonde_mean["v_knt"])
    
    
    
####################################################
# second pass: calculate variance
count_mod={}
count_sonde={}
model_delta={}
sonde_delta={}

for param in params:
    count_mod[param]=np.zeros((len(heights)))
    count_sonde[param]=np.zeros((len(heights)))
    model_delta[param]=np.zeros((len(heights)))
    sonde_delta[param]=np.zeros((len(heights)))
     
        
    
for (heights, model, sonde, curr_date) in profiles.values():    
    for param in params:
        for ix in range(len(heights)):
             if (model.values[param] is not None and not np.isnan(model.values[param][ix])): count_mod[param][ix]+=1
             if (sonde.values[param] is not None and not np.isnan(sonde.values[param][ix])): count_sonde[param][ix]+=1
 
for (heights, model, sonde, curr_date) in profiles.values():

    for param in params:
        
        model_values = model.values[param]  # type: np array
        sonde_values = sonde.values[param]  # type: np array
        if model_values is None or sonde_values is None:
            continue
        
        if param == "wdir_deg": 
            model_delta[param] = util.to_degrees(model_mean["u_knt"], model_mean["v_knt"]) \
                    -   util.to_degrees(model.values["u_knt"], model.values["v_knt"])
            sonde_delta[param] = util.to_degrees(sonde_mean["u_knt"], sonde_mean["v_knt"]) \
                    -   util.to_degrees(sonde.values["u_knt"], sonde.values["v_knt"])

            for ix in range(len(heights)):
                if model_values[ix] is None or sonde_values[ix] is None:
                    # skip assigment,
                    # in case of a single day, we will get 0 error- which means - no data , so one can not tell whether its a perfect
                    # match between model and rad or no data case
                    model_delta[param][ix] = 0
                    sonde_delta[param][ix] = 0
                else:
                    model_delta[param][ix] = util.wrap_degrees(model_delta[param][ix])
                    sonde_delta[param][ix] = util.wrap_degrees(sonde_delta[param][ix])


        else:
            model_delta[param] = model_mean[param] - model_values
            sonde_delta[param] = sonde_mean[param] - sonde_values



        for ix in range(len(heights)):
            if (not np.isnan(delta[ix])): count[param][ix] += 1
            if (np.isnan(delta[ix])): delta[ix] = 0  # delta = 0 , do not increase number of events

# second term for wind dir variance calculations:
        model_var2[param] += model_delta[param]
        sonde_var2[param] += sonde_delta[param]
        model_var[param] += model_delta[param]**2
        sonde_var[param] += sonde_delta[param]**2
    

# finalize computation:
# calculate variance:
for param in params:
     if param == "wdir_deg":
         model_var[param] = (model_var[param] / count_mod[param]  - (model_var2[param] / count_mod[param])**2 )**0.5
         sonde_var[param] = (sonde_var[param] / count_sonde[param]  - (sonde_var2[param]  / count_sonde[param])**2 )**0.5
     else:
        model_var[param] = (model_var[param] / count_mod[param]  )**0.5
        sonde_var[param] = (sonde_var[param] / count_sonde[param]  )**0.5



# print number of events :
print 'number of days [wdir] = ',count["wdir_deg"],count_mod["wdir_deg"],count_sonde["wdir_deg"]
 
# print results, screen and file:
ofile = outdir+'output_statistics_wind'


of = open( ofile, 'w') 
for idx in range(len(bias["wvel_knt"])):
    of.writelines("%6dm : bias:%3.3f mae:%3.3f rmse:%3.3f \n" % (heights[idx], bias["wvel_knt"][idx], mae["wvel_knt"][idx], rmse["wvel_knt"][idx]))
    print("%6dm : bias:%3.3f mae:%3.3f rmse:%3.3f" % (heights[idx], bias["wvel_knt"][idx], mae["wvel_knt"][idx], rmse["wvel_knt"][idx]))

########################################


for draw_param in ["wdir_deg"]:
    title = "Errors for %s to %s , station %s" % (start_date, end_date , station.wmoid)
    plot_profile(
        VerticalProfile(heights,{
          draw_param + " MAE": mae[draw_param],
          draw_param + " RMSE": rmse[draw_param]
        }, station),
        VerticalProfile(heights, {
          draw_param + " bias": bias[draw_param]
        }, station),
        outdir, title)
    # save figure

    title = "Means for %s to %s, station %s" % (start_date, end_date, station.wmoid)
    plot_profile(
        VerticalProfile(heights, {
           draw_param + " model mean": model_mean[draw_param],
           draw_param + " sonde mean": sonde_mean[draw_param]
        }, station),
        None, outdir, title)

    title = "Variance for %s to %s, station %s" % (start_date, end_date, station.wmoid)
    plot_profile(
        VerticalProfile(heights, {
           draw_param + " model variance": model_var[draw_param],
           draw_param + " sonde variance": sonde_var[draw_param]
        }, station),
        None, outdir, title)

