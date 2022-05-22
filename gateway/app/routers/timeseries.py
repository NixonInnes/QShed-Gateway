import json
import pandas as pd
from datetime import datetime
from fastapi import APIRouter
from typing import Optional

from qshed.client.utils import zip_str
import qshed.client.models.data as dataModels
import qshed.client.models.response as responseModels

from config import Config
from gateway.app import influx_client, sql_session
from gateway.app.timeseries import TimeseriesQuery
import gateway.app.sql as sqlModels


router = APIRouter()


@router.get("/get/{name}", response_model=responseModels.TimeseriesResponse)
def get(name: str, start: str, end: str):
    ts_record = sql_session.query(sqlModels.TimeseriesRecord).filter_by(name=name).first()
    if ts_record is None:
        return responseModels.TimeseriesResponse(
            ok=False, 
            content="", 
            message=f"unable to find timeseries with name: {name}"
        )
    return get_by_id(ts_record.id, start, end)


@router.get("/get/id/{id}", response_model=responseModels.TimeseriesResponse)
def get_by_id(id: int, start: str, end: str):
    ts_record = sql_session.query(sqlModels.TimeseriesRecord).get(id)
    if ts_record is None:
        return responseModels.TimeseriesResponse(
            ok=False, 
            content="", 
            message=f"unable to find timeseries with id: {id}"
        )

    if start:
        start = datetime.strptime(start, Config.TIME_FORMAT)
    if end:
        end = datetime.strptime(end, Config.TIME_FORMAT)
    content =zip_str(ts_record.get().get_points(start=start, end=end).to_json())
    return responseModels.TimeseriesResponse(content=content)


@router.post("/create", response_model=responseModels.TimeseriesRecordResponse)
def create(ts_record: dataModels.TimeseriesRecord):
    new_record = sqlModels.TimeseriesRecord(name=ts_record.name)
    sql_session.add(new_record)
    sql_session.commit()
    return responseModels.TimeseriesRecordResponse(content=new_record.json())


@router.post("/set/{name}", response_model=responseModels.TimeseriesResponse)
def set(name: str, dataFrame: dataModels.DataFrameModel):
    ts_record = sql_session.query(
        sqlModels.TimeseriesRecord).filter_by(name=name).first()
    if ts_record is None:
        return responseModels.TimeseriesResponse(
            ok=False, 
            content="", 
            message=f"unable to find timeseries: {name}"
        )
    return set_by_id(ts_record.id, dataFrame)


@router.post("/set/id/{id}", response_model=responseModels.TimeseriesResponse)
def set_by_id(id: int, dataFrame: dataModels.DataFrameModel):
    ts_record = sql_session.query(sqlModels.TimeseriesRecord).get(id)
    if ts_record is None:
        return responseModels.TimeseriesResponse(
            ok=False, 
            content="", 
            message=f"unable to find timeseries with id: {id}"
        )
    df = dataFrame.parse()
    ts_record.get().add_points(df)
    return responseModels.TimeseriesResponse(ok=True, content=df.to_json())


@router.get("/list", response_model=responseModels.TimeseriesRecordListResponse)
def list():
    records = [record.dict() for record in sql_session.query(sqlModels.TimeseriesRecord).all()]
    return responseModels.TimeseriesRecordListResponse(content=json.dumps(records))


@router.post("/scan", response_model=responseModels.TimeseriesRecordListResponse)
def scan():
    q = f'import "influxdata/influxdb/schema"\n\nschema.measurements(bucket: "{Config.INFLUX_BUCKET}")'
    qapi = influx_client.query_api()
    tables = qapi.query(q)

    records = []
    for table in tables:
        for record in table:
            record = sql_session.query(sqlModels.TimeseriesRecord).filter_by(name=record["_value"]).first()
            if record is None:
                record = sqlModels.TimeseriesRecord(name=record["_value"])
                sql_session.add(record)
                sql_session.commit()
                records.append(record.dict())
    return responseModels.TimeseriesRecordListResponse(
        content=json.dumps(records), 
        message=f"added {len(records)} new records"
    )



