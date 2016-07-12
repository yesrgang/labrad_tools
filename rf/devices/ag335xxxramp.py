from ag335xxx import AG335xxx
from labrad.wrappers import connectAsync
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.reactor import callLater

def cancel_delayed_calls(device):
    for call in device.delayed_calls:
        if call.active():
            call.cancel()
    device.delayed_calls = []

class AG335xxxRamp(AG335xxx):
    @inlineCallbacks
    def initialize(self):
        self.delayed_calls = []
        yield super(AG335xxxRamp, self).initialize()
        counter_cxn = yield connectAsync()
        self.counter = yield counter_cxn[self.counter_server]
        self.counter.address(self.counter_address)
        ramprate = yield self.get_ramprate()
        yield self.set_ramprate(ramprate)

    @inlineCallbacks
    def set_ramprate(self, ramprate):
        cancel_delayed_calls(self)
        command = 'MEAS:FREQ? DEF, DEF, (@{})'.format(self.counter_source)
        ans = yield self.counter.query(command)
        f_start = float(ans)
        f_stop = f_start + ramprate*self.t_ramp
        commands = [
            'SOUR{}:FREQ {}'.format(self.source, f_start),
            'SOUR{}:FREQ:STAR {}'.format(self.source, f_start),
            'SOUR{}:FREQ:STOP {}'.format(self.source, f_stop),
            'SOUR{}:SWEEp:TIME {}'.format(self.source, self.t_ramp),
            'SOUR{}:FREQ:MODE SWE'.format(self.source),
            'TRIG{}:SOUR IMM'.format(self.source),
        ]
        for command in commands:
            self.connection.write(command)
        callLater(self.t_ramp/2., self.set_ramprate, ramprate)

    @inlineCallbacks
    def get_ramprate(self):
        start_command = 'SOUR{}:FREQ:STAR?'.format(self.source)
        stop_command = 'SOUR{}:FREQ:STOP?'.format(self.source)
        T_command = 'SOUR{}:SWEEp:TIME?'.format(self.source)
        f_start = yield self.connection.query(start_command)
        f_stop = yield self.connection.query(stop_command)
        T_ramp = yield self.connection.query(T_command)
        ramprate = (float(f_stop) - float(f_start))/float(T_ramp)
        returnValue(ramprate)
