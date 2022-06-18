import json
from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

import qshed.client.models.data as dataModels

from gateway.app.queries import TimeseriesQuery

from . import Base


class Timeseries(Base):
    name = Column(String, index=True)

    @property
    def query(self):
        return TimeseriesQuery(self.name)

    def build_model(self, start, end):
        return dataModels.Timeseries(
            id=self.id,
            name=self.name,
            start=start,
            end=end,
            data=self.query.get_points(start=start, end=end)
        )
