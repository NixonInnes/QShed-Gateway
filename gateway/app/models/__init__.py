from datetime import datetime
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.ext.declarative import declared_attr

from gateway.app import sql_session, sql_engine


class SQLBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        sql_session.add(instance)
        sql_session.commit()
        return instance

    @classmethod
    def query(cls):
        return sql_session.query(cls)


Base = declarative_base(cls=SQLBase)


from .collection import CollectionDatabase, Collection
from .entity import Entity, EntityType, RelationshipType, Property, PropertyType
from .timeseries import Timeseries
from .datamodel_definition import DataModelDefinition, DataModelDefinitionAttribute

Base.metadata.create_all(sql_engine)
