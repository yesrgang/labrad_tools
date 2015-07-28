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
from twistd.internet.task import LoopingCall
from influxdb import InfluxDBClient


class RMDDSServer(DDSServer):
    @inlineCallbacks
    def initServer(self):
        yield DDSServer.initServer(self)
        self.sweep_call = LoopingCall(self._sweep)
        self.sweep_call.start(self.sweep_updateperiod)
        self.db_clinet = InfluxDBClient.from_DSN(os.envron.get('INFLUXDBDSN'))
    
    @setting(5, 'sweepstate', name='s', state='b', returns='b')
    def sweepstate(self, c, name, state=None):
        if state is None:
            state = self.dds[name].sweepstate
        else:
            self.dds[name].sweepstate = state
        yield self.notify_listeners(name)
        returnValue(state)

    @setting(6, 'sweeprate', name='s', rate='v', returns='v')
    def sweeprate(self, c, name, rate=None):
        if rate is None:
            rate = self.dds[name].sweeprate
        else:
            self.dds[name].sweeprate = rate
        yield self.notify_listeners(name)
        returnValue(rate)

    @inlineCallbacks
    def _sweep(self):
        for name in self.dds.keys():
            if self.dds[name].sweepstate:
                offset_query_str = 
                prev_time, prev_detuning = self.db_client.query(self.dds[name].detuning_query_str).raw['series'][0]['values'][0]
                prev_ramprate = self.db_client.query(self.dds[name].ramprate_query_str).raw['series'][0]['values'][0][1]
                f += self.dds[name].sweeprate*self.sweep_dwell
                dt = datetime.datetime.utcnow() - datetime.datetime.strptime(prev_time[:-4], '%Y-%m-%dT%H:%M:%S.%f')
                next_detuning = prev_detuning + prev_ramprate*(dt
                yield self.frequency(None, name, f)


config_name = 'redmasterdds_config'
__server__ = DDSServer(config_name)

if __name__ == "__main__":
    from labrad import util
    util.runServer(__server__)
