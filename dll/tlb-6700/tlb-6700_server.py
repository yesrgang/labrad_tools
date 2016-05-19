"""
### BEGIN NODE INFO
[info]
name = TLB-6700
version = 1.0
description = 
instancename = %LABRADNODE% TLB-6700

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

import json
import ctypes as c
import numpy as np
from time import sleep
from collections import deque

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor
from labrad.errors import Error as labradError
from labrad.server import LabradServer, setting, Signal

from pid import PID

class TLB6700Server(LabradServer):
    name = '%LABRADNODE% TLB-6700'

    def __init__(self, configuration):
        LabradServer.__init__(self)
        
        self.digital_lock_state = False
        self.digital_lock_delayed_call = None
        
        self.load_configuration(configuration)
        self.init_pid()

        self.update = Signal(self.update_id, 'signal: update', 's')


    def load_configuration(self, configuration):
        for key, value in configuration.__dict__.items():
            setattr(self, key, value)

    def init_pid(self):
        self.pid = PID(
            sampling_interval=self.pid_sampling_interval,
            prop_gain=self.pid_prop_gain,
            int_gain=self.pid_int_gain,
            out_range=self.pid_min_max,
            )

    def initServer(self):
        self.dll = c.WinDLL(self.dll_filename)
        self.dll.newp_usb_init_system()
        buf = c.create_string_buffer(self.max_buffer_length)
        self.dll.newp_usb_get_device_info(c.byref(buf))
        print 'available devices: ', buf
        print 'selecting first device...'
        self.device_id = c.c_long(int(buf.value[0]))

    @inlineCallbacks
    def notify_listeners(self):
        values = {
            "diode_current": self.current, 
            "piezo_voltage": self.voltage, 
            "laser_state": self.state, 
            "lock_state": self.digital_lock_state,
        }
        yield self.update(json.dumps(values))

    def send(self, command_string):
        command = c.create_string_buffer(self.max_buffer_length)
        command.value = command_string + '\r\n'
        command_length = c.c_ulong(len(command.value))
        self.dll.newp_usb_send_ascii(self.device_id, c.byref(command), command_length)
        return self.get()

    def get(self):
        buf_length = c.c_ulong(self.max_buffer_length)
        buf = c.create_string_buffer(buf_length.value)
        BytesRead = c.c_ulong(1)
        status = self.dll.newp_usb_get_ascii(self.device_id, c.byref(buf), buf_length, c.addressof(BytesRead))
        if not status:
            return buf.value.split('\r\n')[0]
        else:
            return None

    @setting(1, 'piezo voltage', voltage='v: voltage in percent', returns='v')
    def piezo_voltage(self, c, voltage=None):
        if voltage is not None:
            voltage = sorted([self.voltage_range[0], voltage, self.voltage_range[1]])[1]
            self.send('source:voltage:piezo {}'.format(voltage))
        self.voltage = float(self.send('source:voltage:piezo?'))
        if voltage is not None:
            yield self.notify_listeners()
        returnValue(self.voltage)

    @setting(2, 'diode current', current='v: current in mA', returns='v')
    def diode_current(self, c, current=None):
        if current is not None:
            current = sorted([self.current_range[0], current, self.current_range[1]])[1]
            self.send('source:current:diode {}'.format(current))
        self.current = float(self.send('source:current:diode?'))
        if current is not None:
            yield self.notify_listeners()
        returnValue(self.current)

    @setting(3, 'laser state', state='i', returns='i')
    def laser_state(self, c, state=None):
        if state is not None:
            start_current = yield self.diode_current(None)
            if state: # turn on laser
                self.send('output:state {}'.format(int(state)))
                stop_current = self.default_current
            else :
                stop_current = 0.
            currents = np.linspace(start_current, stop_current, self.ramp_points)
            for cur in currents:
                sleep(float(self.ramp_duration)/float(self.ramp_points))
                yield self.diode_current(None, cur)
            self.send('output:state {}'.format(int(state)))
        self.state = int(self.send('output:state?'))
        if state is not None:
            yield self.notify_listeners()
        returnValue(self.state)
	
    @setting(4, 'request values')
    def request_values(self, c):
        self.laser_state(c)
        self.piezo_voltage(c)
        self.diode_current(c)
        self.set_digital_lock_state(c)
        yield self.notify_listeners()

    @setting(5, 'get configuration')
    def get_configuration(self, c):
        values = {'diode_current_range': self.current_range, 'piezo_voltage_range': self.voltage_range}
        return json.dumps(values)

    @setting(6, 'set digital lock state', state='b', returns='b')
    def set_digital_lock_state(self, c, state=None):
        if state is not None:
            self.pid.offset = yield self.piezo_voltage(None)
            self.pid.current_offset = yield self.diode_current(None)
            self.digital_lock_state = state
            if state:
                yield self.tick_digital_lock()
            else:
                self.pid.reset()
                if hasattr(self.digital_lock_delayed_call, 'cancel'):
                    self.digital_lock_delayed_call.cancel()
        yield self.notify_listeners()
        returnValue(self.digital_lock_state)

    @setting(7, 'set digital lock gains', gains='s', returns='s')
    def set_digital_lock_gains(self, c, gains=None):
        if gains is not None:
            gains = json.loads(gains)
            if gains.has_key('p'):
                self.pid.prop_gain = gains['p']
            if gains.has_key('i'):
                self.pid.int_gain = gains['i']
            if gains.has_key('d'):
                self.pid.diff_gain = gains['d']
            self.pid.update_filter_coefficients()
        return json.dumps({'p': self.pid.prop_gain, 'i': self.pid.int_gain, 'd': self.pid.diff_gain})
    
    @inlineCallbacks
    def tick_digital_lock(self):
        print self.pid.prop_gain
        try:
            error = yield eval(self.get_dmm_str)
        except labradError:
            yield eval(self.init_dmm_str)
            error = yield eval(self.get_dmm_str)
        print error
        new_piezo_voltage = self.pid.tick(error)
        piezo_voltage = yield self.piezo_voltage(None)
        diode_current = yield self.diode_current(None)
        try:
            dpv = new_piezo_voltage - piezo_voltage
            s = dpv - round(dpv, 1)
            diode_current += s
        except:
            s = 0
        yield self.piezo_voltage(None, new_piezo_voltage)
        yield self.diode_current(None, diode_current+s)
        print piezo_voltage
        print diode_current
        if self.digital_lock_state:
            self.digital_lock_delayed_call = reactor.callLater(self.digital_lock_period, self.tick_digital_lock)
   

if __name__ == "__main__":
    configuration = __import__('blue_master_config').ServerConfig()
    __server__ = TLB6700Server(configuration)
    from labrad import util
    util.runServer(__server__)
