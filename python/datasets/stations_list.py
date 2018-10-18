import os
import archive_config
from wyoming_sonde_dataset import WyomingSondeDataset

################################################
# extract stations list based on Wyoming sondes
def extract_stations():
    print ("Extracting stations list...")

    sonde_dataset = WyomingSondeDataset()

    stations = {}

    files = []

    station_ids = []

    # collect all files in archive:
    for (dirpath, dirnames, filenames) in os.walk(archive_config.wyoming_sonde_dir):
        for filename in filenames:

            parts = filename.split("_")
            station_id = parts[2]
            if station_id not in station_ids:
                station_ids.append(station_id);

                (sonde_data, station) = sonde_dataset.read_sonde(dirpath + "/" + filename)

                stations[station.wmoid] = station

            files.extend(filename)
    return stations

stations = extract_stations()


def get_closest_station( lat, lon):
    min_dist = -1
    closest_station = None

    for station in stations:
        dist = (lat - station.lat) ** 2 + (lon - station.lon) ** 2
        if dist < min_dist or min_dist < 0:
            min_dist = dist
            closest_station = station
    if(dist > 0.01) :
        print 'STATION MIN_DIST closest station', closest_station , min_dist        
    return closest_station