from netCDF4 import Dataset
import datetime as dt

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