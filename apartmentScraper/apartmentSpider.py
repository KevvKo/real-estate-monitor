import scrapy
import json
import os
import hashlib
from geopy.geocoders import Nominatim 
import geopandas

from scrapy.crawler import CrawlerProcess
from scrapy.crawler import Settings
from scrapy.utils.project import get_project_settings

from spiders.wggesuchtScraper import WggesuchtScraper
from spiders.immonetScraper import ImmonetScraper
from spiders.is24Scraper import Is24Scraper

settings = {
    'DOWNLOAD_DELAY' : 0,
    'ITEM_PIPELINES':{
        'pipelines.ApartmentPipeline':100,
    },
    'COOKIES_ENABLED': 'False'
    # 'FEED_FORMAT' : 'jsonlines',
    # 'FEED_URI' : 'rawdata.json'
}

#scraping the raw data and provide a json, which containing the raw data included duplicates
process = CrawlerProcess(settings=settings)

#scraping for jena
#process.crawl(WggesuchtScraper, url="https://www.wg-gesucht.de/wohnungen-in-Jena.66.2.1.0.html?offer_filter=1&city_id=66&noDeact=1&categories%5B%5D=2&rent_types%5B%5D=0")
#process.crawl(ImmonetScraper, url="https://www.immonet.de/immobiliensuche/sel.do?&sortby=0&suchart=1&objecttype=1&marketingtype=2&parentcat=1&city=111924&locationname=Jena")
#process.crawl(Is24Scraper, url="https://www.immobilienscout24.de/Suche/de/thueringen/jena/wohnung-mieten")

#scraping for berlin
process.crawl(WggesuchtScraper, url="https://www.wg-gesucht.de/wohnungen-in-Berlin.8.2.1.0.html")
process.crawl(ImmonetScraper, url="https://www.immonet.de/immobiliensuche/sel.do?&sortby=0&suchart=1&objecttype=1&marketingtype=2&parentcat=1&city=87372&locationname=Berlin")
process.crawl(Is24Scraper, url="https://www.immobilienscout24.de/Suche/de/berlin/berlin/wohnung-mieten?enteredFrom=result_list")
process.start() # the script will block here until the crawling is finishedg 

#take the rawdata.json to prepare the data and remove duplicates
hashes = set()

#opens the scraped items-file
with open ('rawdata.json', 'r') as jsonfile:
    data = jsonfile.read()

file = open('berlin.json', 'a')
#file = open('jena.json', 'a')

data = data.split('\n')

#locator is neseccary for the computing of the coordinates for every apartment
locator = Nominatim(user_agent="apartmentScraper")

#loops through every jsonline, creating a hash and check, if the current hash already exist
l = len(data)
for i in range(l - 1):
    apartment = json.loads(data[i])

    currentHash = hashlib.md5((str(apartment['date'])+str(apartment['roomnumber'])+str(apartment['surface'])+str(apartment['sidecosts'])).encode('utf-8')).digest()

    #filters all duplicates, with the hashes
    if(currentHash not in hashes):
        
        #computing the coordinates by geocoder and add it to the json
        if(apartment['street'] is not None):
            loc = apartment['street'].strip() + ' ' + apartment['town'].strip()
            location = locator.geocode(loc)

            #if the object exists, adding the coordinates to the dataset
            if(location is not None):
                apartment['latitude'] = location.latitude
                apartment['longtitude'] = location.longitude

        #writing the jsonline to the file 
        line = json.dumps(apartment) + "\n"
        file.write(line)
        hashes.add(currentHash)
    else:
        continue

file.close()

os.remove('rawdata.json')