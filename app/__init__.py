from flask import Flask
import pymongo


mongo_client = pymongo.MongoClient("mongodb://192.168.1.100:27017")


def create_app():
    app = Flask(__name__)

    from .blueprints.main import main_bp as main_blueprint
    from .blueprints.database import data_bp as database_blueprint
    from .blueprints.scheduler import sched_bp as scheduler_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(database_blueprint, url_prefix="/database")
    app.register_blueprint(scheduler_blueprint, url_prefix="/scheduler")

    return app
