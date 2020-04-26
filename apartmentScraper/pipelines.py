# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import hashlib
from scrapy.exceptions import DropItem

class ApartmentPipeline(object):

    # def process_item(self, item, spider):

    #     line = json.dumps(dict(item)) + "\n"
    #     self.file.write(line)
    #     return item
    def open_spider(self, spider):
        self.file = open('rawdata.json', 'a')

    def close_spider(self, spider):
        self.file.close()


    def process_item(self, item, spider):

        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
