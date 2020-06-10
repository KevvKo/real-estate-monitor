import json
from geopy.geocoders import Nominatim 
from folium.plugins import HeatMap
import pandas as pd
import geopandas as gpd
import folium
import os
import matplotlib.pyplot as plt
import MySQLdb
import sys

tn = "jena"

#integrate the db connection
db = MySQLdb.Connect(
    host = 'localhost',
    user= 'kevin',
    password = 'Montera93',
    database = 'apartment_monitoring'
)

cursor = db.cursor()
query = "SELECT * FROM apartments_{}".format(tn)

with db.cursor(MySQLdb.cursors.DictCursor) as cursor:
    cursor.execute(query)
    data = cursor.fetchall()

    #loads the json array as a dataframe in pandas
    df = pd.DataFrame(data)
    df['coldrent'] = pd.to_numeric(df['coldrent'])
    print(df)
    #removing all rows, which has no validate coordinates
    df = df.dropna(subset = ['latitude', 'longitude', 'coldrent', 'roomnumber'])
    
    #additional line to filter the dataframe for apartments with a specific roomnumber
    df = df[df['roomnumber'] == 2]

    #filter the postcodes and creating a new vector, which contains average rent of a district 
    postcodes = df['postcode'].unique()

    averageRentDf = pd.DataFrame({
        'postcode' : [],
        'averageRent': []})

    for postcode in postcodes:
        values = df[df['postcode'] == postcode]

        averageRentDf = averageRentDf.append({'postcode': str(postcode), 'averageRent': values['coldrent'].sum() / len(values)}, ignore_index= True)

    #creating a geojson with an unique id 
    jenaDistricts = gpd.read_file('real-estate-monitor/jenabezirke.geojson')
 
    #init the mal layout and the centr of the town
    hmap = folium.Map(location=[df['latitude'].iloc[0], df['longitude'].iloc[0]], zoom_start=13)

    for index, row in df.iterrows():

        popUpText = 'Postcode: ' + str(row['postcode']) + '\n' + 'Coldrent: ' + str(row['coldrent'])

        folium.CircleMarker(location=[row['latitude'], row['longitude']],popup = popUpText, radius = 2, color= '#C13F3F', fill_color='#C13F3F').add_to(hmap)

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
    hmap.save('real-estate-monitor/jena.html')