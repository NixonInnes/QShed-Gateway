from __future__ import annotations

import json
from typing import Optional
from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.orm import Mapped, relationship, backref, mapped_column
from sqlalchemy.orm.collections import attribute_keyed_dict
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from sqlalchemy.ext.associationproxy import 

import qshed.client.models.data as dataModels

from gateway.app import sql_session

from . import Base


related_entities_table = Table(
    "related_entities",
    Base.metadata,
    Column("entity_1_id", ForeignKey("entity.id"), primary_key=True),
    Column("entity_2_id", ForeignKey("entity.id"), primary_key=True),
    Column("type", ForeignKey("relationshiptype.id"))
)


class RelationshipType(Base):
    name: Mapped[str] = mapped_column(index=True)


class Entity(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("entitytype.id"))
    type: Mapped[Optional["EntityType"]] = relationship()

    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("entity.id"))
    
    children: Mapped[list["Entity"]] = relationship(
        backref=backref("parent", remote_side=[id])
    )

    related_entities: Mapped[dict[str, EntityAssociation]] = relationship(
        foreign_keys=[id],
        collection_class=attribute_keyed_dict("relationship_type"),
        cascade="all, delete-orphan"
    )

    related: AssociationProxy[dict[str, "Entity"]] = association_proxy(
        "related_entities",
        "entity",
        creator=lambda rel, ent: EntityAssociation(relationship_type=rel, entity=ent)
    )
    

    timeseries_id: Mapped[Optional[int]] = mapped_column(ForeignKey("timeseries.id"))
    timeseries: Mapped[Optional["Timeseries"]] = relationship(
        backref=backref("entity", uselist=False)
    )

    collection_id: Mapped[Optional[int]] = mapped_column(ForeignKey("collection.id"))
    collection: Mapped[Optional["Collection"]] = relationship(
        backref=backref("entity", uselist=False)
    )

    def __repr__(self):
        s = f"<Entity(id={self.id}"
        if self.type is not None:
            s += f", type='{self.type.name}'"
        else:
            s += f", type=None"

        if self.parent:
            s += f", parent={self.parent.id}"

        if self.children:
            s += f", children={[c.id for c in self.children]}"

        if self.related:
            s += f", related={[r.id for r in self.related]}"

        if self.timeseries:
            s += f", timeseries={self.timeseries.name}"

        if self.collection:
            s += f", collection={self.collection.name}"

        s += ")>"
        return s


class EntityAssociation(Base):
    entity_1_id: Mapped[int] = mapped_column(ForeignKey("entity.id"), primary_key=True)
    entity_2_id: Mapped[int] = mapped_column(ForeignKey("entity.id"), primary_key=True)
    relationship_type: Mapped[str]

    entity_1: Mapped[Entity] = relationship(
        back_populates="entity_associations"
    )


class EntityType(Base):
    name: Mapped[str] = mapped_column(index=True)


class Property(Base):
    name: Mapped[str] = mapped_column(index=True)
    value: Mapped[str]

    entity_id: Mapped[int] = mapped_column(ForeignKey("entity.id"))
    entity: Mapped["Entity"] = relationship(backref="properties")

    type_id: Mapped[int] = mapped_column(ForeignKey("propertytype.id"))
    type: Mapped["PropertyType"] = relationship()


class PropertyType(Base):
    name: Mapped[str] = mapped_column(index=True)