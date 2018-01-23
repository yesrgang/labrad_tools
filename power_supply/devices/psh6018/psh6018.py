from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import Device

class PSH6018(Device):
    serial_server_name = None
    serial_address = None
    serial_timeout = .5

    current_range = (0.0, 10.0)
    voltage_range = (0.0, 5.0)
    update_parameters = [
        'state', 
        'current', 
        'voltage', 
        'current_limit', 
        'voltage_limit',
        ]

    @inlineCallbacks
    def initialize(self):
        yield self.connect_labrad()
        self.serial_server = yield self.cxn[self.serial_server_name]
        yield self.serial_server.select_interface(self.serial_address)
        yield self.serial_server.timeout(self.serial_timeout)

        yield self.serial_server.read_lines()
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
        yield self.serial_server.write(command)
        ans = yield self.serial_server.read_line()
        current = float(ans.strip())
        self.current = current
        returnValue(current)
    
    @inlineCallbacks
    def get_current_limit(self):
        command = 'CHAN:CURR?\r\n'
        yield self.serial_server.write(command)
        ans = yield self.serial_server.read_line()
        current_limit = float(ans.strip())
        self.current_limit = current_limit
        returnValue(current_limit)

    @inlineCallbacks
    def set_current_limit(self, current):
        min_current = self.current_range[0]
        max_current = self.current_range[1]
        current = sorted([min_current, current, max_current])[1]
        command = 'CHAN:CURR {}\r\n'.format(current)
        yield self.serial_server.write(command)
        
        yield self.get_current()
        yield self.get_voltage()
    
    @inlineCallbacks
    def get_voltage(self):
        command = 'CHAN:MEAS:VOLT?\r\n'
        yield self.serial_server.write(command)
        ans = yield self.serial_server.read_line()
        voltage = float(ans.strip())
        self.voltage = voltage
        returnValue(voltage)
    
    @inlineCallbacks
    def get_voltage_limit(self):
        command = 'CHAN:VOLT?\r\n'
        yield self.serial_server.write(command)
        ans = yield self.serial_server.read_line()
        voltage_limit = float(ans.strip())
        self.voltage_limit = voltage_limit
        returnValue(voltage_limit)

    @inlineCallbacks
    def set_voltage_limit(self, voltage):
        min_voltage = self.voltage_range[0]
        max_voltage = self.voltage_range[1]
        voltage = sorted([min_voltage, voltage, max_voltage])[1]
        command = 'CHAN:VOLT {}\r\n'.format(voltage)
        yield self.serial_server.write(command)
        
        yield self.get_current()
        yield self.get_voltage()

    @inlineCallbacks
    def get_state(self):
        command = 'OUTP:STAT?\r\n'
        yield self.serial_server.write(command)
        ans = yield self.serial_server.read_line()
        state = bool(int(ans.strip()))
        self.state = state
        returnValue(state)
    
    @inlineCallbacks
    def set_state(self, state):
        if state:
            command = 'OUTP:STAT 1\r\n'
        else:
            command = 'OUTP:STAT 0\r\n'
        yield self.serial_server.write(command)
        yield self.get_state()
