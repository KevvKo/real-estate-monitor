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
    'DOWNLOAD_DELAY' :0,
    'ITEM_PIPELINES':{
        'pipelines.ApartmentPipeline':100,
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

#scraping the raw data and provide a json, which containing the raw data included duplicates
process = CrawlerProcess(settings=settings)

#scraping for jena
# process.crawl(WggesuchtScraper, url="https://www.wg-gesucht.de/wohnungen-in-Jena.66.2.1.0.html?offer_filter=1&city_id=66&noDeact=1&categories%5B%5D=2&rent_types%5B%5D=0")
# process.crawl(ImmonetScraper, url="https://www.immonet.de/immobiliensuche/sel.do?&sortby=0&suchart=1&objecttype=1&marketingtype=2&parentcat=1&city=111924&locationname=Jena")
# process.crawl(Is24Scraper, url="https://www.immobilienscout24.de/Suche/de/thueringen/jena/wohnung-mieten")

# #scraping for berlin
# process.crawl(WggesuchtScraper, url="https://www.wg-gesucht.de/wohnungen-in-Berlin.8.2.1.0.html")
# process.crawl(ImmonetScraper, url="https://www.immonet.de/immobiliensuche/sel.do?&sortby=0&suchart=1&objecttype=1&marketingtype=2&parentcat=1&city=87372&locationname=Berlin")
# process.crawl(Is24Scraper, url="https://www.immobilienscout24.de/Suche/de/berlin/berlin/wohnung-mieten?enteredFrom=result_list")

# #scraping for dresden
# process.crawl(WggesuchtScraper, url="https://www.wg-gesucht.de/wohnungen-in-Dresden.27.2.1.0.html")
# process.crawl(ImmonetScraper, url="https://www.immonet.de/immobiliensuche/sel.do?pageoffset=1&listsize=26&objecttype=1&locationname=Dresden&acid=&actype=&city=100051&ajaxIsRadiusActive=true&sortby=0&suchart=2&radius=0&pcatmtypes=1_2&pCatMTypeStoragefield=&parentcat=1&marketingtype=2&fromprice=&toprice=&fromarea=&toarea=&fromplotarea=&toplotarea=&fromrooms=&torooms=&objectcat=-1&wbs=-1&fromyear=&toyear=&fulltext=&absenden=Ergebnisse+anzeigen")
# process.crawl(Is24Scraper, url="https://www.immobilienscout24.de/Suche/de/sachsen/dresden/wohnung-mieten?enteredFrom=result_list")

process.start() # the script will block here until the crawling is finishedg 

# #take the rawdata.json to prepare the data and remove duplicates
hashes = set()

#opens the scraped items-file
with open ('rawdata.json', 'r') as jsonfile:
    data = jsonfile.read()

#file = open('berlin.json', 'a')
file = open('jena.json', 'a')
#file = open('dresden.json', 'a')
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
        ##errorhandler, if an entry has ni street-key (i.e. entry from wg-gesucht.de because the bit was detected and blocked)
        try:
            if(apartment['street'] is not None):
                loc = apartment['street'].strip() + ' ' + apartment['town'].strip()
                location = locator.geocode(loc)

                #if the object exists, adding the coordinates to the dataset
                if(location is not None):
                    apartment['latitude'] = location.latitude
                    apartment['longtitude'] = location.longitude
        except:
            print('keyerror detected: for ' +  json.dumps(apartment))
        #writing the jsonline to the file 
        line = json.dumps(apartment) + "\n"
        file.write(line)
        hashes.add(currentHash)
    else:
        continue

file.close()

os.remove('rawdata.json')