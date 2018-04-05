from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.reactor import callLater

from devices.verdi.verdi import Verdi
from devices.verdi.lib.helpers import seconds_til_start
from devices.verdi.lib.helpers import cancel_delayed_calls

class M2Verdi(Verdi):
    autostart = False
    serial_server_name = 'yesr20_serial'
    serial_address = 'COM19'

    power_range = (0.0, 18.0) # [W]
    default_power = 18.0 # [W]
    warmup_power_1 = 14.0 # [W]
    warmup_power_2 = 17.0 # [W]
    shutter_delay = 600 # [s]
    warmup_power_delay = 1500 # [s]
    full_power_delay = 1800 # [s]
    
    @inlineCallbacks
    def warmup(self):
        yield cancel_delayed_calls(self)
        yield self.set_power(self.warmup_power_1)
        yield self.set_state(True)
        shutter_call = callLater(self.shutter_delay, self.set_shutter_state, True)
        self.delayed_calls.append(shutter_call)
        warmup_power_call = callLater(self.warmup_power_delay, self.set_power, 
                                    self.warmup_power_2)
        self.delayed_calls.append(warmup_power_call)
        full_power_call = callLater(self.full_power_delay, self.set_power, 
                                    self.default_power)
        self.delayed_calls.append(full_power_call)

__device__ = M2Verdi
