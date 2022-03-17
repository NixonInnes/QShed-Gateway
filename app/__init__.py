from fastapi import FastAPI
from pymongo import MongoClient
from influxdb_client import InfluxDBClient


from config import Config


mongo_client = MongoClient(Config.MONGO_URL)

influx_client = InfluxDBClient(
    url=Config.INFLUX_URL,
    token=Config.INFLUX_TOKEN,
    org=Config.INFLUX_ORG
)


def create_app():
    app = FastAPI()

    from .routers import main, scheduler, database, timeseries

    app.include_router(main.router)
    app.include_router(scheduler.router, prefix="/scheduler")
    app.include_router(database.router, prefix="/database")
    app.include_router(timeseries.router, prefix="/timeseries")

    return app
