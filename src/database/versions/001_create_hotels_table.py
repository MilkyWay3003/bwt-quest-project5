from sqlalchemy import Table, Column, Integer, Numeric, String, Text, MetaData, Date

meta = MetaData()

hotel = Table(
    'hotels', meta,
    Column('id', Integer, primary_key=True),
    Column('name', String(128)),
    Column('country', String(32)),
    Column('city', String(32)),
    Column('postcode', String(16)),
    Column('address', String(128)),
    Column('description', Text()),
    Column('rating', Numeric(10, 2), nullable=True),
    Column('checkin', Date),
    Column('checkout', Date),
    mysql_engine='InnoDB',
    mysql_charset='utf8mb4'
)


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    hotel.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    hotel.drop()
