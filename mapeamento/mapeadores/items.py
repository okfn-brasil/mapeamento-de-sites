# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MapeamentoItem(scrapy.Item):
    territory_id = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    pattern = scrapy.Field()
    url = scrapy.Field()    
    date_from = scrapy.Field()
    date_to = scrapy.Field()
    status = scrapy.Field()
