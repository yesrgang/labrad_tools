import numpy as np
from twisted.internet.defer import inlineCallbacks, returnValue

from generic_power_supply import PowerSupply

class PSH6018(PowerSupply):
    timeout = 0.5

    @inlineCallbacks
    def initialize(self):
        yield self.connection.read_lines()
        yield self.get_parameters()
    
    @inlineCallbacks
    def get_parameters(self):
        yield self.get_state()
        yield self.get_current()
        yield self.get_voltage()
        yield self.get_current_limit()
        yield self.get_voltage_limit()

    @inlineCallbacks
    def get_current(self):
        command = 'CHAN:MEAS:CURR?\r\n'
        yield self.connection.write(command)
        ans = yield self.connection.read_line()
        current = float(ans.strip())
        self.current = current
        returnValue(current)
    
    @inlineCallbacks
    def get_current_limit(self):
        command = 'CHAN:CURR?\r\n'
        yield self.connection.write(command)
        ans = yield self.connection.read_line()
        current_limit = float(ans.strip())
        self.current_limit = current_limit
        returnValue(current_limit)

    @inlineCallbacks
    def set_current_limit(self, current):
        min_current = self.current_range[0]
        max_current = self.current_range[1]
        current = sorted([min_current, current, max_current])[1]
        command = 'CHAN:CURR {}\r\n'.format(current)
        yield self.connection.write(command)
        
        yield self.get_current()
        yield self.get_voltage()
    
    @inlineCallbacks
    def get_voltage(self):
        command = 'CHAN:MEAS:VOLT?\r\n'
        yield self.connection.write(command)
        ans = yield self.connection.read_line()
        voltage = float(ans.strip())
        self.voltage = voltage
        returnValue(voltage)
    
    @inlineCallbacks
    def get_voltage_limit(self):
        command = 'CHAN:VOLT?\r\n'
        yield self.connection.write(command)
        ans = yield self.connection.read_line()
        voltage_limit = float(ans.strip())
        self.voltage_limit = voltage_limit
        returnValue(voltage_limit)

    @inlineCallbacks
    def set_voltage_limit(self, voltage):
        min_voltage = self.voltage_range[0]
        max_voltage = self.voltage_range[1]
        voltage = sorted([min_voltage, voltage, max_voltage])[1]
        command = 'CHAN:VOLT {}\r\n'.format(voltage)
        yield self.connection.write(command)
        
        yield self.get_current()
        yield self.get_voltage()

    @inlineCallbacks
    def get_state(self):
        command = 'OUTP:STAT?\r\n'
        yield self.connection.write(command)
        ans = yield self.connection.read_line()
        state = bool(int(ans.strip()))
        self.state = state
        returnValue(state)
    
    @inlineCallbacks
    def set_state(self, state):
        if state:
            command = 'CHAN:VOLT 1\r\n'
        else:
            command = 'CHAN:VOLT 0\r\n'
        yield self.connection.write(command)
        
        yield self.get_current()
        yield self.get_state()
