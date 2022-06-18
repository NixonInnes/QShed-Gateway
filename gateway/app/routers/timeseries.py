from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Request, Query, Response

from qshed.client.models.data import Timeseries, ts_json_loads
from qshed.client.models.response import TimeseriesResponse, TimeseriesListResponse

from gateway.app import sql_session
from gateway.app.models import Timeseries as sqlTimeseries


router = APIRouter()


# Currently can't use `arbitrary_types_allowed=True` in response models cleanly.
# Timeseries.data is a pandas.DataFrame so requires this config
#@router.get("/get", response_model=TimeseriesListResponse)
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
    timeseries = Timeseries.parse_obj(
        ts_json_loads(
            request_body.decode("utf-8")
        )
    )
    if sql_session.query(sqlTimeseries).filter_by(name=timeseries.name).first():
        raise HTTPException(
            status_code=400, 
            detail=f"Timeseries name already exists: {timeseries.name}"
        )
    ts = sqlTimeseries.create(
        name=timeseries.name
    )
    ts.query.add_points(timeseries.data)
    response_model = TimeseriesResponse(
        data=ts.build_model(
            start=timeseries.data.index[0], 
            end=timeseries.data.index[-1]
        )
    )
    return Response(content=response_model.json(), media_type="application/json")


# @router.get("/get/{name}", response_model=responseModels.TimeseriesResponse)
# def get(name: str, start: str, end: str):
#     ts_record = sql_session.query(sqlModels.TimeseriesRecord).filter_by(name=name).first()
#     if ts_record is None:
#         return responseModels.TimeseriesResponse(
#             ok=False, 
#             content="", 
#             message=f"unable to find timeseries with name: {name}"
#         )
#     return get_by_id(ts_record.id, start, end)


# @router.get("/get/id/{id}", response_model=responseModels.TimeseriesResponse)
# def get_by_id(id: int, start: str, end: str):
#     ts_record = sql_session.query(sqlModels.TimeseriesRecord).get(id)
#     if ts_record is None:
#         return responseModels.TimeseriesResponse(
#             ok=False, 
#             content="", 
#             message=f"unable to find timeseries with id: {id}"
#         )

#     if start:
#         start = datetime.strptime(start, Config.TIME_FORMAT)
#     if end:
#         end = datetime.strptime(end, Config.TIME_FORMAT)
#     content =zip_str(ts_record.get().get_points(start=start, end=end).to_json())
#     return responseModels.TimeseriesResponse(content=content)


# @router.post("/create", response_model=responseModels.TimeseriesRecordResponse)
# def create(ts_record: dataModels.TimeseriesRecord):
#     new_record = sqlModels.TimeseriesRecord(name=ts_record.name)
#     sql_session.add(new_record)
#     sql_session.commit()
#     return responseModels.TimeseriesRecordResponse(content=new_record.json())


# @router.post("/set/{name}", response_model=responseModels.TimeseriesResponse)
# def set(name: str, dataFrame: dataModels.DataFrameModel):
#     ts_record = sql_session.query(
#         sqlModels.TimeseriesRecord).filter_by(name=name).first()
#     if ts_record is None:
#         return responseModels.TimeseriesResponse(
#             ok=False, 
#             content="", 
#             message=f"unable to find timeseries: {name}"
#         )
#     return set_by_id(ts_record.id, dataFrame)


# @router.post("/set/id/{id}", response_model=responseModels.TimeseriesResponse)
# def set_by_id(id: int, dataFrame: dataModels.DataFrameModel):
#     ts_record = sql_session.query(sqlModels.TimeseriesRecord).get(id)
#     if ts_record is None:
#         return responseModels.TimeseriesResponse(
#             ok=False, 
#             content="", 
#             message=f"unable to find timeseries with id: {id}"
#         )
#     df = dataFrame.parse()
#     ts_record.get().add_points(df)
#     return responseModels.TimeseriesResponse(ok=True, content=df.to_json())


# @router.get("/list", response_model=responseModels.TimeseriesRecordListResponse)
# def list():
#     records = [record.dict() for record in sql_session.query(sqlModels.TimeseriesRecord).all()]
#     return responseModels.TimeseriesRecordListResponse(content=json.dumps(records))


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



