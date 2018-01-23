"""
### BEGIN NODE INFO
[info]
name = power_supply
version = 1.0
description = 
instancename = power_supply

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""
import sys

from labrad.server import Signal, setting
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.reactor import callLater

from server_tools.device_server import DeviceServer
from server_tools.decorators import quickSetting, autoSetting

UPDATE_ID = 692077

class PowerSupplyServer(DeviceServer):
    """ Provides basic control for current controllers """
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'power_supply'

    @quickSetting(10, 'b')
    def state(self, c, state=None):
        """ get or update state """
    
#    @setting(11, returns='v')
#    def voltage(self, c):
#        """ get output voltage """
#        device = self.get_selected_device(c)
#        voltage = yield device.get_voltage()
#        yield self.send_update(c)
#        returnValue(voltage)
    
    @quickSetting(11, 'v', do_set=False)
    def voltage(self, c):
        """ get output voltage """
    
    @setting(12, returns='v')
    def current(self, c):
        """ get output current """
        device = self.get_selected_device(c)
        current = yield device.get_current()
        yield self.send_update(c)
        returnValue(current)

    @quickSetting(13, 'v')
    def current_limit(self, c, current_limit=None):
        """ get or update current limit"""
    
    @quickSetting(14, 'v')
    def voltage_limit(self, c, voltage_limit=None):
        """ get or update voltage limit """

if __name__ == '__main__':
    from labrad import util
    util.runServer(PowerSupplyServer())
