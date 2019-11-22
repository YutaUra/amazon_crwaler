import scrapy


class AmazonItem(scrapy.Item):
    time = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    review_num = scrapy.Field()
    description = scrapy.Field()
    shop_name = scrapy.Field()
    shop_url = scrapy.Field()
    shop_address = scrapy.Field()
    categories = scrapy.Field()
