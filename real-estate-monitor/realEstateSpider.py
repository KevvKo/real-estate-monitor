import scrapy
import json
import os
import sys
import hashlib
from geopy.geocoders import Nominatim 
import MySQLdb

from scrapy.crawler import CrawlerProcess
from scrapy.crawler import Settings
from scrapy.utils.project import get_project_settings

from spiders.wgGesuchtScraper import WggesuchtScraper
from spiders.immonetScraper import ImmonetScraper
from spiders.is24Scraper import Is24Scraper

settings = {
    'DOWNLOAD_DELAY' :3,
    'ITEM_PIPELINES':{
        'pipelines.realEstatePipeline':100,
    },
    'COOKIES_ENABLED': 'False',
    'DOWNLOADER_MIDDLEWARES': {
        'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        'scrapy_useragents.downloadermiddlewares.useragents.UserAgentsMiddleware': 500
    },
    'USER_AGENTS' : [
        ('Mozilla/5.0 (X11; Linux x86_64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/57.0.2987.110 '
        'Safari/537.36'),  # chrome
        ('Mozilla/5.0 (X11; Linux x86_64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/61.0.3163.79 '
        'Safari/537.36'),  # chrome
        ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) '
        'Gecko/20100101 '
        'Firefox/55.0'),  # firefox
        ('Mozilla/5.0 (Windows NT 6.1; rv:60.0) '
        'Gecko/20100101 Firefox/60.0') # tor
    ]
}

tn = sys.argv[1]

#scraping the raw data and provide a json, which containing the raw data included duplicates
process = CrawlerProcess(settings=settings)

# #scraping for jena
if(tn == 'jena'):
    process.crawl(WggesuchtScraper, url="https://www.wg-gesucht.de/wohnungen-in-Jena.66.2.1.0.html?offer_filter=1&city_id=66&noDeact=1&categories%5B%5D=2&rent_types%5B%5D=0", town = tn)
    process.crawl(ImmonetScraper, url="https://www.immonet.de/immobiliensuche/sel.do?&sortby=0&suchart=1&objecttype=1&marketingtype=2&parentcat=1&city=111924&locationname=Jena", town = tn)
    process.crawl(Is24Scraper, url="https://www.immobilienscout24.de/Suche/de/thueringen/jena/wohnung-mieten", town = tn)

#scraping for berlin
if(tn== 'berlin'):
    process.crawl(WggesuchtScraper, url="https://www.wg-gesucht.de/wohnungen-in-Berlin.8.2.1.0.html?offer_filter=1&city_id=8&noDeact=1&categories%5B%5D=2&rent_types%5B%5D=0", town = tn)
    process.crawl(ImmonetScraper, url="https://www.immonet.de/immobiliensuche/sel.do?&sortby=0&suchart=1&objecttype=1&marketingtype=2&parentcat=1&city=87372&locationname=Berlin", town = tn)
    process.crawl(Is24Scraper, url="https://www.immobilienscout24.de/Suche/de/berlin/berlin/wohnung-mieten?enteredFrom=result_list", town = tn)

process.start() # the script will block here until the crawling is finishedg 

#handling the database
db = MySQLdb.Connect(
    host = 'localhost',
    user= 'kevin',
    password = 'Montera93',
    database = 'apartment_monitoring'
)

cursor = db.cursor()

#opens the scraped items-file
with open ('cache.json', 'r') as cache:
   data = cache.read()

data = data.split('\n')

#locator is neseccary for the computing of the coordinates for every apartment
locator = Nominatim(user_agent="realEstateMonitor")

#loops through every jsonline, creating a hash and check, if the current hash already exist
l = len(data)

for i in range(l - 1):
    apartment = json.loads(data[i])
    
    try:
        apartment['hash'] = hashlib.md5((str(apartment['date'])+str(apartment['roomnumber'])+str(apartment['surface'])+str(apartment['sidecosts'])).encode('utf-8')).hexdigest()
        hexSQL = 'SELECT * FROM apartments_{} WHERE hash="{}"'.format( tn.lower(), apartment['hash'])
        #filters all duplicates, with the hashes
        cursor.execute(hexSQL)
    except:
        print("Keyerror")
        continue

    if(cursor.rowcount == 0):
        #computing the coordinates by geocoder and add it to the json
        ##errorhandler, if an entry has ni street-key (i.e. entry from wg-gesucht.de because the bit was detected and blocked)
        try:
            if(apartment['street'] is not None):
                loc = apartment['street'].strip() + ' ' + apartment['town'].strip()
                location = locator.geocode(loc)

                #if the object exists, adding the coordinates to the dataset
                if(location is not None):
                    apartment['latitude'] = location.latitude
                    apartment['longitude'] = location.longitude

                #adds null-values for the coordinates, if the coordinates cant be computed
                else:
                     apartment['latitude'] = None
                     apartment['longitude'] = None
            
            #adds null-values for the coordinates, if a street not exists
            else:
                apartment['latitude'] = None
                apartment['longitude'] = None
        except:
            print('keyerror detected: for ' +  json.dumps(apartment))

        #creating the query and insert the data to the databasw
        order = 'INSERT INTO apartments_{} (domain, expose, date, coldrent, roomnumber, surface, sidecosts, street, postcode, town, latitude, longitude, hash) VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'.format(tn.lower())
        values = (apartment['domain'], int(apartment['expose']), apartment['date'], apartment['coldrent'], apartment['roomnumber'], apartment['surface'], apartment['sidecosts'], apartment['street'], apartment['postcode'], apartment['town'], apartment['latitude'], apartment['longitude'], apartment['hash']) 
        
        sql = 'SELECT * FROM apartments_{} WHERE expose={} AND domain="{}"'.format(tn.lower(), apartment['expose'] , apartment['domain'])
    
        cursor.execute(sql)

        if(cursor.rowcount == 0):

            cursor.execute(order, values)
            db.commit()
        
    else:
        continue

#close the opened file and remove the cache
cache.close()
os.remove('cache.json')

    

    
