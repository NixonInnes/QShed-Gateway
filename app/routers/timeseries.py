import json
from datetime import datetime
from fastapi import APIRouter
from typing import Optional

from qshed.client.models.response import TagResponse

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
