from twisted.internet.defer import inlineCallbacks
from influxdb import InfluxDBClient

def to_float(x):
    try:
        return float(x)
    except:
        return 0.

def initialize(self):
    self.dbclient = InfluxDBClient.from_DSN(os.getenv('INFLUXDBDSN'))

@inlineCallbacks
def update(self, value):
    parameters_json = yield self.cxn.yesr20_conductor.set_paramters()
    parameters = json.loads(parameters_json)

    to_db = [{
        "measurement": "experiment parameters",
        "tags": {"device": device_name, "parameter": p},
        "fields": {"value": to_float(v)},
    } for device_name, device in parameters.items() for p, v in device.items()]

    try:
        self.dbclient.write_points(to_db)
    except:
        print "failed to save parameters to database"

config = {
    'influxdb': {
        'parameters_write': {
            'initialize': initialize, 
            'update': update,
            'value': None,
        },
    },
}

