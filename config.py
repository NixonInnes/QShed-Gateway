import os


class Config:
    MONGO_URL = "mongodb://" + os.environ.get("MONGO_URL", "192.168.1.1:27017")
    SCHEDULER_URL = os.environ.get("SCHEDULER_URL", "http://192.168.1.1:5100")
    INFLUX_URL = os.environ.get("INFLUX_URL", "192.168.1.1:8086")
    INFLUX_BUCKET = os.environ.get("INFLUX_BUCKET", "")
    INFLUX_ORG = os.environ.get("INFLUX_ORG", "")
    INFLUX_TOKEN = os.environ.get("INFLUX_TOKEN", "")
    TIME_FORMAT = "%y/%m/%d %H:%M:%S"
