# -*- coding: utf-8 -*-
#Author: Kevin Klein
#this spider crawls through www.immobilienscout24.de and scraping all data from 
#every single apartment with scrapy 
import scrapy
from datetime import datetime

class Is24Scraper(scrapy.Spider):
    name="is24"
    def __init__(self, url=None, *args, **kwargs):
        super(Is24Scraper, self).__init__(*args, **kwargs)
        self.start_urls = [url]
 
    #parses the requested urls als crawling through every single apartment
    def parse(self, response):

        #get the number of pages with search results
        pages = len(response.css("#pageSelection option"))
        
        pageN = 1
        
        #loop through the pages and parsing the expose-ids
        while(pageN <= pages):
            yield scrapy.Request(url="https://www.immobilienscout24.de/Suche/de/thueringen/jena/wohnung-mieten?pagenumber={}".format(str(pageN)),callback=self.parse_expose_id)
            pageN +=1
    
    #parsing all expose-ids from the pageresult
    def parse_expose_id(self, response):
        exposes = scrapy.Field()

        #get all links from the current page
        links = response.css("a")
            
        #loops through every url, and checks if the beginning from the url is an expose

        for link in links:

            #css-selectors to extract the url and the exposeRefferer (if the link is from the search)
            href = link.css("::attr(href)").extract()[0][1:7]

            #adds the expose to the set if it is a result from the search            
            if(href == "expose"):

                #if the current href is an expose check the expose-refferer 
                exposeReferrer = link.css("::attr(data-go-to-expose-referrer)").extract()[0]
                if(exposeReferrer == "RESULT_LIST_LISTING"):
                    exposes[link.css("::attr(href)").extract()[0][8:]] = link.css("::attr(href)").extract()[0]

        for expose in exposes:
            yield response.follow(url = 'https://www.immobilienscout24.de{}'.format(exposes[expose]), callback = self.parse_expose, cb_kwargs = dict(expose_id = expose))
            
    #parses the necessary informations from every requestes expose
    def parse_expose(self, response, expose_id):
        apartment = scrapy.Field()

        apartment['domain'] = response.url.split('/')[2]
        apartment['date'] = datetime.today().strftime('%Y-%m-%d')
        apartment['expose'] = expose_id
        apartment['coldrent'] = response.css('div.is24qa-kaltmiete.is24-value.font-semibold.is24-preis-value ::text').get().split()[0].strip(),
        apartment['roomnumber'] = response.css('div.is24qa-zi.is24-value.font-semibold ::text').get().strip(),
        apartment['surface'] = response.css('div.is24qa-flaeche.is24-value.font-semibold ::text').get().split()[0].strip(),
        apartment[ 'sidecosts'] = response.css('dd.is24qa-nebenkosten.grid-item.three-fifths::text').getall()[1].split()[0].strip()
        yield apartment