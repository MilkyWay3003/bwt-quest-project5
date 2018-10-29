from sqlalchemy import Table, Column, Integer, String, MetaData, Numeric
from migrate.changeset.constraint import ForeignKeyConstraint

meta = MetaData()

rooms = Table(
    'rooms', meta,
    Column('id', Integer, primary_key=True)
)

prices = Table(
    'prices', meta,
    Column('id', Integer, primary_key=True),
    Column('cost', Numeric(10, 2), server_default='0'),
    Column('currency', String(8), nullable=True),
    Column('max_persons', Integer, nullable=True),
    Column('cancel_type', String(32), nullable=True),
    Column('meal', String(32), nullable=True),
    Column('room_id', Integer),
    mysql_engine='InnoDB',
    mysql_charset='utf8mb4'
)

cons = ForeignKeyConstraint(
    [prices.c.room_id],
    [rooms.c.id],
    name="fk_prices_room",
    onupdate="cascade",
    ondelete="cascade"
)


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    prices.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    prices.drop()
