# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime

class ImmonetScraper(scrapy.Spider):
    name = 'immonet'

    #constructor of immoWeltSpider
    def __init__(self, url=None, *args, **kwargs):
        super(ImmonetScraper, self).__init__(*args, **kwargs)
        self.start_urls = [url]

    #scraping the next url with searchresults
    def parse(self, response):

        #requesting the first page with results
        yield scrapy.Request(response.url, callback=self.parse_apartment)
        pageResults = response.css('ul.tbl.margin-auto.margin-top-0.margin-bottom-0.padding-0 a::attr(href)').getall()

        #requesting further pages with results
        for page in pageResults:
            yield scrapy.Request('https://www.immonet.de{}'.format(page), callback=self.parse_apartment)

    #scraping all exposes from the current page
    def parse_apartment(self,response):
        exposes = response.css('a.flex-grow-1.display-flex ::attr(href)').getall()
        
        #requesting for every expose from the results the apartmentside
        for expose in exposes:
           yield scrapy.Request('https://www.immonet.de{}'.format(expose), callback = self.parse_apartment_data)

    #scraping all informations from the current apartment and store them into  an item
    def parse_apartment_data(self, response):
        adress = response.css('p.text-100.pull-left::text').getall()
        
        if('Jena' in adress[0] or 'Jena' in adress[1]):
        
            apartment = scrapy.Field()
            apartment['domain'] = response.url.split('/')[2]
            apartment['date'] = datetime.today().strftime('%Y-%m-%d')
            apartment['expose'] = response.url.split('/')[4]
            
            #prepare the field coldrent
            coldrent = response.css('div#priceid_2::text').get()
            if(coldrent):
                apartment['coldrent'] = coldrent.strip().split('.')[0]
            else:
                apartment['coldrent'] = None

            #prepare the field roomnumber
            roomnumber = response.css('span#kfroomsValue::text').get()
            if(roomnumber):
                apartment['roomnumber'] = roomnumber.strip()
            else:
                apartment['roomnumber'] = None

            #prepare the field roomnumber
            surface = response.css('span#kffirstareaValue::text').get()
            if(roomnumber):
                apartment['surface'] = surface.split()[0]
            else:
                apartment['surface'] = None

            #prepare the field sidecosts
            sidecosts = response.css('div#priceid_20::text').get()
            if(sidecosts):
                apartment['sidecosts'] = sidecosts.split()[0]
            else:
                apartment['sidecosts'] = None

            return apartment