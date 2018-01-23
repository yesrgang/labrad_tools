import numpy as np

from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.reactor import callLater, callFromThread

from server_tools.device_server import Device
from lib.helpers import sleep

class Ldc80xx(Device):
    """ thorlabs ldc80xx device 

    write to gpib bus with write_to_slot and query with query_with_slot
    so that multiple instances of this device don't get confused responses
    from thr PRO8
    """
    gpib_server_name = None
    gpib_address = None

    pro8_slot = None

    current_ramp_duration = 5
    current_ramp_num_points = 10
    current_range = (0.0, 0.153)
    current_stepsize = 1e-4
    default_current = 0

    update_parameters = ['state', 'current', 'power']

    @inlineCallbacks
    def initialize(self):
        yield self.connect_labrad()
        self.gpib_server = yield self.cxn[self.gpib_server_name]
        yield self.gpib_server.select_interface(self.gpib_address)
        yield self.get_parameters()
    
    @inlineCallbacks
    def get_parameters(self):
        self.state = yield self.get_state()
        self.current = yield self.get_current()
        self.power = yield self.get_power()

    @inlineCallbacks
    def write_to_slot(self, command):
        slot_command = ':SLOT {};'.format(self.pro8_slot)
        yield self.gpib_server.write(slot_command + command)
    
    @inlineCallbacks
    def query_to_slot(self, command):
        slot_command = ':SLOT {};'.format(self.pro8_slot)
        ans = yield self.gpib_server.query(slot_command + command)
        returnValue(ans)

    @inlineCallbacks
    def get_current(self):
        command = ':ILD:SET?'
        ans = yield self.query_to_slot(command)
        returnValue(float(ans[9:]))

    @inlineCallbacks
    def set_current(self, current):
        min_current = self.current_range[0]
        max_current = self.current_range[1]
        current = sorted([min_current, current, max_current])[1]
        command = ':ILD:SET {}'.format(current)
        
        yield self.write_to_slot(command)
        self.power = yield self.get_power()

    @inlineCallbacks
    def get_power(self):
        command = ':POPT:ACT?'
        ans = yield self.query_to_slot(command)
        returnValue(float(ans[10:]))
    
    @inlineCallbacks
    def set_power(self, power):
        yield None

    @inlineCallbacks
    def get_state(self):
        command = ':LASER?'
        ans = yield self.query_to_slot(command)
        if ans == ':LASER ON':
            returnValue(True)
        elif ans == ':LASER OFF':
            returnValue(False)

    @inlineCallbacks
    def set_state(self, state):
        if state:
            command = ':LASER ON'
        else:
            command = ':LASER OFF'
        
        yield self.write_to_slot(command)

    @inlineCallbacks
    def dial_current(self, stop):
        start = yield self.get_current()
        values = np.linspace(start, stop, self.current_ramp_num_points+1)[1:]
        times = np.linspace(0, self.current_ramp_duration, self.current_ramp_num_points+1)[1:]
        for t, v in zip(times, values): 
            yield self.set_current(v)
            yield sleep(float(self.current_ramp_duration) / self.current_ramp_num_points)

    @inlineCallbacks
    def warmup(self):
        yield self.set_state(True)
        callFromThread(self.dial_current, self.default_current)
        callLater(self.current_ramp_duration+.5, self.get_parameters)
        returnValue(self.current_ramp_duration+1.)

    @inlineCallbacks
    def shutdown(self):
        yield None
        callFromThread(self.dial_current, 0)
        callLater(self.current_ramp_duration+.5, self.set_state, False)
        callLater(self.current_ramp_duration+1., self.get_parameters)
        returnValue(self.current_ramp_duration+1.5)
