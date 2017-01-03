import numpy as np
import time

from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.reactor import callLater

from generic_current_controller import CurrentController
from lib.helpers import sleep

T_RAMP = 5
N_RAMP = 10

class LDC80xx(CurrentController):
    @inlineCallbacks
    def initialize(self):
        self._lock = DeferredLock()
        for command in self.init_commands:
            yield self.connection.write(command)
        yield self.get_parameters()
    
    @inlineCallbacks
    def get_parameters(self):
        self.state = yield self.get_state()
        self.current = yield self.get_current()
        self.power = yield self.get_power()

    @inlineCallbacks
    def set_slot(self):
        yield self.connection.write(':SLOT {}'.format(self.slot))

    @inlineCallbacks
    def get_current(self):
        yield self._lock.acquire()
        yield self.set_slot()
        ans = yield self.connection.query(':ILD:SET?')
        yield self._lock.release()
        returnValue(float(ans[9:]))

    @inlineCallbacks
    def set_current(self, current):
        min_current = self.current_range[0]
        max_current = self.current_range[1]
        current = sorted([min_current, current, max_current])[1]
        command = ':ILD:SET {}'.format(current)
        
        yield self._lock.acquire()
        yield self.set_slot()
        yield self.connection.write(command)
        yield self._lock.release()
        self.power = yield self.get_power()

    @inlineCallbacks
    def get_power(self):
        yield self._lock.acquire()
        yield self.set_slot()
        ans = yield self.connection.query(':POPT:ACT?')
        yield self._lock.release()
        returnValue(float(ans[10:]))
    
    @inlineCallbacks
    def set_power(self, power):
        yield None

    @inlineCallbacks
    def get_state(self):
        yield self._lock.acquire()
        yield self.set_slot()
        ans = yield self.connection.query(':LASER?')
        yield self._lock.release()
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
        
        yield self._lock.acquire()
        yield self.set_slot()
        yield self.connection.write(command)
        yield self._lock.release()

    @inlineCallbacks
    def dial_current(self, stop):
        start = yield self.get_current()
        values = np.linspace(start, stop, N_RAMP+1)[1:]
        times = np.linspace(0, T_RAMP, N_RAMP+1)[1:]
        for t, v in zip(times, values): 
            self.set_current(v)
            yield sleep(float(T_RAMP)/N_RAMP)
#            callLater(t, self.set_current, v)

    @inlineCallbacks
    def warmup(self):
        yield self.set_state(True)
        yield self.dial_current(self.default_current)
        callLater(T_RAMP+.5, self.get_parameters)
        returnValue(T_RAMP+1.)

    @inlineCallbacks
    def shutdown(self):
        yield self.dial_current(0)
        callLater(T_RAMP+.5, self.set_state, False)
        callLater(T_RAMP+1., self.get_parameters)
        returnValue(T_RAMP+1.5)
