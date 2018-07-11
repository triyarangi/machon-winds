from python.profile_database import ProfileDatabase
import datetime as dt
from python.plot_profile import plot_profile

################################################
# TEST

test_date = dt.datetime(2016,07,01,00,00)

wmoId = 40179
minh = 15000
maxh = 25000
param = "wvel_knt"

db = ProfileDatabase()
wrf_profile = db.get_profile("WRF", wmoId, test_date, minh, maxh, param)

hi_sonde_profile = db.get_profile("HIRES", wmoId, test_date, minh, maxh, param)

lo_sonde_profile = db.get_profile("LORES", wmoId, test_date, minh, maxh, param)

print(wrf_profile.samples)
print(hi_sonde_profile.samples)
print(lo_sonde_profile.samples)

rescaled_hi_profile = hi_sonde_profile.rescale(wrf_profile.samples.keys())
rescaled_lo_profile = lo_sonde_profile.rescale(wrf_profile.samples.keys())

print(wrf_profile.samples)
print(rescaled_hi_profile.samples)
print(rescaled_lo_profile.samples)



plot_profile(
    { "WRF WD(knot)" : wrf_profile.samples,
      "HIRES WD(knot)" : rescaled_hi_profile.samples,
      "LORES WD(knot)" : rescaled_lo_profile.samples
     })