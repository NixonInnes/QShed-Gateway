from fastapi import FastAPI
import pymongo


mongo_client = pymongo.MongoClient("mongodb://192.168.1.100:27017")


def create_app():
    app = FastAPI()

    from .routers import main, scheduler, database

    app.include_router(main.router)
    app.include_router(scheduler.router, prefix="/scheduler")
    app.include_router(database.router, prefix="/database")

    return app
