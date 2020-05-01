import json
from geopy.geocoders import Nominatim 
import geopandas

#parse the json into a reversable dataset
with open ('apartments.json', 'r') as jsonfile:
    data = jsonfile.read().split('\n')[:-1]

for i in range(len(data)):
    data[i] = json.loads(data[i])

#initialize a geocoder object and computing the coordinates (latitude, longitude) for every
#scraped adress, to make it possible to build a heat-map
locator = Nominatim(user_agent="test")
for i in range(len(data)):
    if(data[i]['street'] is not None):
        loc = data[i]['street'].strip() + ' ' + data[i]['town'].strip()
        location = locator.geocode(loc)

        #if the object exists, adding the coordinates to the dataset
        if(location is not None):
            data[i]['latitude'] = location.latitude
            data[i]['longtitude'] = location.longitude