import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import Settings
from scrapy.utils.project import get_project_settings

from wggesuchtScraper import WggesuchtScraper
from immonetScraper import ImmonetScraper
from  is24Scraper import Is24Scraper

process = CrawlerProcess(settings={
    'FEED_FORMAT': 'jsonlines',
    'FEED_URI': 'apartments.json',
    'DOWNLOAD_DELAY': '0',
    'COOKIES_ENABLED' : 'False'
})

process.crawl(WggesuchtScraper, url="https://www.wg-gesucht.de/wohnungen-in-Jena.66.2.1.0.html?offer_filter=1&city_id=66&noDeact=1&categories%5B%5D=2&rent_types%5B%5D=0")
process.crawl(Is24Scraper, url="https://www.immobilienscout24.de/Suche/de/thueringen/jena/wohnung-mieten")
process.crawl(ImmonetScraper, url="https://www.immonet.de/immobiliensuche/sel.do?suchart=2&city=111924&marketingtype=2&pageoffset=1&radius=0&parentcat=1&sortby=0&listsize=26&objecttype=1&page=1")
process.start() # the script will block here until the crawling is finishedg