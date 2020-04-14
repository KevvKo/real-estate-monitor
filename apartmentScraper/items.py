# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class Apartment(scrapy.Item):
    expose = scrapy.Field()
    coldrent = scrapy.Field()
    roomnumber = scrapy.Field()
    surface = scrapy.Field()
    sidecosts = scrapy.Field()
