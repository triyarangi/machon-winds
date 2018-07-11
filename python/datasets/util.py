from netCDF4 import Dataset


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