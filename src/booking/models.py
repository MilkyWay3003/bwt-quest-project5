from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


DeclarativeBase = declarative_base()


class Hotel(DeclarativeBase):
    __tablename__ = 'hotels'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(128))
    country = Column('country', String(32))
    city = Column('city', String(32))
    postcode = Column('postcode', String(16))
    address = Column('address', String(128))
    description = Column('description', Text())
    rating = Column('rating', Numeric(10, 2))
    image = Column('image', String(128))
    checkin = Column('checkin', Date)
    checkout = Column('checkout', Date)
    rooms = relationship('Room', backref='hotel')

    def __init__(self, name, country, city, postcode, address, description, rating, image, checkin, checkout):
        self.name = name
        self.country = country
        self.city = city
        self.postcode = postcode
        self.address = address
        self.description = description
        self.rating = rating
        self.image = image
        self.checkin = checkin
        self.checkout = checkout

    def __repr__(self):
        return "<Data {}, {}, {}, {}, {}, {}, {}, {}>".format(
            self.name,
            self.country,
            self.city,
            self.address,
            self.postcode,
            self.description,
            self.rating,
            self.image,
            self.checkin,
            self.checkout
        )


class Room(DeclarativeBase):
    __tablename__ = 'rooms'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(128))
    description = Column('description', Text())
    services = Column('services', Text())
    image = Column('image', String(128))
    hotel_id = Column('hotel_id', Integer, ForeignKey('hotels.id'))
    prices = relationship('Price', backref='room')

    def __init__(self, name, description, services, image, hotel_id):
        self.name = name
        self.description = description
        self.services = services
        self.image = image
        self.hotel_id = hotel_id

    def __repr__(self):
        return "<Data {}, {}, {}, {}, {}>".format(
            self.name,
            self.description,
            self.services,
            self.image,
            self.hotel_id
        )


class Price(DeclarativeBase):
    __tablename__ = 'prices'

    id = Column('id', Integer, primary_key=True)
    cost = Column('cost', Numeric(10, 2))
    currency = Column('currency', String(8))
    max_persons = Column('max_persons', Integer)
    cancel_type = Column('cancel_type', String(32))
    meal = Column('meal', String(32))
    room_id = Column('room_id', Integer, ForeignKey('rooms.id'))

    def __init__(self, cost, currency, max_persons, cancel_type, meal, room_id):
        self.cost = cost
        self.currency = currency
        self.max_persons = max_persons
        self.cancel_type = cancel_type
        self.meal = meal
        self.room_id = room_id

    def __repr__(self):
        return "<Data {}, {}, {}, {}, {}, {}>".format(
            self.cost,
            self.currency,
            self.max_persons,
            self.cancel_type,
            self.meal,
            self.room_id
        )
