# Load csv file
city_file = open("city_data.csv")

# Read data from csv file
city_data = city_file.readlines()

header = city_data[0]

# Store the [0] city_names, [1] latitudes, [2] longitudes
seen_counties = set()
counties = list()

for row in city_data[1:]:
    city_name, latitude, longitude = row.split(",")[0:3]
    # have already seen city?
    if (city_name in seen_counties): continue
    # add city to seen counties
    seen_counties.add(city_name)
    # add city data to list
    counties.append([city_name, float(latitude), float(longitude)])
    
#[print(x) for x in counties]

import math

# dict[city_name] = list((other_city_name, distance to other_city))
distanceDictionary = {}

def distance(latitude1, longitude1, latitude2, longitude2):
    radius = 6371e3 # calculation in metres
    phi1 = latitude1 * math.pi / 180 # convert to radians
    phi2 = latitude2 * math.pi / 180 # convert to radians
    
    d_phi = (latitude2 - latitude1) * math.pi / 180
    d_lambda = (longitude2 - longitude1) * math.pi / 180

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return radius * c

# loop through all pairings of counties
for city_name1, latitude1, longitude1 in counties:
    distanceDictionary[city_name1] = list()
    for city_name2, latitude2, longitude2 in counties:
        # distance between counties
        city_distance = distance(latitude1, longitude2, latitude2, longitude2)
        # add name and distance to dictionary
        distanceDictionary[city_name1].append((city_name2, city_distance))
    
    # sort elements from closest -> furthest
    distanceDictionary[city_name1] = sorted(distanceDictionary[city_name1], key = lambda x: x[1])

# save distanceDictionary to distance_dictionary.pickle file
import pickle

pickle_file = open("distance_dictionary.pickle", "wb")
pickle.dump(distanceDictionary, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)
pickle_file.close()