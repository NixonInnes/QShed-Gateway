from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

import qshed.client.models.data as dataModels

from gateway.app import mongo_client, sql_session

from . import Base


class CollectionDatabase(Base):
    name: Mapped[str] = mapped_column(index=True)
    collections: Mapped[list["Collection"]] = relationship(backref="database")

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
            collections=[collection.id for collection in self.collections],
        )


class Collection(Base):
    name: Mapped[str] = mapped_column(index=True)
    database_id: Mapped[int] = mapped_column(ForeignKey("collectiondatabase.id"))

    def build_model(self, query={}, limit=10):
        return dataModels.Collection(
            id=self.id,
            name=self.name,
            database=self.database_id,
            query=query,
            limit=limit,
            data=list(self.data.find(query).sort("$natural", -1).limit(limit)),
        )

    @property
    def data(self):
        return mongo_client[self.database.name][self.name]
