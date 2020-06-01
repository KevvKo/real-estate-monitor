import json
from geopy.geocoders import Nominatim 
from folium.plugins import HeatMap
import pandas as pd
import geopandas as gpd
import folium
import os
import matplotlib.pyplot as plt

#parse the json into a reversable dataset
with open ('real-estate-monitor/jena.json', 'r') as jsonfile:
    data = jsonfile.read().split('\n')[:-1]

#converting the data set in a reusable json array
for i in range(len(data)):
    data[i] = json.loads(data[i])

#loads the json array as a dataframe in pandas
df = pd.DataFrame(data)
df['coldrent'] = pd.to_numeric(df['coldrent'].str.replace(',','.'))

#removing all rows, which has no validate coordinates
df = df.dropna(subset = ['latitude', 'longtitude', 'coldrent', 'roomnumber'])

#additional line to filter the dataframe for apartments with a specific roomnumber
df = df[df['roomnumber'] == '1']

#filter the postcodes and creating a new vector, which contains average rent of a district 
postcodes = df['postcode'].unique()

averageRentDf = pd.DataFrame({
    'postcode' : [],
    'averageRent': []})

for postcode in postcodes:
    values = df[df['postcode'] == postcode]

    averageRentDf = averageRentDf.append({'postcode': postcode, 'averageRent': values['coldrent'].sum() / len(values)}, ignore_index= True)

#creating a geojson with an unique id 
jenaDistricts = gpd.read_file('real-estate-monitor/jenabezirke.geojson')

#init the mal layout and the centr of the town
hmap = folium.Map(location=[df['latitude'].iloc[0], df['longtitude'].iloc[0]], zoom_start=13)

for index, row in df.iterrows():
    popUpText = 'Postcode: ' + row['postcode'] + '\n' + 'Coldrent: ' + str(row['coldrent'])

    folium.CircleMarker(location=[row['latitude'], row['longtitude']],popup = popUpText, radius = 2, color= '#C13F3F', fill_color='#C13F3F').add_to(hmap)

folium.Choropleth(
    geo_data= jenaDistricts,
    name='choropleth',
    data= averageRentDf,
    columns=['postcode','averageRent'],
    key_on= 'feature.properties.plz',
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=1,
    legend_name='average coldrent in €'
).add_to(hmap)

folium.LayerControl().add_to(hmap)
hmap.save('apartmentScraper/jena.html')