from fastapi import FastAPI
from pymongo import MongoClient
from influxdb_client import InfluxDBClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import Config


mongo_client = MongoClient(Config.MONGO_ADDRESS)

influx_client = InfluxDBClient(
    url=Config.INFLUX_ADDRESS, token=Config.INFLUX_TOKEN, org=Config.INFLUX_ORG
)

sql_engine = create_engine(Config.SQL_ADDRESS, future=True)
sql_session = Session(sql_engine)


def create_app():
    app = FastAPI()

    from .routers import main, scheduler, sql, nosql, timeseries

    app.include_router(main.router)
    app.include_router(scheduler.router, prefix="/scheduler")
    app.include_router(sql.router, prefix="/sql")
    app.include_router(nosql.router, prefix="/nosql")
    app.include_router(timeseries.router, prefix="/timeseries")

    return app
