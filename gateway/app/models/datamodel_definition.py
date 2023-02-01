from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class DataModelDefinition(Base):
    name: Mapped[str] = mapped_column(index=True)


class DataModelDefinitionAttribute(Base):
    name: Mapped[str] = mapped_column(index=True)
    type: Mapped[str] = mapped_column()

    definition_id: Mapped[int] = mapped_column(ForeignKey("datamodeldefinition.id"))
    definition: Mapped["DataModelDefinition"] = relationship(backref="attributes")
