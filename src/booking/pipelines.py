# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pprint
import datetime
from .models import Hotel, Room, Price
from .items import BookingHotelItem
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scrapy.mail import MailSender


class MySQLPipeline(object):
    def process_item(self, item, spider):
        try:
            if isinstance(item, BookingHotelItem):
                hotel_id = spider.database.insert_or_update(Hotel, 'name', {
                    'name': item['name'],
                    'country': item['country'],
                    'city': item['city'],
                    'postcode': item['postcode'],
                    'address': item['address'],
                    'description': item['description'],
                    'rating': item['rating'],
                    'checkin': item['checkin'],
                    'checkout': item['checkout'],
                    'image': 'images/' + item['images'][0]['path']
                })

                for room in item['rooms']:
                    room_id = spider.database.insert_or_update(Room, 'name', {
                        'name': room['name'],
                        'description': room['description'],
                        'services': room['services'],
                        'image': room['images'],
                        'hotel_id': hotel_id
                    })

                    spider.database.delete(Price, 'room_id', room_id)

                    for price in room['prices']:
                        spider.database.insert(Price(
                            room_id=room_id,
                            cost=price['cost'],
                            currency=price['currency'],
                            max_persons=price['persons'],
                            cancel_type=price['cancel'],
                            meal=price['meal']
                        ))
        except:
            spider.database.rollback()
            raise

        return item

    def close_spider(self, spider):
        settings = spider.settings
        gmail_user = settings['MAIL_USER']
        print(gmail_user)
        gmail_password = settings['MAIL_PASS']
        print(gmail_password)

        msg = MIMEMultipart()
        mail_subject = 'Booking.com website Scraper Report for ' + datetime.date.today().strftime("%m/%d/%y")
        msg['Subject'] = mail_subject

        intro = "Summary stats from Scrapy Booking.com website: \n\n"
        body = spider.crawler.stats.get_stats()
        body = pprint.pformat(body)
        body = intro + body
        msg.attach(MIMEText(body, 'plain'))

        mail_sender = MailSender(mailfrom=gmail_user, smtphost="smtp.gmail.com", smtpport=587,
                                 smtpuser=gmail_user, smtppass=gmail_password)
        mail_sender.send(to=[gmail_user], subject=mail_subject, body=msg.as_string(), cc=None)

