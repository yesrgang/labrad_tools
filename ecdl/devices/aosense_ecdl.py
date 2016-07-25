import numpy as np
import time

from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.reactor import callLater
import labrad.units as U

from generic_ecdl import GenericECDL

class AOSenseECDL(GenericECDL):
    timeout = 1 * U.s
    @inlineCallbacks
    def initialize(self):
        self._lock = DeferredLock()
        for command in self.init_commands:
            yield self.connection.write_line(command)
            ans = yield self.connection.read_line()
        yield self.get_parameters()

    @inlineCallbacks 
    def get_parameters(self):
        self.state = yield self.get_state()
        self.diode_current = yield self.get_diode_current()
        self.piezo_voltage = yield self.get_piezo_voltage()

    @inlineCallbacks
    def get_current(self):
        yield self.connection.write_line('ILA')
        ans = yield self.connection.read_line()
        returnValue(float(ans))

    @inlineCallbacks
    def set_diode_current(self, current):
        min_current = self.diode_current_range[0]
        max_current = self.diode_current_range[1]
        current = sorted([min_current, current, max_current])[1]
        command = 'ILA {}'.format(current)
        
        yield self.connection.write_line(command)
        ans = yield self.connection.read_line()

    @inlineCallbacks
    def get_piezo_voltage(self):
        yield self.connection.write_line('UPZ')
        ans = yield self.connection.read_line()
        returnValue(float(ans))
    
    @inlineCallbacks
    def set_piezo_voltage(self, piezo_voltage):
        min_voltage = self.piezo_voltage_range[0]
        max_voltage = self.piezo_voltage_range[1]
        voltage = sorted([min_voltage, voltage, max_voltage])[1]
        command = 'UPZ {}'.format(voltage)
        
        yield self.connection.write_line(command)
        ans = yield self.connection.read_line()
    
    @inlineCallbacks
    def get_state(self):
        yield self.connection.write_line('LASER')
        ans = yield self.connection.read_line()
        if ans == 'ON':
            returnValue(True)
        else:
            returnValue(False)

    @inlineCallbacks
    def set_state(self, state):
        if state:
            command = 'LASER ON'
        else:
            command = 'LASER OFF'
        
        yield self.connection.write_line(command)
        ans = yield self.connection.read_line()

    @inlineCallbacks
    def dial_current(self, stop):
        self._lock.acquire()
        start = yield self.get_current()
        values = np.linspace(start, stop, 20)[1:]
        times = np.linspace(0, 5, 20)[1:]
        for t, v in zip(times, values): 
            callLater(t, self.set_current, v)
        callLater(6, self._lock.release)

    @inlineCallbacks
    def warmup(self):
        yield self.set_state(True)
        yield self.dial_current(self.default_current)
        callLater(6, self.get_parameters)

    @inlineCallbacks
    def shutdown(self):
        yield self.dial_current(0)
        callLater(5.1, self.set_state, False)
        callLater(6, self.get_parameters)
