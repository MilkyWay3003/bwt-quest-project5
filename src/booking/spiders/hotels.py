import json
import re
import os
import errno
import scrapy
import logging
import urllib.request
from scrapy.utils.log import configure_logging
from ..items import BookingHotelItem
from ..database import Database


class HotelsSpider(scrapy.Spider):
    name = 'hotels'

    allowed_domains = [
        'www.booking.com',
    ]

    search_params = {}

    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )

    def __init__(self, params):
        self.database = Database().get_instance()
        if params:
            self.search_params = params

    def construct_url_params(self, separator='&'):
        params = zip(self.search_params.keys(), self.search_params.values())
        params = ['='.join(pair) for pair in params]
        params = separator.join(params)
        return params

    def start_requests(self):

        base_url = 'https://www.booking.com/searchresults.ru.html?'

        params = self.construct_url_params()

        return [
            scrapy.Request(base_url + params)
        ]

    # get the hotel pages
    def parse(self, response):
        self.logger.info('City %s', response.url)

        hotel_links = response.xpath('//a[@class="hotel_name_link url"]/@href')

        for hotel_link in hotel_links:
            link = hotel_link.extract()
            link = link.split('?')[0]
            link = link.strip()
            link = response.urljoin(link)
            self.logger.info('Hotel pages %s', hotel_link.extract())

            params = self.construct_url_params(separator=';')
            link = link + '?' + params

            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Host": "www.booking.com",
                "Pragma": "no-cache",
                "referer": link,
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/68.0.3440.106 Chrome/68.0.3440.106 Safari/537.36"
            }

            yield scrapy.Request(link, headers=headers, callback=self.parse_hotel_info)

        next_page = response.xpath('//a[contains(@class, "bui-pagination__link paging-next")]/@href')
        if next_page is not None:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse)

    # get the hotels info
    def parse_hotel_info(self, response):
        item = BookingHotelItem()

        item['name'] = self.parse_hotel_name(response)

        address = self.parse_hotel_address(response)

        if address:
            item['country'] = address['addressCountry']
            item['city'] = address['addressRegion']
            item['postcode'] = address['postalCode']
            item['address'] = address['addressLocality']
        else:
            item['country'] = "No country"
            item['city'] = "No city"
            item['postcode'] = "No postcode"
            item['address'] = "No address"

        item['description'] = self.parse_hotel_description(response)

        rating = self.parse_hotel_rating(response)
        if rating:
            item['rating'] = rating
        else:
            item['rating'] = None

        item['images'] = self.parse_hotel_images(response)
        item['image_urls'] = [item['images']]

        item['checkin'] = '-'.join([
            self.search_params['checkin_year'],
            self.search_params['checkin_month'],
            self.search_params['checkin_monthday']
        ])
        item['checkout'] = '-'.join([
            self.search_params['checkout_year'],
            self.search_params['checkout_month'],
            self.search_params['checkout_monthday']
        ])

        room_items = self.parse_rooms_info(self, response)
        # print(room_items)
        item['rooms'] = room_items
        yield item

    # get the rooms info
    @staticmethod
    def parse_rooms_info(self, response):
        rooms = []

        pattern = re.compile("b_rooms_available_and_soldout\s*:\s*.*,")
        s = response.xpath('//script[contains(text(), "env : {")]/text()').re(pattern)[0]
        p = re.compile(r"b_rooms_available_and_soldout\s*:\s*(.*),")
        data = p.match(s).group(1)
        data = json.loads(data)

        for room_data in data:
            room = dict()
            room['name'] = room_data['b_name']
            room_id = str(room_data['b_id'])  # booking inner room id

            prices = []
            # room price from json
            for block in room_data['b_blocks']:
                price = dict()
                price_str = block.get('b_price', None)
                if price_str is not None:
                    prc = price_str.split('\xa0')
                    price['cost'] = float(prc[1].replace(' ', '').replace(',', '.'))
                    price['currency'] = prc[0]
                else:
                    continue

                # room conditions of cancel from json
                cancel_str = block.get('b_cancellation_type', None)
                if cancel_str is not None:
                    cancel = cancel_str.split(' ')
                    price['cancel'] = ''.join(cancel)
                else:
                    price['cancel'] = None

                # room max_persons from json
                persons = block.get('b_max_persons', None)
                if persons is not None:
                    price['persons'] = persons
                else:
                    price['persons'] = None

                # room include type of meal from json
                meal_str = block.get('b_mealplan_included_name', None)
                if meal_str is not None:
                    meal = meal_str.split(' ')
                    price['meal'] = ''.join(meal)
                else:
                    price['meal'] = None

                prices.append(price)

            # TODO: remake room model schema and add benefits
            # print(prices)
            if prices:
                room['prices'] = prices
            else:
                break

            description_room = self.parse_complex_room_description(response, room_id)
            if description_room:
                room['description'] = description_room
            else:
                room['description'] = "No description"

            services_room = self.parse_complex_room_services(response, room_id)
            if services_room:
                room['services'] = services_room
            else:
                room['services'] = "No services"

            image_room = self.parse_complex_room_images(response, room_id)
            if image_room:
                file_path = "images/rooms/"
                directory = os.path.dirname(file_path)
                try:
                    os.makedirs(directory)
                except OSError as exception:
                    if exception.errno != errno.EEXIST:
                        raise
                image_room_path = "images/rooms/" + room_id + ".jpg"
                urllib.request.urlretrieve(image_room, image_room_path)
                room['images'] = image_room_path
            else:
                room['images'] = "No image"

            rooms.append(room)

        return rooms

    @staticmethod
    def parse_complex_room_description(response, room_id):
        bath = response.xpath(
            '//div[@id="blocktoggleRD' + room_id + '"]'
            '//span[@data-name-en="Bathroom"]'
            '/text()'
        ).extract()

        bath = [line.strip() for line in bath]
        bath = ' '.join(bath)

        room_size = response.xpath(
            '//div[@id="blocktoggleRD' + room_id + '"]'
            '//div[@class="info"]'
            '//text()'
        ).extract()

        room_size = [line.strip() for line in room_size]
        room_size = ' '.join(room_size)

        desc = response.xpath(
            '//div[@id="blocktoggleRD' + room_id + '"]'
            '//p'
            '/text()'
        ).extract()

        desc = [line.strip() for line in desc]
        desc = ' '.join(desc)  # TODO check desc

        description = bath + room_size + desc

        return description

    @staticmethod
    def parse_complex_room_services(response, room_id):

        services = response.xpath(
            '//div[@id="blocktoggleRD' + room_id + '"]'
                                                   '//li'
                                                   '//text()'
        ).extract()

        services = [line.strip().replace(' \n', ' ') for line in services]
        services = ' '.join(services)

        return services

    @staticmethod
    def parse_complex_room_images(response, room_id):
        image = response.xpath(
            '//div[@id="blocktoggleRD' + room_id + '"]'
            '//img'
            '/@data-lazy'
        ).extract_first()

        return image

    @staticmethod
    def parse_simple_room_type(response):
        return response.xpath(
            '//td[@class="ftd"]'
        ).extract()

    @staticmethod
    def parse_hotel_name(response):
        return response.xpath(
            'normalize-space(//*[@id="hp_hotel_name"]'
            '/text())'
        ).extract_first()

    @staticmethod
    def parse_hotel_address(response):
        address = response.xpath('//script[contains(text(), "addressLocality")] //text()').extract_first()
        address = json.loads(address)
        dict = address['address']
        return dict

    @staticmethod
    def parse_hotel_description(response):
        result = response.xpath(
            '//div[@class="hotel_description_wrapper_exp hp-description"]'
            '//p'
            '/text()'
        ).extract()

        result = [line.strip() for line in result]
        result = '\n'.join(result)
        return result

    @staticmethod
    def parse_hotel_rating(response):
        rating = response.xpath(
            'normalize-space(//span[@class="review-score-badge"]'
            '/text())'
        ).extract()

        rating = [i for i in rating]
        rating = ''.join(rating)
        rating = rating.replace(',', '.')
        if rating:
            rating = float(rating)
        else:
            rating = None
        return rating

    @staticmethod
    def parse_hotel_images(response):
        result = response.xpath(
            '//div[@id="photos_distinct"]'
            '/a'
            '/@href'
        ).extract_first()

        if result is None:
            result = response.xpath(
                '//div[@class="bh-photo-grid-thumbs bh-photo-grid-thumbs-s-full"]'
                '//a'
                '/@href'
            ).extract_first()

        return result
