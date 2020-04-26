# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import hashlib
from scrapy.exceptions import DropItem

class ApartmentPipeline(object):

    # def open_spider(self, spider):
    #     self.file = open('items.json', 'a')

    def close_spider(self, spider):
        self.file.close()

    # def process_item(self, item, spider):

    #     line = json.dumps(dict(item)) + "\n"
    #     self.file.write(line)
    #     return item
    def __init__(self):
        self.hashes = set()
        self.file = open('items.json', 'a')

    def process_item(self, item, spider):
        currentHash = hashlib.md5((str(item['coldrent']) + str(item['surface']) + str(item['roomnumber']) + str(item['sidecosts'])).encode('utf-8'))
        if currentHash.digest() in self.hashes:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.hashes.add(currentHash.digest())
            line = json.dumps(dict(item)) + "\n"
            self.file.write(line)
            return item
