import json
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, backref

from . import sql_engine, sql_session


Base = declarative_base()


class Entity(Base):
    __tablename__ = "sql_entity"
    id = Column(Integer, primary_key=True)

    name = Column(String, index=True)
    data = Column(String)
    type = Column(Integer, default=0)

    parent_id = Column(Integer, ForeignKey("sql_entity.id"))
    children = relationship("Entity", backref=backref("parent", remote_side=[id]))

    @property
    def display_name(self):
        if self.parent:
            return f"{self.parent.name}:{self.name}"
        return self.name

    @classmethod
    def get_roots(cls):
        return sql_session.query(cls).filter(cls.parent==None).all()

    def dict(self):
        return dict(
            id=self.id,
            name=self.name,
            display_name=self.display_name,
            data_=self.data,
            type=self.type,
            parent=self.parent.id if self.parent else None,
            children=[child.id for child in self.children]
        )

    def json(self):
        return json.dumps(self.dict())



Base.metadata.create_all(sql_engine)