from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr

from gateway.app import sql_session

class SQLBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        sql_session.add(instance)
        sql_session.commit()
        return instance



from sqlalchemy.orm import declarative_base

Base = declarative_base(cls=SQLBase)


from .collection import CollectionDatabase, Collection
from .entity import Entity
from .timeseries import Timeseries
from gateway.app import sql_engine

Base.metadata.create_all(sql_engine)