from netCDF4 import Dataset
import datetime as dt
import numpy as np


def load_dataset( path):
    try:
        # open netcdf dataset:
        return Dataset(path)

    except (OSError, IOError) as e:  # failed to
        print ("Failed to open ", path, " : ", e)
        return None


# convert string to float, return None if failed
def to_float( str ):
    try:
        return float(str)
    except ValueError:
        return None


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + dt.timedelta(n)


def to_degrees(u, v):
     import math
     return (270. - ( np.arctan2(v,u)*(180./math.pi) ))%360.
   
def wrap_degrees(deg):
   if deg > +180: deg -= 360
   if deg < -180: deg += 360
   return deg


def nan_helper(y):
    """Helper to handle indices and logical indices of NaNs.

    Input:
        - y, 1d numpy array with possible NaNs
    Output:
        - nans, logical indices of NaNs
        - index, a function, with signature indices= index(logical_indices),
          to convert logical indices of NaNs to 'equivalent' indices
    Example:
        >>> # linear interpolation of NaNs
        >>> nans, x= nan_helper(y)
        >>> y[nans]= np.interp(x(nans), x(~nans), y[~nans])
    """

    return np.isnan(y), lambda z: z.nonzero()[0]