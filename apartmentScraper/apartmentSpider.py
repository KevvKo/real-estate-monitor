import scrapy
import json
import os
import hashlib

from scrapy.crawler import CrawlerProcess
from scrapy.crawler import Settings
from scrapy.utils.project import get_project_settings

from spiders.wggesuchtScraper import WggesuchtScraper
from spiders.immonetScraper import ImmonetScraper
from spiders.is24Scraper import Is24Scraper

settings = {
    'DOWNLOAD_DELAY' : 5,
    'ITEM_PIPELINES':{
        'pipelines.ApartmentPipeline':100,
    },
    'COOKIES_ENABLED': 'False'
    # 'FEED_FORMAT' : 'jsonlines',
    # 'FEED_URI' : 'rawdata.json'
}

#scraping the raw data and provide a json, which containing the raw data included duplicates
process = CrawlerProcess(settings=settings)

process.crawl(WggesuchtScraper, url="https://www.wg-gesucht.de/wohnungen-in-Jena.66.2.1.0.html?offer_filter=1&city_id=66&noDeact=1&categories%5B%5D=2&rent_types%5B%5D=0")
process.crawl(ImmonetScraper, url="https://www.immonet.de/immobiliensuche/sel.do?suchart=2&city=111924&marketingtype=2&pageoffset=1&radius=0&parentcat=1&sortby=0&listsize=26&objecttype=1&page=1")
process.crawl(Is24Scraper, url="https://www.immobilienscout24.de/Suche/de/thueringen/jena/wohnung-mieten")
process.start() # the script will block here until the crawling is finishedg 

#take the rawdata.json to prepare the data and remove duplicates
hashes = set()

#opens the scraped items-file
with open ('rawdata.json', 'r') as jsonfile:
    data = jsonfile.read()

file = open('apartments.json', 'a')

data = data.split('\n')
#loops through every jsonline, creating a hash and check, if the current hash already exist
l = len(data)
for i in range(l - 1):
    js = json.loads(data[i])

    currentHash = hashlib.md5((str(js['date'])+str(js['roomnumber'])+str(js['surface'])+str(js['sidecosts'])).encode('utf-8')).digest()

    #filters all duplicates, with the hashes
    if(currentHash not in hashes):
        line = json.dumps(js) + "\n"
        file.write(line)
        hashes.add(currentHash)
    else:
        continue

file.close()

os.remove('rawdata.json')