import json

from sqlalchemy.orm import Mapped, mapped_column

import qshed.client.models.data as dataModels

from gateway.app.queries import TimeseriesQuery

from . import Base


class Timeseries(Base):
    name: Mapped[str] = mapped_column(index=True)

    @property
    def data(self):
        return TimeseriesQuery(self.name)

    def build_model(self, start, end):
        return dataModels.Timeseries(
            id=self.id,
            name=self.name,
            start=start,
            end=end,
            data=self.data.get_points(start=start, end=end),
        )
