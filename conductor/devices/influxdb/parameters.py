import sys

from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from labrad.wrappers import connectAsync
from influxdb import InfluxDBClient

sys.path.append('../')
from generic_device.generic_parameter import GenericParameter

def to_float(x):
    try:
        return float(x)
    except:
        return 0.

class Parameters(GenericParameter):
    @inlineCallbacks
    def initialize(self):
        yield None
        self.dbclient = InfluxDBClient.from_DSN(os.getenv('INFLUXDBDSN'))
    
    @inlineCallbacks
    def update(self, value):
        parameters_json = yield self.cxn.conductor.get_paramter_values()
        parameters = json.loads(parameters_json)
    
        to_db = [
            {
                "measurement": "experiment parameters",
                "tags": {"device": device_name, "parameter": p},
                "fields": {"value": to_float(v)},
            } for device_name, device in parameters.items() 
              for p, v in device.items()
        ]
    
        deferToThread(self.dbclient.write_points, to_db)
