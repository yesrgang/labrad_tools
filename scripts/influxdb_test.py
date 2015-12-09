from influxdb import InfluxDBClient
import os

"""
create environment variable INFLUXDBDSN = influxdb://username:password@hostname:8086/srq
"""

client = InfluxDBClient.from_DSN(os.getenv('INFLUXDBDSN'))

def db_point(measurement_name, channel_name, value):
    return [{"measurement": measurement_name, 
             "tags": {"channel": channel_name},
             "fields": {"value": value},
             }]

client.write_points(db_point('test', 'channel a', 2))
