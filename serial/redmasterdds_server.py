"""
### BEGIN NODE INFO
[info]
name = Red Master DDS
version = 1.0
description = 
instancename = %LABRADNODE% Red Master DDS

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
import os
import datetime
from dds_server import DDSServer
from labrad.server import setting, Signal, returnValue
from twisted.internet.task import LoopingCall
from twisted.internet.defer import inlineCallbacks
from influxdb import InfluxDBClient


class RMDDSServer(DDSServer):
    @inlineCallbacks
    def initServer(self):
        yield DDSServer.initServer(self)
	dsn = os.getenv('INFLUXDBDSN')
        self.db_client = InfluxDBClient.from_DSN(dsn)
        self.drift_call = LoopingCall(self._drift)
        self.drift_call.start(self.drift_updateperiod)
    
    @setting(5, 'driftstate', name='s', state='b', returns='b')
    def driftstate(self, c, name, state=None):
        if state is None:
            state = self.dds[name].driftstate
        else:
            self.dds[name].driftstate = state
        yield self.notify_listeners(name)
        returnValue(state)

    @setting(6, 'driftrate', name='s', rate='v', returns='v')
    def driftrate(self, c, name, rate=None):
        if rate is None:
            driftrate = self.db_client.query(self.dds[name].driftrate_query_str).raw['series'][0]['values'][-1][1]
        else:
            self.db_client.write_points(self.dds[name].driftrate_write(rate))
        yield self.notify_listeners(name)
        returnValue(rate)

    @inlineCallbacks
    def _drift(self):
        for name in self.dds.keys():
            if self.dds[name].driftstate:
                prev_time, prev_detuning = self.db_client.query(self.dds[name].detuning_query_str).raw['series'][0]['values'][-1]
                prev_driftrate = self.db_client.query(self.dds[name].driftrate_query_str).raw['series'][0]['values'][-1][1]
                dt = datetime.datetime.utcnow() - datetime.datetime.strptime(prev_time[:-4], '%Y-%m-%dT%H:%M:%S.%f')
                next_detuning = prev_detuning + prev_driftrate*dt.total_seconds()
                yield self.frequency(None, name, next_detuning)
                yield self.driftrate(None, name, prev_driftrate)
            	self.db_client.write_points(self.dds[name].detuning_write(next_detuning))
		print next_detuning


config_name = 'redmasterdds_config'
__server__ = RMDDSServer(config_name)

if __name__ == "__main__":
    from labrad import util
    util.runServer(__server__)
