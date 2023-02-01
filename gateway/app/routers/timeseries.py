from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Request, Query, Response

from qshed.client.models.data import Timeseries, ts_json_loads
from qshed.client.models.response import (
    TimeseriesResponse,
    TimeseriesListResponse,
    error,
)

from gateway.app import sql_session
from gateway.app.models import Timeseries as sqlTimeseries


router = APIRouter()


# Currently can't use `arbitrary_types_allowed=True` in response models cleanly.
# Timeseries.data is a pandas.DataFrame so requires this config
# @router.get("/get", response_model=TimeseriesListResponse)
@router.get("/get")
def get(start: datetime, end: datetime, id: List[int] = Query(default=[])):
    ts_list = []
    for i in id:
        ts = sql_session.query(sqlTimeseries).get(i)
        if ts is None:
            raise HTTPException(status_code=404, detail=f"Invalid timeseries id: {i}")
        ts_list.append(ts)
    response_model = TimeseriesListResponse(
        data=[ts.build_model(start, end) for ts in ts_list]
    )
    return Response(content=response_model.json(), media_type="application/json")


# Currently FastAPI won't use any custom json_loads methods so we have to load it manually
# @router.post("/create")
# def create(timeseries: Timeseries):
#     if sql_session.query(sqlTimeseries).filter_by(name=timeseries.name).first():
#         raise HTTPException(
#             status_code=400,
#             detail=f"Timeseries name already exists: {timeseries.name}"
#         )
#     ts = sqlTimeseries.create(
#         name=timeseries.name
#     )
#     ts.query.add_points(timeseries.data)
#     return TimeseriesResponse(
#         data=ts.build_model(
#             start=timeseries.data.index.iloc[0],
#             end=timeseries.data.index.iloc[-1]
#         )
#     )
@router.post("/create")
async def create(timeseries_request: Request):
    request_body = await timeseries_request.body()
    timeseries = Timeseries.parse_obj(ts_json_loads(request_body.decode("utf-8")))
    if sql_session.query(sqlTimeseries).filter_by(name=timeseries.name).first():
        raise HTTPException(
            status_code=400, detail=f"Timeseries name already exists: {timeseries.name}"
        )
    sql_timeseries = sqlTimeseries.create(name=timeseries.name)
    sql_timeseries.query.add_points(timeseries.data)
    response_model = TimeseriesResponse(
        data=sql_timeseries.build_model(
            start=timeseries.data.index[0], end=timeseries.data.index[-1]
        )
    )
    return Response(content=response_model.json(), media_type="application/json")


@router.post("/add")
async def add(timeseries_request: Request):
    request_body = await timeseries_request.body()
    timeseries = Timeseries.parse_obj(ts_json_loads(request_body.decode("utf-8")))
    if timeseries.id is not None:
        sql_timeseries = sql_session.query(sqlTimeseries).get(timeseries.id)
        if sql_timeseries is None:
            raise HTTPException(
                status_code=404, detail=f"Invalid Timeseries id: {timeseries.id}"
            )
    else:
        sql_timeseries = (
            sql_session.query(sqlTimeseries).filter_by(name=timeseries.name).first()
        )
        if sql_timeseries is None:
            raise HTTPException(
                status_code=404, detail=f"Invalid Timeseries name: {timeseries.name}"
            )

    sql_timeseries.query.add_points(timeseries.data)
    response_model = TimeseriesResponse(
        data=sql_timeseries.build_model(
            start=timeseries.data.index[0], end=timeseries.data.index[-1]
        )
    )
    return Response(content=response_model.json(), media_type="application/json")


# @router.post("/scan", response_model=responseModels.TimeseriesRecordListResponse)
# def scan():
#     q = f'import "influxdata/influxdb/schema"\n\nschema.measurements(bucket: "{Config.INFLUX_BUCKET}")'
#     qapi = influx_client.query_api()
#     tables = qapi.query(q)

#     records = []
#     for table in tables:
#         for record in table:
#             record = sql_session.query(sqlModels.TimeseriesRecord).filter_by(name=record["_value"]).first()
#             if record is None:
#                 record = sqlModels.TimeseriesRecord(name=record["_value"])
#                 sql_session.add(record)
#                 sql_session.commit()
#                 records.append(record.dict())
#     return responseModels.TimeseriesRecordListResponse(
#         content=json.dumps(records),
#         message=f"added {len(records)} new records"
#     )
