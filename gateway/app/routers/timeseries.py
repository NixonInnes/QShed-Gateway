import json
import pandas as pd
from datetime import datetime
from fastapi import APIRouter
from typing import Optional

from qshed.client.models.data import DataFrameModel
from qshed.client.models.response import TagResponse, StrResponse

from config import Config
from ..timeseries import Timeseries


router = APIRouter()


@router.get("/get/{tag_name}", response_model=TagResponse)
def get_tag(tag_name: str, start: str, end: str):
    if start:
        start = datetime.strptime(start, Config.TIME_FORMAT)
    if end:
        end = datetime.strptime(end, Config.TIME_FORMAT)
    ts = Timeseries(tag_name).get_points(start=start, end=end).to_json()
    return TagResponse(content=ts)

@router.post("/set/{tag_name}", response_model=StrResponse)
def set_tag_values(tag_name: str, dataFrame: DataFrameModel):
    ts = Timeseries(tag_name)
    df = dataFrame.parse()
    ts.add_points(df)
    return StrResponse(content="ok")

