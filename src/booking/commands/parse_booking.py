from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerProcess
from ..spiders.hotels import HotelsSpider
from scrapy.utils.project import get_project_settings
import os
import logging
from datetime import date, timedelta, datetime


class ParseBookingCommand(ScrapyCommand):
    def syntax(self):
        return "[options]"

    def short_desc(self):
        return "Parse Booking.com website"

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option("--city", dest="city",
                          help="City code. Must be an integer, according to internal Booking.com id for location")
        parser.add_option("--checkin", dest="checkin",
                          help="Checkin date in ISO (YYYY-MM-DD) format")
        parser.add_option("--checkout", dest="checkout",
                          help="Checkout date in ISO (YYYY-MM-DD) format")
        parser.add_option("-p", "--proxy", dest="proxy", default=False, action='store_true',
                          help="Use proxy servers")
        parser.add_option("--cr", dest="concurrent_requests", default=16,
                          help="Use maximum concurrent requests (default: 16)")
        parser.add_option("--crpd", dest="concurrent_requests_per_domain", default=16,
                          help="Use concurrent requests per domain (default: 16)")
        parser.add_option("--crpip", dest="concurrent_requests_per_ip", default=16,
                          help="Use concurrent requests per ip (default: 16)")

    def run(self, args, opts):
        search_params = dict()

        if opts.city:
            try:
                city = int(opts.city)
                search_params['city'] = str(city)
            except ValueError:
                logging.error('Invalid city ID format')
        else:
            logging.error('Specify city ID')
            return

        if opts.checkin:
            try:
                checkin = opts.checkin
                datetime.strptime(checkin, "%Y-%m-%d")
            except ValueError:
                logging.error('Invalid checkin date. Specify checkin in ISO (YYYY-MM-DD) format')
                return
        else:
            logging.warning('Checkin date not specified, using tomorrow')
            checkin = date.today() + timedelta(days=1)
            checkin = checkin.isoformat()
        search_params['checkin_monthday'] = checkin.split('-')[2]
        search_params['checkin_month'] = checkin.split('-')[1]
        search_params['checkin_year'] = checkin.split('-')[0]

        if opts.checkout:
            try:
                checkout = opts.checkout
                datetime.strptime(checkout, "%Y-%m-%d")

                chkin = datetime.strptime(checkin, "%Y-%m-%d").date()
                chkout = datetime.strptime(checkout, "%Y-%m-%d").date()
                if chkout < chkin:
                    logging.error('Checkout date must be greater than checkin date')
                    return
            except ValueError:
                logging.error('Invalid checkout date. Specify checkout in ISO (YYYY-MM-DD) format')
                return
        else:
            logging.warning('Checkin date not specified, using day after checkin')
            checkout = datetime.strptime(checkin, "%Y-%m-%d").date() + timedelta(days=1)
            checkout = checkout.isoformat()
        search_params['checkout_monthday'] = checkout.split('-')[2]
        search_params['checkout_month'] = checkout.split('-')[1]
        search_params['checkout_year'] = checkout.split('-')[0]

        os.environ['SCRAPY_SETTINGS_MODULE'] = 'booking.settings'
        scrapy_settings = get_project_settings()
        if opts.proxy:
            scrapy_settings.set('DOWNLOADER_MIDDLEWARES', {
                'booking.middlewares.CustomHttpProxyMiddleware': 400,
                'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
            })
            logging.info('Using proxy')

        if opts.concurrent_requests:
            try:
                cr = int(opts.concurrent_requests)
                scrapy_settings.set('CONCURRENT_REQUESTS', cr)
                logging.info('Using concurrent requests')
            except ValueError:
                logging.error('Invalid concurrent requests format')
        else:
                logging.error('Specify concurrent requests')
                return

        if opts.concurrent_requests_per_domain:
            try:
                crpd = int(opts.concurrent_requests_per_domain)
                scrapy_settings.set('CONCURRENT_REQUESTS_PER_DOMAIN', crpd)
                logging.info('Using concurrent requests per domain')
            except ValueError:
                logging.error('Invalid concurrent requests per domain format')
        else:
            logging.error('Specify concurrent requests per domain')
            return

        if opts.concurrent_requests_per_ip:
            try:
                crip = int(opts.concurrent_requests_per_ip)
                scrapy_settings.set('CONCURRENT_REQUESTS_PER_IP', crip)
                logging.info('Using concurrent requests per ip')
            except ValueError:
                logging.error('Invalid concurrent requests per ip format')
        else:
            logging.error('Specify concurrent requests per ip')
            return

        print(search_params)
        print(cr)
        print(crpd)
        print(crip)

        process = CrawlerProcess(scrapy_settings)
        process.crawl(HotelsSpider, params=search_params)
        process.start()
