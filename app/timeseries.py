from datetime import datetime, timedelta
from influxdb_client.client.write_api import SYNCHRONOUS

from config import Config
from . import influx_client


class Timeseries:
    def __init__(self, name):
        print(Config.INFLUX_URL)
        self.name = name
        self.__write_api = influx_client.write_api(write_options=SYNCHRONOUS)
        self.__query_api = influx_client.query_api()

    def __query(self, q, params={}, _params={}):
        q_prefix = """
            from(bucket:"{bucket}")
        """.format(
            bucket=Config.INFLUX_BUCKET
        )

        q_suffix = """
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") 
            |> keep(columns: ["_time", "v"])
            |> sort(columns: ["_time"], desc: _desc) 
        """

        default_params = {"_measurement": self.name, "_desc": False}

        if _params:
            q = q.format(**_params)

        q = q_prefix + q + q_suffix
        params = {**default_params, **params}
        return self.__query_api.query_data_frame(q, params=params)

    def __parse_influx_table(self, df, squeeze=True):
        if len(df) < 1:
            return df
        df.drop(["result", "table"], axis=1, inplace=True)
        df.rename(columns={"_time": "time", "v": self.name}, inplace=True)
        df.set_index("time", inplace=True)
        return df

    def add_point(self, value, time=None):
        if not time:
            time = datetime.now()
        self.__write_api.write(
            bucket,
            org,
            [{"measurement": self.name, "fields": {"v": value}, "time": time}],
        )

    def get_points(self, start=timedelta(days=-1), end=None):
        if not end:
            end = datetime.now()

        q = """
            |> range(start: _start, stop: _end)
            |> filter(fn: (r) => r["_measurement"] == _measurement)
        """
        params = {
            "_start": start,
            "_end": end,
        }
        df = self.__query(q, params=params)
        return self.__parse_influx_table(df)

    def get_points_agg(
        self,
        start=timedelta(days=-1),
        end=None,
        aggregate="mean",
        every=timedelta(hours=1),
    ):
        if not end:
            end = datetime.now()

        q = """
            |> range(start: _start, stop: _end)
            |> filter(fn: (r) => r["_measurement"] == _measurement)
            |> aggregateWindow(every: {_every}, fn: {_aggregate}, createEmpty: false)
        """
        params = {
            "_start": start,
            "_end": end,
            "_every": every,
        }
        _params = {
            "_aggregate": aggregate,
            "_every": "_every" if not isinstance(every, str) else every,
        }
        df = self.__query(q, params=params, _params=_params)
        return self.__parse_influx_table(df)

    def get_latest_point(self):
        q = """
            |> range(start: 0, stop: now())
            |> filter(fn: (r) => r["_measurement"] == _measurement)
            |> last()
        """
        df = self.__query(q)
        return self.__parse_influx_table(df, squeeze=False)