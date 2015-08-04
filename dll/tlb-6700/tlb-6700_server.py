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

from labrad.server import LabradServer, setting, Signal
from twisted.internet.defer import inlineCallbacks, returnValue
import numpy as np
import ctypes as c
import json

class TLB6700Server(LabradServer):
    name = '%LABRADNODE% TLB-6700'

    def __init__(self, configuration):
        LabradServer.__init__(self)
        self.load_configuration(configuration)
        self.update = Signal(self.update_id, 'signal: update', 's')

    def load_configuration(self, configuration):
        for key, value in configuration.__dict__.items():
            setattr(self, key, value)

    def initServer(self):
        self.dll = c.WinDll(self.dll_filename)
        self.dll.newp_usb_init_system()
        buf = c.create_string_buffer(self.max_buffer_length)
        self.dll.newp_usb_get_device_info(c.byref(buf))
        print 'available devices: ', buf
        print 'selecting first device...'
        self.device_id = c.c_long(int(Buffer.value[0]))

    @inlineCallbacks
    def notify_listeners(self):
        values = {'diode current': self.current, 'piezo voltage': self.voltage}
        self.update(json.dumps(values))

    @inlineCallbacks
    def send(self, command_string):
        command = c.create_string_buffer(self.max_buffer_length)
        command.value = command_string + '\r\n'
        command_length = c.c_ulong(len(command.value))
        yield self.dll.newp_usb_send_ascii(self.device_id, c.byref(command), command_length)
        return self.get()

    @inlineCallbacks
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
            yield self.send('source:voltage:piezo {}'.format(voltage))
        self.voltage = yield self.send('source:voltage:piezo?')
        returnValue(self.voltage)

    @setting(1, 'diode current', current='v: current in mA', returns='v')
    def diode_current(self, c, current=None):
        if current is not None:
            yield self.send('source:current:diode {}'.format(current))
        self.current = yield self.send('source:current:diode?')
        returnValue(self.current)
    
if __name__ == "__main__":
    configuration = __import__('blue_master_config').ServerConfig()
    __server__ = TLB6700Server(configuration)
    from labrad import util
    util.runServer(__server__)
