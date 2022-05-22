import os


class Config:
    MONGO_ADDRESS = "mongodb://" + os.environ.get("MONGO_URL", "192.168.1.100:27017")
    
    SCHEDULER_ADDRESS = os.environ.get("SCHEDULER_URL", "http://localhost:4500")
    
    INFLUX_ADDRESS = os.environ.get("INFLUX_URL", "192.168.1.100:8086")
    INFLUX_BUCKET = os.environ.get("INFLUX_BUCKET", "")
    INFLUX_ORG = os.environ.get("INFLUX_ORG", "")
    INFLUX_TOKEN = os.environ.get("INFLUX_TOKEN", "")

    SQL_ADDRESS = os.environ.get("SQL_ADDRESS", "sqlite:///database.sqlite")

    TIME_FORMAT = "%Y/%m/%d %H:%M:%S"
