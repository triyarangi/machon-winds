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
#param = "wdir_deg"

db = ProfileDatabase()
wrf_profile = db.get_profile("WRF", wmoId, test_date, minh, maxh, param)

hi_sonde_profile = db.get_profile("HIRES", wmoId, test_date, minh, maxh, param)

lo_sonde_profile = db.get_profile("LORES", wmoId, test_date, minh, maxh, param)


rescaled_hi_profile = hi_sonde_profile.rescale(wrf_profile.heights)
rescaled_lo_profile = lo_sonde_profile.rescale(wrf_profile.heights)




plot_profile(
    { "WRF WD(knot)" : wrf_profile,
      "HIRES WD(knot)" : rescaled_hi_profile,
      "LORES WD(knot)" : rescaled_lo_profile
     })