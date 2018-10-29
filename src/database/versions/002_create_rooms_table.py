from sqlalchemy import Table, Column, Integer, String, Text, MetaData
from migrate.changeset.constraint import ForeignKeyConstraint

meta = MetaData()
hotel = Table(
    'hotels', meta,
    Column('id', Integer, primary_key=True)
)

room = Table(
    'rooms', meta,
    Column('id', Integer, primary_key=True),
    Column('name', String(128), nullable=True),
    Column('description', Text()),
    Column('services', Text()),
    Column('image', String(128), nullable=True),
    Column('hotel_id', Integer),
    mysql_engine='InnoDB',
    mysql_charset='utf8mb4'
)

cons = ForeignKeyConstraint(
    [room.c.hotel_id],
    [hotel.c.id],
    name="fk_rooms_hotel",
    onupdate="cascade",
    ondelete="cascade"
)


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    room.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    room.drop()
