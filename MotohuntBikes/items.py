# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MotohuntbikesItem(scrapy.Item):
    # define the fields for your item here like:
    vin                 = scrapy.Field()
    make                = scrapy.Field()
    model               = scrapy.Field()
    trim                = scrapy.Field()
    year                = scrapy.Field()
    price               = scrapy.Field()
    condition           = scrapy.Field()
    dealer              = scrapy.Field()
    dealer_link         = scrapy.Field()
    dealer_number       = scrapy.Field()
    description         = scrapy.Field()
    mileage             = scrapy.Field()
    color               = scrapy.Field()
    location            = scrapy.Field()
    engine              = scrapy.Field()
    fuel_type           = scrapy.Field()
    body_type           = scrapy.Field()
    car_url             = scrapy.Field()
    image_links         = scrapy.Field()

class RockAutoItem(scrapy.Item):
    # define the fields for your item here like:
    make    = scrapy.Field()
    year    = scrapy.Field()
    model   = scrapy.Field()
    engine  = scrapy.Field()
    part_type       = scrapy.Field()
    part_sub_type   = scrapy.Field()

    price       = scrapy.Field()
    part_images = scrapy.Field()
    part_manufacturer   = scrapy.Field()
    part_number = scrapy.Field()
    part_url    = scrapy.Field()
    part_name   = scrapy.Field()
