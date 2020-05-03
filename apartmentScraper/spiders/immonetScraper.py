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

        #scraping the count of pages with results
        townValue = response.css('input#locationname ::attr(value)').get()

        pages = int(response.css('a.padding-left-15.paddint-left-sm-12.padding-right-15.padding-right-sm-12.v-line-shadow.v-line-shadow-l::text').getall()[-1])
        pageN = 1

        #requesting further pages with results
        while(pageN <= pages):
            yield scrapy.Request(response.url + '&page={}'.format(pageN), callback=self.parse_apartment, cb_kwargs = dict(town = townValue))
            pageN += 1

    #scraping all exposes from the current page
    def parse_apartment(self,response, town):
        exposes = response.css('a.flex-grow-1.display-flex ::attr(href)').getall()
        
        #requesting for every expose from the results the apartmentside
        for expose in exposes:
           yield scrapy.Request('https://www.immonet.de{}'.format(expose), callback = self.parse_apartment_data, cb_kwargs = dict(town = town))

    #scraping all informations from the current apartment and store them into  an item
    def parse_apartment_data(self, response, town):
        adress = response.css('p.text-100.pull-left::text').getall()
        if(len(adress)> 0):
            if(town in adress[0] or town in adress[1]):
                
                apartment = scrapy.Field()

                apartment['domain'] = response.url.split('/')[2]
                apartment['date'] = datetime.today().strftime('%Y-%m-%d')

                apartment['expose'] = response.url.split('/')[4]
                
                #prepare the field coldrent
                coldrent = response.css('div#priceid_2::text').get()
                if(coldrent):
                    coldrent = coldrent.replace('\u00a0\u20ac', '').replace('\t', '').replace('\n', '')
                    if('.' in coldrent): 
                        coldrent = coldrent.replace(',', '')
                        apartment['coldrent'] = coldrent.replace('.', ',')
                    else:
                        apartment['coldrent'] = coldrent.replace(',', '') + ',00'
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
                if(surface):
                    surface = surface.replace('\u00a0m\u00b2', '')
                    if('.' in surface):
                        apartment['surface'] = surface.replace('.', ',').strip()
                    else:
                        apartment['surface'] = surface.strip() + ',00'
                else:
                    apartment['surface'] = None

                #prepare the field sidecosts
                sidecosts = response.css('div#priceid_20::text').get()
                if(sidecosts):
                    if('.' in sidecosts):
                        apartment['sidecosts'] = sidecosts.replace('.', ',').replace('\u00a0\u20ac', '').replace('\t', '').replace('\n', '').strip()
                    else: 
                        apartment['sidecosts'] = sidecosts.replace('.', ',').replace('\u00a0\u20ac', '').replace('\t', '').replace('\n', '').strip() + ',00'
                else:
                    apartment['sidecosts'] = None

                #prepare the adress fields
                adressRaw = response.css('p.text-100.pull-left ::text').getall()
                if(adress):
                    
                    adress = ''.join(adressRaw).replace('\t', '').replace('Auf Karte anzeigen', '').split('\u00a0')

                    #prepare the street field
                    street = adress[0].split('\n')[1]

                    if(street is not ""):
                        apartment['street'] = street
                    else:
                        apartment['street'] = None      

                    #prepare the postcode field
                    postcode = adress[0].split('\n')[-1]
                    if(postcode is not ""):
                        apartment['postcode'] = postcode
                    else:
                        apartment['postcode'] = None

                    #prepare the town field
                    apartment['town'] = adress[-1].replace('\n', '')

                return apartment
