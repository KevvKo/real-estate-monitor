# -*- coding: utf-8 -*-
#Author: Kevin Klein
#this spider crawls through www.immobilienscout24.de and scraping all data from 
#every single apartment with scrapy 
import scrapy, MySQLdb
from datetime import datetime

class Is24Scraper(scrapy.Spider):
    name="is24"
    def __init__(self, url=None, town = None, *args, **kwargs):
        super(Is24Scraper, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.town = town
        self.db = MySQLdb.Connect(
            host = 'localhost',
            user= 'kevin',
            password = 'Montera93',
            database = 'apartment_monitoring'
        )

        self.cursor = self.db.cursor()
 
    #parses the requested urls als crawling through every single apartment
    def parse(self, response):

        #get the number of pages with search results
        pages = len(response.css("#pageSelection option"))
        
        pageN = 1
        town = response.url.split('/')[6]
        land = response.url.split('/')[5]
        #loop through the pages and parsing the expose-ids
        while(pageN <= pages):

            yield scrapy.Request(url="https://www.immobilienscout24.de/Suche/de/{}/{}/wohnung-mieten?pagenumber={}".format(land,town ,str(pageN)),callback=self.parse_expose_id, cb_kwargs = dict(town  = town))
            pageN +=1
    
    #parsing all expose-ids from the pageresult
    def parse_expose_id(self, response, town):
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
                exposeReferrer = link.css("::attr(data-go-to-expose-referrer)").extract()
                if(len(exposeReferrer) > 0):

                    if(exposeReferrer[0] == "RESULT_LIST_LISTING"):
                        exposes[link.css("::attr(href)").extract()[0][8:]] = link.css("::attr(href)").extract()[0]

        for expose in exposes:
            sql = 'SELECT * FROM apartments_{} WHERE expose={} and domain="www.immobilienscout24.de"'.format( self.town, expose)
            self.cursor.execute(sql)
  
            if(self.cursor.rowcount == 0 ):
                yield response.follow(url = 'https://www.immobilienscout24.de{}'.format(exposes[expose]), callback = self.parse_expose, cb_kwargs = dict(expose_id = expose))
            
    #parses the necessary informations from every requestes expose
    def parse_expose(self, response, expose_id):
        apartment = scrapy.Field()
        
        apartment['domain'] = response.url.split('/')[2]
        apartment['date'] = datetime.today().strftime('%Y-%m-%d')
        apartment['expose'] = expose_id

        #prepare the coldrent-entry
        coldrent = response.css('div.is24qa-kaltmiete.is24-value.font-semibold.is24-preis-value::text').get().split(' ')[1]
        if('.' in coldrent):
            coldrent = coldrent.replace('.', '')

        apartment['coldrent'] = float(coldrent.replace(',', '.'))

        #prepare the roomnumber-data
        roomnumber = response.css('dd.is24qa-zimmer.grid-item.three-fifths::text').get().split(' ')[1]

        if(',' in roomnumber): apartment['roomnumber'] = float(roomnumber.replace(',', '.'))
        else: apartment['roomnumber'] = float(roomnumber)

        #prepare the surface-entry
        surface = response.css('div.is24qa-flaeche.is24-value.font-semibold::text').get().split(' ')[1]
        if(',' not in surface):
            surface += '.00'
        else:
            surface = surface.replace(',', '.')
        apartment['surface'] = float(surface)

        #prepare the sidecosts-entry
        sidecosts = response.css('dd.is24qa-nebenkosten.grid-item.three-fifths::text').getall()[1].split()[0]

        #checkks if the sidecosts can be prepared
        if('keine' in sidecosts):
             apartment[ 'sidecosts'] = None  

        #continues the treatning
        else:
            if(sidecosts != '0'):
                sidecosts = sidecosts.replace(',', '')
                if('.' not in sidecosts):
                    sidecosts += '.00'
                apartment[ 'sidecosts'] = float(sidecosts)
            else:
                apartment[ 'sidecosts'] = None  

        #prepare the street field
        street = response.css('span.block.font-nowrap.print-hide ::text').get()
        if(street is not ""):
            try:
                apartment['street'] = street.replace(',', '').strip()
            except:
                apartment['street'] = street
        else:
            apartment['street'] = None

        #prepare the postcode-field
        postcode = response.css('span.zip-region-and-country ::text').get()
        if(postcode is not ""):
            apartment['postcode'] = postcode.split(' ')[0]
        else:
            apartment['postcode'] = None

        #prepare the town field
        apartment['town'] = self.town
        return apartment
