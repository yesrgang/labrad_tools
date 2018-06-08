import json
import numpy as np
import time
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.reactor import callLater, callInThread

from server_tools.device_server import Device
from lib.helpers import sleep


class AOSenseECDL(Device):
    serial_server_name = None
    serial_address = None
    serial_timeout = 0.05
    serial_baudrate = 115200
    
    current_ramp_duration = 5 # [s]
    current_ramp_num_points = 10 # [s]
    default_diode_current = None # [mA]
    diode_current_range = (10.0, 200.0) # [mA]

    piezo_voltage_range = (0.0, 125.0) # [V]
    
    update_parameters = ['state', 'diode_current', 'piezo_voltage']

    @inlineCallbacks
    def initialize(self):
        yield self.connect_labrad()
        self.serial_server = yield self.cxn[self.serial_server_name]
        yield self.serial_server.select_interface(self.serial_address)
        yield self.serial_server.disconnect()
        yield self.serial_server.select_interface(self.serial_address)
        yield self.serial_server.timeout(self.serial_timeout)
        yield self.serial_server.baudrate(self.serial_baudrate)

        yield self.get_parameters()

    @inlineCallbacks 
    def get_parameters(self):
        self.state = yield self.get_state()
        print self.state
        self.diode_current = yield self.get_diode_current()
        self.piezo_voltage = yield self.get_piezo_voltage()

    @inlineCallbacks
    def get_state(self):
        yield self.serial_server.write_line('LASER')
        ans = yield self.serial_server.read_lines()
        if 'OFF' not in ans[0]:
            state = True
        else:
            state = False
        returnValue(state)

    @inlineCallbacks
    def set_state(self, state):
        if state:
            command = 'LASER ON'
        else:
            command = 'LASER OFF'

        yield self.serial_server.write_line(command)
        ans = yield self.serial_server.read_lines()

    @inlineCallbacks
    def get_diode_current(self):
        yield self.serial_server.write_line('ILA')
        ans = yield self.serial_server.read_lines()
        current = float(ans[0].split('=')[-1])
        returnValue(current)

    @inlineCallbacks
    def set_diode_current(self, current):
        min_current = min(self.diode_current_range)
        max_current = max(self.diode_current_range)
        current = sorted([min_current, current, max_current])[1]
        command = 'ILA {}'.format(round(current, 5))
        
        yield self.serial_server.write_line(command)
        ans = yield self.serial_server.read_lines()

    @inlineCallbacks
    def get_piezo_voltage(self):
        yield self.serial_server.write_line('UPZ')
        ans = yield self.serial_server.read_lines()
        voltage = float(ans[0].split('=')[-1])
        returnValue(voltage)
    
    @inlineCallbacks
    def set_piezo_voltage(self, voltage):
        min_voltage = self.piezo_voltage_range[0]
        max_voltage = self.piezo_voltage_range[1]
        voltage = sorted([min_voltage, voltage, max_voltage])[1]
        command = 'UPZ {}'.format(voltage)
        yield self.serial_server.write_line(command)
        ans = yield self.serial_server.read_lines()
    
    @inlineCallbacks
    def dial_current(self, stop):
        start = yield self.get_diode_current()
        currents = np.linspace(start, stop, self.current_ramp_num_points+1)[1:]
        dt = float(self.current_ramp_duration) / self.current_ramp_num_points
        for current in currents: 
            yield self.set_diode_current(current)
            yield sleep(dt)

    @inlineCallbacks
    def warmup(self):
        yield None
        callInThread(self.do_warmup)
    
    @inlineCallbacks
    def do_warmup(self):
        yield self.set_state(True)
        yield self.dial_current(self.default_diode_current)
        yield sleep(1)
        yield self.get_parameters()
        update = {self.name: {p: getattr(self, p) for p in self.update_parameters}}
        yield self.device_server.update(json.dumps(update))
    
    @inlineCallbacks
    def shutdown(self):
        yield None
        callInThread(self.do_shutdown)

    @inlineCallbacks
    def do_shutdown(self):
        yield self.dial_current(min(self.diode_current_range))
        yield self.set_state(False)
        yield sleep(5)
        yield self.get_parameters()
        update = {self.name: {p: getattr(self, p) for p in self.update_parameters}}
        yield self.device_server.update(json.dumps(update))
