import json
from time import time
import os
from influxdb import InfluxDBClient
from labrad.wrappers import connectAsync
from twisted.internet.defer import inlineCallbacks
from twisted.internet.reactor import callInThread

from conductor_device.conductor_parameter import ConductorParameter

def to_float(x):
    try:
        return float(x)
    except:
        return 0.

class Client(ConductorParameter):
    priority = 1
    update_every = 300 # 5 minutes [s]
    last_update = 0 # unix timestamp of last update [s]

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        self.dbclient = InfluxDBClient.from_DSN(os.getenv('INFLUXDBDSN'))
    
    @inlineCallbacks
    def update(self):
        if (time() - self.last_update) > self.update_every:
            self.last_update = time()
            parameters_json = yield self.cxn.conductor.get_parameter_values()
            parameters = json.loads(parameters_json)
        
            to_db = [
                {
                    "measurement": "experiment parameters",
                    "tags": {"device": device_name, "parameter": p},
                    "fields": {"value": to_float(v)},
                } for device_name, device in parameters.items() 
                  for p, v in device.items()
            ]
        
            callInThread(self.dbclient.write_points, to_db)
