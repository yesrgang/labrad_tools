"""
### BEGIN NODE INFO
[info]
name = dds
version = 1.0
description = 
instancename = dds

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

import json
import sys
from datetime import datetime
sys.path.append('../')

from labrad.server import Signal, setting
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue

from serial_device_server import SerialDeviceServer


UPDATE_ID = 698063

class DDSServer(SerialDeviceServer):
    name = '%LABRADNODE% DDS Server'
    update = Signal(UPDATE_ID, 'signal: update', 's')
   
    @setting(2, state='b', returns='b')
    def state(self, c, state=None):
        device = self.get_device(c)
        if state is not None:
            yield device.set_state(state)
        device.state = yield device.get_state()
        yield self.send_update(c)
        returnValue(device.state)

    @setting(3, frequency='v', returns='v')
    def frequency(self, c, frequency=None):
        device = self.get_device(c)
        if frequency is not None:
            yield device.set_frequency(frequency)
        device.frequency = yield device.get_frequency()
        yield self.send_update(c)
        returnValue(device.frequency)

    @setting(4, amplitude='v', returns='v')
    def amplitude(self, c, amplitude=None):
        device = self.get_device(c)
        if amplitude is not None:
            yield device.set_amplitude(amplitude)
        device.amplitude = yield device.get_amplitude()
        yield self.send_update(c)
        returnValue(device.amplitude)

    @setting(5)
    def send_update(self, c):
        d = self.get_device(c)
        parameters = dict([(p, getattr(d, p)) for p in d.update_parameters])
        yield self.update(json.dumps({c['name']: parameters}))

#    @setting(2, state='b')
#    def state(self, c, state=None):
#        yield self.send_update(c)
#        returnValue(True)
#
#    @setting(3, frequency='v', returns='v')
#    def frequency(self, c, frequency=None):
#        device = self.get_device(c)
#        if frequency is None:
#            frequency = device.frequency
#        else:
#            device.frequency = frequency
#        for b in get_instruction_set(device.address, device.freg, device.ftw()):
#            yield device.serial_connection.write(b)
#        ans = yield device.serial_connection.read_line()
#        yield self.send_update(c)
#        returnValue(frequency)
#    
#    @setting(4, amplitude='v', returns='v')
#    def amplitude(self, c, amplitude=None):
#        device = self.get_device(c)
#        if amplitude is None:
#            amplitude = device.amplitude
#        else:
#            device.amplitude = amplitude
#        for b in get_instruction_set(device.address, device.areg, device.atw()):
#            yield device.serial_connection.write(b)
#        ans = yield self.serial_server.read_line()
#        yield self.send_update(c)
#        returnValue(amplitude)
#
#    @setting(5)
#    def send_update(self, c):
#        d = self.get_device(c)
#        parameters = dict([(p, getattr(d, p)) for p in d.update_parameters])
#        yield self.update(json.dumps({c['name']: parameters}))

if __name__ == "__main__":
    from labrad import util
    util.runServer(DDSServer())
