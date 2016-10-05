import json
import os
import sys

from influxdb import InfluxDBClient
from labrad.wrappers import connectAsync
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from twisted.internet.reactor import callInThread

sys.path.append('../')
from generic_device.generic_parameter import GenericParameter

def to_float(x):
    try:
        return float(x)
    except:
        return 0.

class Client(GenericParameter):
    @inlineCallbacks
    def initialize(self):
        self.cxn = yield connectAsync()
        self.counter = 0
        self.dbclient = InfluxDBClient.from_DSN(os.getenv('INFLUXDBDSN'))
    
    @inlineCallbacks
    def update(self, value):
        self.counter += 1
        if self.counter >= 10:
            self.counter = 0
            print 'sending to db'
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
        
            #yield deferToThread(self.dbclient.write_points, to_db)
            callInThread(self.dbclient.write_points, to_db)
