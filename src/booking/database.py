from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scrapy.utils.project import get_project_settings
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()


class Singleton:
    def __init__(self, cls):
        self.cls = cls
        self.instance = None

    def __call__(self, *args, **kwds):
        if self.instance is None:
            self.instance = self.cls(*args, **kwds)
        return self.instance


class DBConnection():
    engine = None
    session = None

    def __init__(self):
        engine = create_engine(get_project_settings().get("CONNECTION_STRING"))
        DeclarativeBase.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def insert(self, data):
        self.session.add(data)
        self.session.commit()
        return data.id

    def update(self, model, field, values):
        query = self.session.query(model).filter(getattr(model, field) == values[field])
        if len(query.all()):
            query.update(values)
            self.session.commit()

    def insert_or_update(self, model, field, values):
        query = self.session.query(model).filter(getattr(model, field) == values[field])
        obj = query.first()
        if obj is not None:
            query.update(values)
            self.session.commit()
            return obj.id
        else:
            return self.insert(model(**values))

    def delete(self, model, field, filter_val):
        self.session.query(model).filter(getattr(model, field) == filter_val).delete()

    def rollback(self):
        self.session.rollback()

    def __del__(self):
        self.session.close()


@Singleton
class Database(object):
    connection = None

    def get_instance(self):
        if self.connection is None:
            self.connection = DBConnection()
        return self.connection
