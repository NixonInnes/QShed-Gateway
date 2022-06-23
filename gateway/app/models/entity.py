import json
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

import qshed.client.models.data as dataModels

from gateway.app import sql_session

from . import Base


class Entity(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    data = Column(String)
    type = Column(Integer, default=0)

    parent_id = Column(Integer, ForeignKey("entity.id"))
    children = relationship("Entity", backref=backref("parent", remote_side=[id]))

    timeseries_id = Column(Integer, ForeignKey("timeseries.id"))
    timeseries = relationship("Timeseries", backref=backref("entity", uselist=False))
    collection_id = Column(Integer, ForeignKey("collection.id"))
    collection = relationship("Collection", backref=backref("entity", uselist=False))

    def get_relative_name(self, full=False):
        if self.parent is not None:
            if full:
                return f"{self.parent.get_relative_name(full=full)}:{self.name}"
            return f"{self.parent.name}:{self.name}"
        return self.name

    @classmethod
    def get_roots(cls):
        return sql_session.query(cls).filter(cls.parent==None).all()

    def build_model(self):
        return dataModels.Entity(
            id=self.id,
            name=self.name,
            data_=self.data,
            type=self.type,
            parent=self.parent.id if self.parent else None,
            children=[child.id for child in self.children],
            timeseries=self.timeseries_id,
            collection=self.collection_id
        )

