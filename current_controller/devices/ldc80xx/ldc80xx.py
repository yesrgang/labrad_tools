import json
import numpy as np
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.reactor import callLater, callInThread

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
        currents = np.linspace(start, stop, self.current_ramp_num_points+1)[1:]
        dt = float(self.current_ramp_duration) / self.current_ramp_num_points
        for current in currents: 
            yield self.set_current(current)
            yield sleep(dt)
    
    @inlineCallbacks
    def warmup(self):
        yield None
        callInThread(self.do_warmup)
#        yield self.do_warmup()
    
    @inlineCallbacks
    def do_warmup(self):
        yield self.set_state(True)
        yield self.dial_current(self.default_current)
        yield sleep(.1)
        yield self.get_parameters()
        update = {self.name: {p: getattr(self, p) for p in self.update_parameters}}
        yield self.device_server.update(json.dumps(update))

    @inlineCallbacks
    def shutdown(self):
        yield None
        callInThread(self.do_shutdown)
#        yield self.do_shutdown()

    @inlineCallbacks
    def do_shutdown(self):
        yield self.dial_current(min(self.current_range))
        yield self.set_state(False)
        yield sleep(.1)
        yield self.get_parameters()
        update = {self.name: {p: getattr(self, p) for p in self.update_parameters}}
        yield self.device_server.update(json.dumps(update))
