from python.profile_database import ProfileDatabase
import datetime as dt
import python.datasets.util as util
from python.plot_profile import plot_profile
from collections import OrderedDict

################################################
# TEST



wmoId = 40179
minh = 15000
maxh = 25000
param = "wvel_knt"
#param = "wdir_deg"

db = ProfileDatabase()

start_date = dt.datetime(2016,07,01,00,00)
end_date = dt.datetime(2016,07,4,00,00)

count = 0
bias = OrderedDict()
mae = OrderedDict()
rmse = OrderedDict()

for sample_date in util.daterange(start_date, end_date):

    print("Processing %s" % sample_date)
    try:
        wrf_profile = db.get_profile("WRF", wmoId, sample_date, minh, maxh, param)
    except IOError:
        print ("Failed to read WRF data for %s" % sample_date)
        continue
#    try:
#        hi_sonde_profile = db.get_profile("HIRES", wmoId, sample_date, minh, maxh, param)
#    except IOError:
#        print ("Failed to read HIRES data for %s" % sample_date)
#        continue
    try:
        lo_sonde_profile = db.get_profile("LORES", wmoId, sample_date, minh, maxh, param)
    except IOError:
        print ("Failed to read LORES data for %s" % sample_date)
        continue

#    rescaled_hi_profile = hi_sonde_profile.rescale(wrf_profile.samples.keys())
    rescaled_lo_profile = lo_sonde_profile.rescale(wrf_profile.samples.keys())

    print( "%s WRF %s" % (sample_date, wrf_profile.samples))
    print( "%s LORES %s" % (sample_date, rescaled_lo_profile.samples))

    for hgt in wrf_profile.samples.iterkeys():

        wrf_value = wrf_profile.samples[hgt]
        sonde_value = rescaled_lo_profile.samples[hgt]

        if wrf_value is None or sonde_value is None: continue

        if not hgt in bias:
            bias[hgt] = mae[hgt] = rmse[hgt] = 0

        bias[hgt] += wrf_value - sonde_value
        mae[hgt] += abs(wrf_value - sonde_value)
        rmse[hgt] += (wrf_value - sonde_value)**2

    count = count + 1

for hgt in bias.iterkeys():
    mae[hgt] = mae[hgt] / count
    rmse[hgt] = (rmse[hgt] / count)**0.5

    print("%6dm : bias:%3.3f mae:%3.3f rmse:%3.3f" % (hgt, bias[hgt], mae[hgt], rmse[hgt]))

plot_profile(
    { "WRF WD(knot)" : wrf_profile.samples,
#      "HIRES WD(knot)" : rescaled_hi_profile.samples,
      "LORES WD(knot)" : rescaled_lo_profile.samples
     })

