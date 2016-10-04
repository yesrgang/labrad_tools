import numpy as np
import time

from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.reactor import callLater
import labrad.units as U

from generic_ecdl import GenericECDL

T_RAMP = 5
N_RAMP = 10

class AOSenseECDL(GenericECDL):
    timeout = 1 * U.s
    baudrate = 115200
    stopbits = 1
    bytesize = 8
    @inlineCallbacks
    def initialize(self):
        self._lock = DeferredLock()
        #for command in self.init_commands:
        #    yield self.connection.write(command)
        #    ans = yield self.connection.read_line()
        yield self.get_parameters()

    @inlineCallbacks 
    def get_parameters(self):
        self.state = yield self.get_state()
        self.diode_current = yield self.get_diode_current()
        self.piezo_voltage = yield self.get_piezo_voltage()

    @inlineCallbacks
    def get_diode_current(self):
        yield self._lock.acquire()
        yield self.connection.write('ILA\r\n')
        ans = yield self.connection.read_line()
        s = ans.split('\r\n')[0].split('=')[-1] 
        current = float(s)
        ans = yield self.connection.read_line()
        ans = yield self.connection.read_line()
        yield self._lock.release()
        returnValue(current)

    @inlineCallbacks
    def set_diode_current(self, current):
        min_current = min(self.diode_current_range)
        max_current = max(self.diode_current_range)
        current = sorted([min_current, current, max_current])[1]
        command = 'ILA {}\r\n'.format(round(current, 5))
        
        yield self._lock.acquire()
        yield self.connection.write(command)
        ans = yield self.connection.read_line()
        ans = yield self.connection.read_line()
        ans = yield self.connection.read_line()
        yield self._lock.release()

    @inlineCallbacks
    def get_piezo_voltage(self):
        yield self._lock.acquire()
        yield self.connection.write('UPZ\r\n')
        ans = yield self.connection.read_line()
        s = ans.split('\r\n')[0].split('=')[-1]
        voltage = float(s)
        ans = yield self.connection.read_line()
        ans = yield self.connection.read_line()
        yield self._lock.release()
        returnValue(voltage)
    
    @inlineCallbacks
    def set_piezo_voltage(self, voltage):
        min_voltage = self.piezo_voltage_range[0]
        max_voltage = self.piezo_voltage_range[1]
        voltage = sorted([min_voltage, voltage, max_voltage])[1]
        command = 'UPZ {}\r\n'.format(voltage)
        yield self._lock.acquire()
        yield self.connection.write(command)
        ans = yield self.connection.read_line()
        ans = yield self.connection.read_line()
        ans = yield self.connection.read_line()
        yield self._lock.release()
    
    @inlineCallbacks
    def get_state(self):
        yield self._lock.acquire()
        yield self.connection.write('LASER\r\n')
        ans = yield self.connection.read_line()
        if 'OFF' not in ans:
            ans = yield self.connection.read_line()
            ans = yield self.connection.read_line()
            state = True
        else:
            ans = yield self.connection.read_line()
            ans = yield self.connection.read_line()
            state = False
        yield self._lock.release()
        returnValue(state)

    @inlineCallbacks
    def set_state(self, state):
        if state:
            command = 'LASER ON\r\n'
        else:
            command = 'LASER OFF\r\n'
        

        yield self._lock.acquire()
        yield self.connection.write(command)
        ans = yield self.connection.read_line()
        ans = yield self.connection.read_line()
        ans = yield self.connection.read_line()
        yield self._lock.release()

    @inlineCallbacks
    def dial_current(self, stop):
        start = yield self.get_diode_current()
        values = np.linspace(start, stop, N_RAMP+1)[1:]
        times = np.linspace(0, T_RAMP, N_RAMP+1)[1:]
        for t, v in zip(times, values): 
            callLater(t, self.set_diode_current, v)

    @inlineCallbacks
    def warmup(self):
        yield self.set_state(True)
        yield self.dial_current(self.default_current)
        callLater(T_RAMP + 1.0, self.get_parameters)

    @inlineCallbacks
    def shutdown(self):
        yield self.dial_current(min(self.diode_current_range))
        callLater(T_RAMP + 0.5, self.set_state, False)
        callLater(T_RAMP + 4.0, self.get_parameters)
