# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class BookingHotelItem(Item):
    name = Field()
    country = Field()
    city = Field()
    postcode = Field()
    address = Field()
    description = Field()
    rating = Field()
    images = Field()
    image_urls = Field()
    checkin = Field()
    checkout = Field()
    rooms = Field()

