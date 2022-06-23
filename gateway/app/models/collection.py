import json
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

import qshed.client.models.data as dataModels
import qshed.client.models.response as responseModels

from gateway.app import mongo_client, sql_session
from gateway.app.queries import TimeseriesQuery

from . import Base


class CollectionDatabase(Base):
    name = Column(String, index=True)
    collections = relationship("Collection", backref="database")

    @classmethod
    def create(cls, name, **kwargs):
        mongo_client[name]
        collection_db = cls(name=name, **kwargs)
        sql_session.add(collection_db)
        sql_session.commit()
        return collection_db


    def build_model(self):
        return dataModels.CollectionDatabase(
            id=self.id,
            name=self.name,
            collections=[
                collection.id for collection in self.collections
            ]
        )


class Collection(Base):
    name = Column(String, index=True)
    database_id = Column(Integer, ForeignKey("collectiondatabase.id"))

    def build_model(self, query={}, limit=10):
        return dataModels.Collection(
            id=self.id,
            name=self.name,
            database=self.database_id,
            query=query,
            limit=limit,
            data=list(
                self.query
                .find(query)
                .sort("$natural", -1)
                .limit(limit)
            )
        )

    @property
    def query(self):
        return mongo_client[self.database.name][self.name]

