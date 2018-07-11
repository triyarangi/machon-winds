import python.datasets.stations_list as stations_list

################################################
# TEST

for wmoid in stations_list.stations.iterkeys():
    print( wmoid )

