from influxdb import InfluxDBClient
import os

client = InfluxDBClient.from_DSN(os.getenv('INFLUXDBDSN'))

def db_point(name, sequence):
    return [{"measurement": "sequences", 
             "tags": {"name": name},
             "fields": {"sequence": sequence},
             }]
