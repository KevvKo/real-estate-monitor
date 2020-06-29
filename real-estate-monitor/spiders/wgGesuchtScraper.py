# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import MySQLdb

class WggesuchtScraper(scrapy.Spider):
    name = 'wggesucht'

    #constructor of immoWeltSpider
    def __init__(self, url=None,town = None, *args, **kwargs):
        super(WggesuchtScraper, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.town = town.lower()
        self.db = MySQLdb.Connect(
            host = #specify host,
            user= #specifiy user,
            password = #specifiy password,
            database = #specifiy database,
        )

        self.cursor = self.db.cursor()
    #scraping the next url with searchresults
    def parse(self, response):

        #catches all exposes from the current page
        exposes = response.css('div.wgg_card.offer_list_item div.col-sm-4.card_image a::attr(href)').getall()

        #loops through every founded expose and starting a request
        for i in range(len(exposes)):
            
            #sql-query to check, if an aoartment is already in the database
            sql = 'SELECT * FROM apartments_{} WHERE expose={} and domain="www.wg-gesucht.de"'.format( self.town, exposes[i].split('.')[1])
            self.cursor.execute(sql)

            if(self.cursor.rowcount == 0 ):

                yield scrapy.Request('https://www.wg-gesucht.de/{}'.format(exposes[i]), callback = self.parse_apartment_data)
            else:
                print('record exists')
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
        coldrent = response.css('div#rent label.graph_amount ::text').get()
        if(coldrent):
            apartment['coldrent'] = float(coldrent.replace('\u20ac', '').strip() + '.00')
        else:
            apartment['coldrent'] = None

        #prepare the field roomnumber
        roomnumber = response.css('div#rent_wrapper div.basic_facts_bottom_part label.amount ::text').get()
        if(roomnumber):
            apartment['roomnumber'] = float(roomnumber.strip().replace(',', '.'))
        else:
            apartment['roomnumber'] = None

        #prepare the field roomnumber
        surface = response.css('div#rent_wrapper div.basic_facts_top_part label.amount ::text').get()
        if(roomnumber):
            apartment['surface'] = float(surface.replace('\u00b2', '').strip().split('m')[0] +'.00')
        else:
            apartment['surface'] = None

        #prepare the field sidecosts
        sidecosts = response.css('div#graph_wrapper div#utilities_costs label.graph_amount ::text').get()
        if(sidecosts):
            sidecosts = sidecosts.replace('\u20ac', '').strip()
            if(sidecosts == 'n.a.'):
                apartment['sidecosts'] = None
            else:
                apartment['sidecosts'] = float(sidecosts  + '.00')
                
        else: apartment['sidecosts'] = None

        #prepare the adressfileds
        adress = response.css('div.col-sm-4.mb10 a ::text').getall()

        if(adress):
        
            #prepare the street field
            street = adress[0].replace('\n', '').strip()

            if(street is not ""):
                apartment['street'] = street
            else:
                apartment['street'] = None      

            #prepare the postcode and town field
            townAdress = adress[1]
            if(townAdress is not ""):
                townAdress = townAdress.replace('\n', '').strip().split(' ')

                #some entrys have no valid postcode as scraped info. 
                #this occures, through blocking and captchuring from the website. 
                try:
                    apartment['postcode'] = townAdress[0]
                except:
                    apartment['postcode'] = None
                apartment['town'] = townAdress[1]
                
            else:
                apartment['postcode'] = None
                apartment['town'] = self.town

        return apartment
