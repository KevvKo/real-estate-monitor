import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import Settings
from scrapy.utils.project import get_project_settings

from spiders.wggesuchtScraper import WggesuchtScraper
from spiders.immonetScraper import ImmonetScraper
from spiders.is24Scraper import Is24Scraper

settings = {
    # 'FEED_FORMAT': 'jsonlines',
    # 'FEED_URI': 'items.json',
    # 'FEED_EXPORTERS': {
    #     'jsonlines': 'pipelines.ApartmentPipeline'
    # }
    'ITEM_PIPELINES':{
        'pipelines.ApartmentPipeline':800,
    }
}

process = CrawlerProcess(settings=settings)

process.crawl(WggesuchtScraper, url="https://www.wg-gesucht.de/wohnungen-in-Jena.66.2.1.0.html?offer_filter=1&city_id=66&noDeact=1&categories%5B%5D=2&rent_types%5B%5D=0")
process.crawl(ImmonetScraper, url="https://www.immonet.de/immobiliensuche/sel.do?suchart=2&city=111924&marketingtype=2&pageoffset=1&radius=0&parentcat=1&sortby=0&listsize=26&objecttype=1&page=1")
process.crawl(Is24Scraper, url="https://www.immobilienscout24.de/Suche/de/thueringen/jena/wohnung-mieten")
process.start() # the script will block here until the crawling is finishedg 