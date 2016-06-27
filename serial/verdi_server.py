"""
### BEGIN NODE INFO
[info]
name = Verdi
version = 1.0
description = 
instancename = %LABRADNODE% Verdi

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.server import Signal
from labrad.types import Error
import labrad.types as T
from twisted.internet import reactor
from twisted.internet.defer import returnValue

#STATE_ID = 698005
#SHUTTER_ID = 698006
#POWER_ID = 698007

class VerdiServer(SerialDeviceServer):
    name = '%LABRADNODE% Verdi Server'

    def __init__(self, config_name):
        SerialDeviceServer.__init__(self)
        self.config_name = config_name
        self.load_configuration()
        self.update_values = Signal(self.update_id, 'signal: update values', '(sbbvv)')
    
    @inlineCallbacks
    def initServer(self):
        try:
            yield self.init_serial(self.serial_server_name, self.port) # can be called later if we have multiple verdis...
        except SerialConnectionError, e:
            self.ser = None
            if e.code == 0:
                print 'Could not find serial server for node: {}'.format(self.node_server)
                print 'Please start correct serial server'
            elif e.code == 1:
                print 'Error opening serial connection'
                print 'Check set up and restart serial server'
            else: 
                raise
    
    def load_configuration(self):
        config = __import__(self.config_name).VerdiConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)

    @setting(1, 'select device by name', name='s', returns='s')
    def select_device_by_name(self, c, name):
        c['name'] = name
        return str(self.verdi[name].__dict__)

    @inlineCallbacks
    def notify_listeners(self, name):
        state = yield self.state(None, name)
        shutter_state = yield self.shutter_state(None, name)
        power = yield self.power(None, name)
        current = yield self.current(None, name)
        yield self.update_values((name, state, shutter_state, power, current))

    @setting(10, 'state', name='s', state='b', returns='b')
    def state(self, c, name, state=None):
        if state == True:
            yield self.serial_server.write_line('Laser: 1')
            ans = yield self.serial_server.read_line()
        elif state == False:
            yield self.serial_server.write_line('Laser: 0')
            ans = yield self.serial_server.read_line()
        yield self.serial_server.write_line('Print Laser')
        ans = yield self.serial_server.read_line()
        #if c is not None:
        #   yield self.notify_listeners(name)
        returnValue(bool(ans))

    @setting(11, 'shutter state', name='s', state='b', returns='b')
    def shutter_state(self, c, name, state=None):
        if state == True:
            yield self.serial_server.write_line('Shutter: 1')
            ans = yield self.serial_server.read_line()
        elif state == False:
            yield self.serial_server.write_line('Shutter: 0')
            ans = yield self.serial_server.read_line()
        yield self.serial_server.write_line('Print Shutter')
        ans = yield self.serial_server.read_line()
        #if c is not None:
        #    yield self.notify_listeners(name)
        returnValue(bool(ans))

    @setting(12, 'power', name='s', power='v', returns='v')
    def power(self, c, name, power=None):
        if power:
            yield self.serial_server.write_line('Light: {}'.format(power))
            ans = yield self.serial_server.read_line()
        yield self.serial_server.write_line('Print Light')
        ans = yield self.serial_server.read_line()
        print ans
        #if c is not None:
        #    yield self.notify_listeners(name)
        returnValue(float(ans))

    @setting(13, 'current', name='s', returns='v')
    def current(self, c, name):
        yield self.serial_server.write_line('Print Current')
        ans = yield self.serial_server.read_line()
        #if c is not None:
        #    yield self.notify_listeners(name)
        returnValue(float(ans))

    @setting(14, 'request values', name='s')
    def request_values(self, c, name):
        yield self.notify_listeners(name)

if __name__ == "__main__":
    from labrad import util
    util.runServer(VerdiServer('verdi_config'))
