# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime

class WggesuchtScraper(scrapy.Spider):
    name = 'wggesucht'

    #constructor of immoWeltSpider
    def __init__(self, url=None, *args, **kwargs):
        super(WggesuchtScraper, self).__init__(*args, **kwargs)
        self.start_urls = [url]

    #scraping the next url with searchresults
    def parse(self, response):

        #catches all exposes from the current page
        exposes = response.css('div.wgg_card.offer_list_item div.col-sm-4.card_image a::attr(href)').getall()

        #loops through every founded expose and starting a request
        for expose in exposes:
          yield scrapy.Request('https://www.wg-gesucht.de/{}'.format(expose), callback = self.parse_apartment_data)

        nextPage = response.css('ul.pagination.pagination-sm a::attr(href)').getall()

        #checks, if the requested page is working
        if(len(nextPage)>0):
            nextPage = nextPage[-1]

            if(nextPage is not ''):
                yield scrapy.Request('https://www.wg-gesucht.de/{}'.format(nextPage), callback=self.parse)
        else:
            print(response.status)

    #scraping all informations from the current apartment and store them into  an item
    def parse_apartment_data(self, response):
 
        apartment = scrapy.Field()
        apartment['domain'] = response.url.split('/')[2]
        apartment['date'] = datetime.today().strftime('%Y-%m-%d')
        apartment['expose'] = response.url.split('.')[3]
        
        #prepare the field coldrent
        coldrent = response.css('td.col-xs-6.col-sm-4.print_text_left b::text').get()
        if(coldrent):
            apartment['coldrent'] = coldrent.split('\u20ac')[0].strip()
        else:
            apartment['coldrent'] = None

        #prepare the field roomnumber
        roomnumber = response.css('div#rent_wrapper div.basic_facts_bottom_part label.amount ::text').get()
        if(roomnumber):
            apartment['roomnumber'] = roomnumber.strip()
        else:
            apartment['roomnumber'] = None

        #prepare the field roomnumber
        surface = response.css('div#rent_wrapper div.basic_facts_top_part label.amount ::text').get()
        if(roomnumber):
            apartment['surface'] = surface.split('\u00b2')[0].strip()
        else:
            apartment['surface'] = None

        #prepare the field sidecosts
        sidecosts = response.css('div#graph_wrapper div#utilities_costs label.graph_amount ::text').get()
        if(sidecosts):
            sidecosts = sidecosts.strip()
            if(sidecosts is  not 'n.a.'):
                 apartment['sidecosts'] = sidecosts.split('\u20ac')[0].strip()
        else: apartment['sidecosts'] = None

        return apartment