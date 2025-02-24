# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LinkedinScraperItem(scrapy.Item):
    name = scrapy.Field()
    headline = scrapy.Field()
    location = scrapy.Field()
    profile_url = scrapy.Field()
